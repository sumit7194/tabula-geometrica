"""Hail Mary — the specialized modules (torch), shared by the DOSnet pipeline and the baseline.

- PredictorCNN: one job, learn the dynamics (state_t -> residual -> state_{t+1}).
- leray_project: one job, enforce the constraint (project E divergence-free), a FIXED differentiable layer
  (torch.fft), the "Projector" module. Same Nyquist handling as the numpy ground truth.
- div_E: the constraint functional, for monitoring + the baseline's soft penalty.

Plan A (DOSnet) = PredictorCNN then leray_project, each single-objective.
Baseline (monolith) = PredictorCNN trained with dynamics + soft div-penalty, no projection at rollout.
"""

import numpy as np
import torch
from torch import nn


def wavenumbers(n, L, device):
    k = torch.fft.fftfreq(n, d=L / n, device=device) * 2 * np.pi
    KX, KY = torch.meshgrid(k, k, indexing="ij")
    if n % 2 == 0:
        KX = KX.clone(); KY = KY.clone(); KX[n // 2, :] = 0.0; KY[:, n // 2] = 0.0
    K2 = KX ** 2 + KY ** 2
    K2safe = K2.clone(); K2safe[K2 == 0] = 1.0
    return KX, KY, K2safe


def div_E(Ex, Ey, KX, KY):
    """spectral divergence dEx/dx + dEy/dy (batched over leading dims)."""
    dx = torch.fft.ifft2(1j * KX * torch.fft.fft2(Ex)).real
    dy = torch.fft.ifft2(1j * KY * torch.fft.fft2(Ey)).real
    return dx + dy


def leray_project(Ex, Ey, KX, KY, K2safe):
    """remove the gradient part so div E = 0 -- the constraint-enforcing module (differentiable)."""
    Fx, Fy = torch.fft.fft2(Ex), torch.fft.fft2(Ey)
    kdotF = (KX * Fx + KY * Fy) / K2safe
    return torch.fft.ifft2(Fx - KX * kdotF).real, torch.fft.ifft2(Fy - KY * kdotF).real


class SpectralConv2d(nn.Module):
    """global-receptive-field layer (keep low Fourier modes, learned complex channel mix) -- for non-local maps."""

    def __init__(self, cin, cout, modes):
        super().__init__()
        self.modes = modes; scale = 1.0 / (cin * cout)
        self.w1 = nn.Parameter(scale * torch.randn(cin, cout, modes, modes, dtype=torch.cfloat))
        self.w2 = nn.Parameter(scale * torch.randn(cin, cout, modes, modes, dtype=torch.cfloat))

    def forward(self, x):
        B, C, H, W = x.shape; m = self.modes
        xf = torch.fft.rfft2(x)
        out = torch.zeros(B, self.w2.shape[1], H, W // 2 + 1, dtype=torch.cfloat, device=x.device)
        out[:, :, :m, :m] = torch.einsum("bixy,ioxy->boxy", xf[:, :, :m, :m], self.w1)
        out[:, :, -m:, :m] = torch.einsum("bixy,ioxy->boxy", xf[:, :, -m:, :m], self.w2)
        return torch.fft.irfft2(out, s=(H, W))


class SpectralConv1d(nn.Module):
    """1-D global-receptive-field layer (keep low Fourier modes, learned complex channel mix)."""

    def __init__(self, cin, cout, modes):
        super().__init__()
        self.modes = modes; scale = 1.0 / (cin * cout)
        self.w = nn.Parameter(scale * torch.randn(cin, cout, modes, dtype=torch.cfloat))

    def forward(self, x):
        B, C, N = x.shape; m = self.modes
        xf = torch.fft.rfft(x)
        out = torch.zeros(B, self.w.shape[1], xf.shape[-1], dtype=torch.cfloat, device=x.device)
        out[..., :m] = torch.einsum("bix,iox->box", xf[..., :m], self.w)
        return torch.fft.irfft(out, n=N)


class FNO1d(nn.Module):
    """1-D Fourier Neural Operator cin->cout (global operator; the Phase-F fix for high-freq/long-range)."""

    def __init__(self, cin=2, cout=2, width=64, modes=32, depth=4, residual=True):
        super().__init__()
        self.residual = residual
        self.lift = nn.Conv1d(cin, width, 1)
        self.spec = nn.ModuleList([SpectralConv1d(width, width, modes) for _ in range(depth)])
        self.point = nn.ModuleList([nn.Conv1d(width, width, 1) for _ in range(depth)])
        self.proj = nn.Sequential(nn.Conv1d(width, width, 1), nn.GELU(), nn.Conv1d(width, cout, 1))

    def forward(self, s):
        x = self.lift(s)
        for sp, p in zip(self.spec, self.point):
            x = nn.functional.gelu(sp(x) + p(x))
        out = self.proj(x)
        return s + out if self.residual else out


class FNO2d(nn.Module):
    """global operator cin->cout (the fix for non-local maps like inverse-curl / 1-over-k^2; Phase F's lesson)."""

    def __init__(self, cin, cout, width=32, modes=12, depth=4, residual=False):
        super().__init__()
        self.residual = residual
        self.lift = nn.Conv2d(cin, width, 1)
        self.spec = nn.ModuleList([SpectralConv2d(width, width, modes) for _ in range(depth)])
        self.point = nn.ModuleList([nn.Conv2d(width, width, 1) for _ in range(depth)])
        self.proj = nn.Sequential(nn.Conv2d(width, width, 1), nn.GELU(), nn.Conv2d(width, cout, 1))

    def forward(self, s):
        x = self.lift(s)
        for sp, p in zip(self.spec, self.point):
            x = nn.functional.gelu(sp(x) + p(x))
        out = self.proj(x)
        return s + out if self.residual else out


class PredictorCNN(nn.Module):
    """small periodic CNN: state (B,3,H,W) -> next state via a learned residual."""

    def __init__(self, ch=48, depth=4):
        super().__init__()
        layers = [nn.Conv2d(3, ch, 3, padding=1, padding_mode="circular"), nn.GELU()]
        for _ in range(depth - 1):
            layers += [nn.Conv2d(ch, ch, 3, padding=1, padding_mode="circular"), nn.GELU()]
        layers += [nn.Conv2d(ch, 3, 3, padding=1, padding_mode="circular")]
        self.net = nn.Sequential(*layers)

    def forward(self, s):
        return s + self.net(s)                              # residual: next ~ state + small correction


def _selfcheck():
    """torch projection must zero the divergence to machine precision, matching the numpy ground truth."""
    import sys; sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
    from maxwell import Maxwell2D
    sim = Maxwell2D(n=32); rng = np.random.default_rng(0); s = sim.random_state(rng)
    KX, KY, K2safe = wavenumbers(32, 2 * np.pi, "cpu")
    Ex = torch.tensor(s[0])[None]; Ey = torch.tensor(s[1])[None]
    # perturb off the manifold, then project
    Ex = Ex + 0.5 * torch.randn_like(Ex); Ey = Ey + 0.5 * torch.randn_like(Ey)
    before = div_E(Ex, Ey, KX, KY).abs().max().item()
    Exp, Eyp = leray_project(Ex, Ey, KX, KY, K2safe)
    after = div_E(Exp, Eyp, KX, KY).abs().max().item()
    print(f"torch projection: |div E| {before:.2e} -> {after:.2e}  (gate < 1e-5, float32 floor): {after < 1e-5}")
    return after < 1e-5


if __name__ == "__main__":
    _selfcheck()
