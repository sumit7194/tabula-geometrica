"""Hail Mary — Experiment 1 foundation: the Maxwell constrained-evolution testbed.

Maxwell's equations are the standard numerical-relativity warm-up: the divergence constraints (div E = rho,
div B = 0) are the direct analogues of Einstein's Hamiltonian/momentum constraints, and "free evolution drifts
off the constraint surface and detonates" is the baby version of the merger failure. We use the clean 2-D TM
reduction on a periodic grid -- fields (Ex, Ey, Bz), one nontrivial constraint (Gauss's law div E = rho).

Vacuum (rho = 0, J = 0) for the first cut: the constraint manifold is "divergence-free E". Ground truth is a
spectral (FFT-derivative) + RK4 integrator, which preserves div E to machine precision -- so any drift later is
the NEURAL approximation's fault, exactly what we want to study.

This file is ONLY the physics + data generator + a correctness sanity check (energy conserved, constraint
preserved). The predictor/projector/baseline nets come next. Correctness is the project's one hard rule, so the
ground truth is verified here before any learning is built on it.

Equations (c=1, vacuum):  dEx/dt =  dBz/dy ,  dEy/dt = -dBz/dx ,  dBz/dt = dEx/dy - dEy/dx
Constraint: C = div E = dEx/dx + dEy/dy  (must stay 0).
"""

import numpy as np

np.seterr(all="ignore")


class Maxwell2D:
    """2-D TM Maxwell on a periodic [0, L)^2 grid; spectral derivatives, RK4 time stepping."""

    def __init__(self, n=32, L=2 * np.pi, dt=0.01):
        self.n, self.L, self.dt = n, L, dt
        k = np.fft.fftfreq(n, d=L / n) * 2 * np.pi            # angular wavenumbers
        self.KX, self.KY = np.meshgrid(k, k, indexing="ij")
        if n % 2 == 0:                                         # zero the Nyquist mode: no Hermitian partner on an
            self.KX[n // 2, :] = 0.0                           # even grid, so i*k derivatives break reality there
            self.KY[:, n // 2] = 0.0                           # and the projection can't fully cancel div E.
        self.K2 = self.KX ** 2 + self.KY ** 2                 # consistent operators -> div(project(E)) = 0 exactly
        self.K2safe = self.K2.copy(); self.K2safe[self.K2 == 0] = 1.0  # guard k=0 AND Nyquist-induced zero modes

    # ---- spectral derivatives ----
    def ddx(self, f):
        return np.real(np.fft.ifft2(1j * self.KX * np.fft.fft2(f)))

    def ddy(self, f):
        return np.real(np.fft.ifft2(1j * self.KY * np.fft.fft2(f)))

    def divE(self, Ex, Ey):
        return self.ddx(Ex) + self.ddy(Ey)

    def project_divfree(self, Ex, Ey):
        """Leray/Helmholtz projection: remove the gradient part so div E = 0 (the constraint manifold)."""
        Fx, Fy = np.fft.fft2(Ex), np.fft.fft2(Ey)
        kdotF = (self.KX * Fx + self.KY * Fy) / self.K2safe
        Fx -= self.KX * kdotF; Fy -= self.KY * kdotF
        return np.real(np.fft.ifft2(Fx)), np.real(np.fft.ifft2(Fy))

    # ---- dynamics ----
    def rhs(self, s):
        Ex, Ey, Bz = s
        return np.stack([self.ddy(Bz), -self.ddx(Bz), self.ddy(Ex) - self.ddx(Ey)])

    def step(self, s):
        dt = self.dt
        k1 = self.rhs(s); k2 = self.rhs(s + 0.5 * dt * k1)
        k3 = self.rhs(s + 0.5 * dt * k2); k4 = self.rhs(s + dt * k3)
        return s + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)

    def rollout(self, s0, nsteps):
        out = np.empty((nsteps + 1, *s0.shape)); out[0] = s0
        s = s0
        for t in range(nsteps):
            s = self.step(s); out[t + 1] = s
        return out

    def energy(self, s):
        return 0.5 * float((s ** 2).sum())

    # ---- initial conditions ----
    def random_state(self, rng, kcut=4.0):
        """smooth random (Ex, Ey, Bz); E projected divergence-free so we START on the constraint surface."""
        def smooth():
            f = rng.standard_normal((self.n, self.n))
            F = np.fft.fft2(f) * np.exp(-self.K2 / (2 * kcut ** 2))
            g = np.real(np.fft.ifft2(F)); return g / (g.std() + 1e-9)
        Ex, Ey, Bz = smooth(), smooth(), smooth()
        Ex, Ey = self.project_divfree(Ex, Ey)
        return np.stack([Ex, Ey, Bz])


def make_dataset(n_traj=64, nsteps=40, grid=32, seed=0):
    """trajectories of (Ex,Ey,Bz) for training one-step predictors; returns (T, nsteps+1, 3, n, n)."""
    sim = Maxwell2D(n=grid); rng = np.random.default_rng(seed)
    return np.stack([sim.rollout(sim.random_state(rng), nsteps) for _ in range(n_traj)]).astype(np.float32), sim


def _sanity():
    sim = Maxwell2D(n=32, dt=0.01); rng = np.random.default_rng(1)
    s0 = sim.random_state(rng)
    print(f"initial |div E| max = {np.abs(sim.divE(s0[0], s0[1])).max():.2e}  (projected to ~0)")
    traj = sim.rollout(s0, 400)
    E0 = sim.energy(s0)
    drift = max(abs(sim.energy(traj[t]) - E0) / E0 for t in range(traj.shape[0]))
    cmax = max(np.abs(sim.divE(traj[t][0], traj[t][1])).max() for t in range(traj.shape[0]))
    print(f"energy relative drift over 400 steps = {drift:.2e}  (gate < 1e-4: spectral+RK4 conserves)")
    print(f"max |div E| over 400 steps          = {cmax:.2e}  (gate < 1e-8: true evolution preserves the constraint)")
    ok = drift < 1e-4 and cmax < 1e-8
    print(f"\nground-truth Maxwell VERIFIED (energy conserved + constraint preserved): {ok}")
    return ok


if __name__ == "__main__":
    _sanity()
