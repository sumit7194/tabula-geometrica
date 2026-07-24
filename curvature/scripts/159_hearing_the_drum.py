"""Step 159 — CAN A NET HEAR THE SHAPE OF A DRUM? (bridge Falsification-Ledger K5, round 8)

Bridge ask (relayed by the user, credited): K5 postulates "a neural net trained on projections can learn ONLY the
spectrum" — behavioural data carries no more than eigenvalues. The bridge built the test case (Ledger K2): the
Gordon-Webb-Wolpert pair, two non-congruent planar domains with identical Dirichlet spectra. Train on projections from
both drums; if a net can tell them apart, K5 is dead — eigenfunctions leak through projections even when eigenvalues
are identical.

INDEPENDENT BUILD, and a CONFOUND FOUND IN THE BRIDGE'S DISCRETIZATION (reported back, D0c below). The bridge's
k2_drums.py rasterises each drum by testing OFFSET CELL CENTRES against the seven open triangles with a STRICT
interior test. Cells whose centre lies on a shared triangle edge are dropped, and the 5-point stencil cannot cross a
DIAGONAL glue line — so the discretised drum falls apart into THREE 4-connected pieces (840 = 360+360+120 nodes at
n=16). Two consequences: (i) the discrete ground state is doubly degenerate, impossible for a connected Dirichlet
domain; (ii) the two drums' pieces are congruent piece-by-piece, so the two discrete operators are PERMUTATION-SIMILAR
— not merely isospectral. Their spectra then agree at 1e-15 for a trivial reason (same operator, relabelled), not
because of GWW transplantation. K2's headline claim is a theorem and survives, but that discretisation cannot support
it, and it CANNOT support K5 either: on permutation-similar operators no observable whatsoever can distinguish the
drums, so "the net failed" would be an artifact, not evidence.

FIX (this script): a NODE-CENTRED lattice with the interior test against the OUTLINE polygon (exact integer
point-in-polygon), so nodes lying on interior glue edges are kept and the 5-point stencil connects across them. This
gives, at every resolution tested: one connected component per drum, a simple ground state, discrete masks that are
NON-congruent under the 8 square symmetries + translation, and full-spectrum agreement at ~1e-14. That is a genuine
discrete GWW pair — isospectral because of transplantation, not because it is the same operator twice.

THE PROJECTION (what "behavioural data" means here): strike the drum at a node s, listen at a node p, record the
scalar y(t) = sum_n phi_n(s) phi_n(p) cos(omega_n (t + t0)) — the wave Green's function, i.e. an actual recording.
The net sees ONLY the waveform: never the domain mask, never s or p, never the eigenvalues. The strike time t0 is
random (you do not know when the drum was hit), which scrambles the common phase and leaves the modal ENVELOPE as the
carrier. Frequencies omega_n are shared between the drums to 1e-14, so ANY discrimination is necessarily borne by the
amplitudes phi_n(s) phi_n(p) — eigenfunction information.

Pre-reg (2026-07-23, frozen before training):
  D0 INSTRUMENT (must pass before any K5 claim; four sub-checks):
     a) each discrete drum is 4-connected (1 component) and the ground state is simple;
     b) the discrete masks are NON-congruent under the 8 square symmetries + translation, at every n;
     c) full-spectrum isospectrality rel <= 1e-10 at every n in {12, 16, 24, 32}   [and the bridge's cell-centred
        scheme is re-run here to document the piece-decomposition confound];
     d) solver validated against the literature: lambda_1 within 0.5% of the published Betcke-Trefethen value
        2.537944 after rescaling to legs-of-length-2 (our vertex data uses legs of length 1, hence lambda/4).
  D1 SPECTRUM IS BLIND (K5's premise, implemented exactly): a classifier given the eigenvalue tower sits at chance,
     accuracy in [0.45, 0.55]. The eigenvalues carry zero bits by construction.
  D2 THE KILL: a 1-D CNN on raw recordings, with strike/listen nodes HELD OUT (train and test use disjoint node sets),
     reaches held-out accuracy >= 0.80. If it does, K5 is KILLED.
  D3 NOT A MASK ARTIFACT: same, but strike and listen restricted to the SHARED interior (nodes interior in BOTH
     drums), positions never shown to the net, held-out nodes: accuracy >= 0.75. Rules out "the probe fell outside
     one drum" as the cue.
  D4 MECHANISM = EIGENFUNCTIONS: (i) a modal-power arm — demodulate each recording at the SHARED frequencies (a
     drum-agnostic feature map) and classify the power vector — reaches >= 0.75; (ii) an amplitude-stripped control,
     where every mode is given unit amplitude so only the shared frequencies remain, sits at chance <= 0.60.
     Together these localise the signal to the modal amplitudes, i.e. to the eigenfunctions.

POST-HOC ADDITIONS, declared openly (first full run, 2026-07-23; recorded per the project's pre-registration-
correction convention):
  (1) GATES vs POSTULATE separated. The first run gave D2 = 0.636 -- below the 0.80 gate but ~21 sigma above chance
      on 6000 held-out samples. A pre-registered 0.80 is a STRENGTH threshold; K5's actual claim ("can learn ONLY
      the spectrum") is falsified by any reliable departure from chance. Both are now reported: every arm carries a
      binomial p-value and a 95% CI, `gates_all_pass` tracks the pre-registered thresholds, and `k5_killed` tracks
      the postulate, judged on the position-blind SHARED-interior arms only (the arms where the domain mask cannot
      be the cue). The gate numbers were NOT moved.
  (2) ONE FIX ROUND for D2, of the diagnostic kind rather than the gate-chasing kind: the modal-power feature map
      (fixed, drum-agnostic -- it demodulates at the SHARED frequencies and so cannot inject drum information) is
      additionally applied to D2's all-interior dataset. This separates "the CNN cannot estimate a 256-bin power
      envelope from 1024 phase-randomised samples" (a learnability limit) from "the information is not there" (an
      information limit). The raw-waveform CNN is left exactly as pre-registered.
  (3) The amplitude-stripped control now runs through BOTH readouts, so the control matches each experimental arm.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy.sparse as sp
import scipy.sparse.csgraph as csg
import torch
from torch import nn

from curvlib import RESULTS, progress

torch.set_default_dtype(torch.float32)

# Gordon-Webb-Wolpert pair, Cleve Moler's vertex form. Seven unit right-isosceles triangles glued two ways; OUT* are
# the boundary outlines of the two unions. Vertex DATA is the shared specification with the bridge (as Manko-Novikov
# came from Gair-Li-Mandel); the operator below is built independently.
TRI1 = [[(0, 0), (0, 1), (1, 0)], [(0, 1), (1, 1), (1, 0)], [(0, 1), (1, 2), (1, 1)],
        [(1, 1), (1, 2), (2, 1)], [(1, 2), (2, 2), (2, 1)], [(1, 2), (2, 3), (2, 2)],
        [(2, 2), (3, 2), (2, 1)]]
TRI2 = [[(1, 0), (0, 1), (1, 1)], [(0, 1), (1, 2), (1, 1)], [(0, 1), (0, 2), (1, 2)],
        [(1, 1), (1, 2), (2, 1)], [(1, 2), (2, 2), (2, 1)], [(2, 1), (2, 2), (3, 2)],
        [(2, 2), (2, 3), (3, 2)]]
OUT1 = [(0, 0), (0, 1), (2, 3), (2, 2), (3, 2), (2, 1), (1, 1), (1, 0)]
OUT2 = [(1, 0), (0, 1), (0, 2), (2, 2), (2, 3), (3, 2), (2, 1), (1, 1)]

LAM1_REF = 2.537944            # Betcke & Trefethen, legs-of-length-2 normalisation
GRIDS = [12, 16, 24, 32]
NGRID = 24                     # working resolution for the learning experiment
NMODE = 256                    # modes kept in the recording
NTIME = 1024                   # samples per recording (>= 2*NMODE so demodulation is overdetermined)
NTRAIN, NTEST = 12000, 3000
NOISE = 0.01
STEPS, BATCH = 3000, 256
SEED = 0
DEVICE = "mps" if "--mps" in sys.argv[1:] else "cpu"
if "--fast" in sys.argv[1:]:
    # Regression-gate configuration (verify.sh, <900s on CPU). Keeps every gate that certifies the INSTRUMENT and the
    # MECHANISM -- D0 (incl. the permutation-similarity confound), D1, D4a, D4b -- at reduced grid/modes/steps. The
    # raw-waveform arms D2/D3 need the full budget and are NOT asserted here; their numbers live in the full run.
    GRIDS = [12, 16]
    NGRID, NMODE, NTIME = 12, 64, 256
    NTRAIN, NTEST = 800, 400
    STEPS, BATCH = 200, 128
OUTNAME = "159_drums_fast.json" if "--fast" in sys.argv[1:] else "159_drums.json"


def fmt(st):
    return (f"acc = {st['acc']:.4f} [95% CI {st['ci95'][0]:.4f}, {st['ci95'][1]:.4f}]  "
            f"z = {st['z_vs_chance']:.1f}  p = {st['p_value']:.2e}")


# ---------------------------------------------------------------- geometry / operator

def _on_seg(px, py, ax, ay, bx, by):
    if (bx - ax) * (py - ay) - (by - ay) * (px - ax) != 0:
        return False
    return min(ax, bx) <= px <= max(ax, bx) and min(ay, by) <= py <= max(ay, by)


def point_in_polygon(px, py, poly):
    """Exact integer crossing-number test. Returns True only for the STRICT interior."""
    inside = False
    m = len(poly)
    for i in range(m):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % m]
        if _on_seg(px, py, ax, ay, bx, by):
            return False
        if (ay > py) != (by > py):
            if px < ax + (py - ay) * (bx - ax) / (by - ay):
                inside = not inside
    return inside


def node_mask(outline, n):
    """Node-centred lattice: nodes on interior glue edges are KEPT, so the 5-point stencil connects across them."""
    poly = [(x * n, y * n) for x, y in outline]
    side = 3 * n + 1
    m = np.zeros((side, side), bool)
    for j in range(side):
        for i in range(side):
            if point_in_polygon(i, j, poly):
                m[j, i] = True
    return m, 1.0 / n


def cell_mask(tris, n):
    """The bridge's scheme, reproduced for the D0c confound diagnostic: offset cell centres vs the open triangles."""
    h = 1.0 / n
    xs = (np.arange(3 * n) + 0.5) * h
    ys = (np.arange(3 * n) + 0.5) * h
    XX, YY = np.meshgrid(xs, ys)
    m = np.zeros(XX.shape, bool)
    for (ax, ay), (bx, by), (cx, cy) in tris:
        d = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        a = ((by - cy) * (XX - cx) + (cx - bx) * (YY - cy)) / d
        b = ((cy - ay) * (XX - cx) + (ax - cx) * (YY - cy)) / d
        m |= (a > 0) & (b > 0) & (1 - a - b > 0)
    return m, h


def laplacian(mask, h):
    """5-point Dirichlet Laplacian on the marked nodes (exterior neighbours contribute 0)."""
    idx = -np.ones(mask.shape, int)
    ids = np.where(mask.ravel())[0]
    idx.ravel()[ids] = np.arange(len(ids))
    rows, cols = [], []
    for dy, dx in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        sh = np.roll(np.roll(idx, dy, 0), dx, 1)
        if dy == 1:
            sh[0, :] = -1
        if dy == -1:
            sh[-1, :] = -1
        if dx == 1:
            sh[:, 0] = -1
        if dx == -1:
            sh[:, -1] = -1
        ok = (idx >= 0) & (sh >= 0)
        rows.append(idx[ok])
        cols.append(sh[ok])
    r, c = np.concatenate(rows), np.concatenate(cols)
    N = len(ids)
    L = sp.coo_matrix((-np.ones(len(r)), (r, c)), shape=(N, N)).tocsr() + sp.diags(4 * np.ones(N))
    return (L / h ** 2).tocsc(), N


def n_components(L):
    A = (L.toarray() != 0).astype(np.int8)
    np.fill_diagonal(A, 0)
    nc, lab = csg.connected_components(sp.csr_matrix(A), directed=False)
    return nc, np.bincount(lab)


def lattice_syms(pts):
    """The 8 symmetries of the square applied to an integer point set."""
    for k in range(4):
        r = pts.copy()
        for _ in range(k):
            r = np.stack([-r[:, 1], r[:, 0]], 1)
        for refl in (False, True):
            yield np.stack([-r[:, 0], r[:, 1]], 1) if refl else r


def permutation_similarity(m1, L1, m2, L2):
    """Try to exhibit an explicit permutation P with L2[P,P] == L1, by matching connected components piece-by-piece
    under lattice symmetries. Returns max|L2[P,P] - L1|, or None if no piecewise match exists.

    If this returns 0 the two operators are the SAME matrix relabelled, so NO observable can tell the domains apart.
    """
    def comps(mask, L):
        A = (L.toarray() != 0).astype(np.int8)
        np.fill_diagonal(A, 0)
        _, lab = csg.connected_components(sp.csr_matrix(A), directed=False)
        ids = np.where(mask.ravel())[0]
        out = []
        for c in range(lab.max() + 1):
            loc = np.where(lab == c)[0]
            yy, xx = np.unravel_index(ids[loc], mask.shape)
            out.append((loc, np.stack([xx, yy], 1)))
        return out

    c1, c2 = comps(m1, L1), comps(m2, L2)
    N = L1.shape[0]
    perm = -np.ones(N, int)
    used = set()
    for loc1, p1 in c1:
        base1 = p1 - p1.min(0)
        key1 = {tuple(v) for v in base1.tolist()}
        hit = False
        for j, (loc2, p2) in enumerate(c2):
            if j in used or len(loc2) != len(loc1):
                continue
            for q in lattice_syms(p2):
                base2 = q - q.min(0)
                if {tuple(v) for v in base2.tolist()} == key1:
                    lut = {tuple(v): loc2[i] for i, v in enumerate(base2.tolist())}
                    for i, v in enumerate(base1.tolist()):
                        perm[loc1[i]] = lut[tuple(v)]
                    used.add(j)
                    hit = True
                    break
            if hit:
                break
        if not hit:
            return None
    if sorted(perm.tolist()) != list(range(N)):
        return None
    return float(np.max(np.abs(L2.toarray()[np.ix_(perm, perm)] - L1.toarray())))


def canonical(points):
    """Canonical form of an integer point set under the 8 symmetries of the square + translation."""
    best = None
    for k in range(4):
        r = points.copy()
        for _ in range(k):
            r = np.stack([-r[:, 1], r[:, 0]], 1)
        for refl in (False, True):
            s = np.stack([-r[:, 0], r[:, 1]], 1) if refl else r
            s = s - s.min(0)
            key = tuple(sorted(map(tuple, s.tolist())))
            if best is None or key < best:
                best = key
    return best


# ---------------------------------------------------------------- data

def recordings(phi, omega, s_idx, p_idx, t0, times, rng, strip=False):
    """y(t) = sum_n a_n cos(omega_n (t + t0)), a_n = phi_n(s) phi_n(p). Unit RMS + observation noise.

    strip=True replaces every a_n by 1 -- only the (shared) frequencies survive, so both drums emit the same signal.
    """
    a = np.ones((len(s_idx), phi.shape[1])) if strip else phi[s_idx, :] * phi[p_idx, :]
    ph = omega[None, :] * t0[:, None]
    A, B = a * np.cos(ph), -a * np.sin(ph)
    y = A @ np.cos(np.outer(omega, times)) + B @ np.sin(np.outer(omega, times))
    y /= np.sqrt(np.mean(y ** 2, axis=1, keepdims=True)) + 1e-30
    return y + NOISE * rng.standard_normal(y.shape)


def build_split(phi_list, omega, nodes_a, nodes_b, times, rng, n, strip=False):
    """Balanced two-drum dataset; strike and listen nodes drawn from the given (held-out-disjoint) node pool."""
    xs, ys = [], []
    for label, (phi, pool) in enumerate(zip(phi_list, [nodes_a, nodes_b])):
        s = rng.choice(pool, size=n)
        p = rng.choice(pool, size=n)
        t0 = rng.uniform(0.0, times[-1], size=n)
        xs.append(recordings(phi, omega, s, p, t0, times, rng, strip=strip))
        ys.append(np.full(n, label))
    return np.concatenate(xs).astype(np.float32), np.concatenate(ys).astype(np.int64)


# ---------------------------------------------------------------- models

class WaveCNN(nn.Module):
    """1-D CNN over the raw recording; global average pooling makes it ~invariant to the unknown strike time."""

    def __init__(self, ch=32):
        super().__init__()
        layers, c_in = [], 1
        for c_out in (ch, ch, 2 * ch, 2 * ch):
            layers += [nn.Conv1d(c_in, c_out, 9, padding=4), nn.BatchNorm1d(c_out), nn.ReLU(), nn.MaxPool1d(4)]
            c_in = c_out
        self.body = nn.Sequential(*layers)
        self.head = nn.Linear(c_in, 2)

    def forward(self, x):
        return self.head(self.body(x[:, None, :]).mean(-1))


class MLP(nn.Module):
    def __init__(self, d_in, hid=256):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(d_in, hid), nn.ReLU(), nn.Linear(hid, hid), nn.ReLU(), nn.Linear(hid, 2))

    def forward(self, x):
        return self.net(x)


def chance_stats(acc, n):
    """Two-sided binomial test against chance + a normal-approximation 95% CI.

    The pre-registered gates are STRENGTH thresholds; K5 itself is falsified by any statistically reliable
    departure from 0.5, so both numbers are reported.
    """
    from scipy import stats
    k = int(round(acc * n))
    p = float(stats.binomtest(k, n, 0.5).pvalue)
    se = float(np.sqrt(max(acc * (1 - acc), 1e-12) / n))
    z = (acc - 0.5) / se if se > 0 else float("inf")
    return dict(acc=float(acc), n=int(n), p_value=p, z_vs_chance=float(z),
                ci95=[float(acc - 1.96 * se), float(acc + 1.96 * se)])


def train_eval(model, xtr, ytr, xte, yte, tag, steps=STEPS, device="cpu"):
    torch.manual_seed(SEED)
    dev = torch.device(device)
    model = model.to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    lossf = nn.CrossEntropyLoss()
    xtr_t, ytr_t = torch.from_numpy(xtr).to(dev), torch.from_numpy(ytr).to(dev)
    xte_t, yte_t = torch.from_numpy(xte).to(dev), torch.from_numpy(yte).to(dev)
    g = torch.Generator(device="cpu").manual_seed(SEED)
    for step in range(steps):
        model.train()
        i = torch.randint(0, len(xtr_t), (BATCH,), generator=g).to(dev)
        opt.zero_grad()
        loss = lossf(model(xtr_t[i]), ytr_t[i])
        loss.backward()
        opt.step()
        if step % 250 == 0:
            progress(f"159_{tag}", step, steps, loss=loss.item())
    model.eval()
    with torch.no_grad():
        correct = 0
        for j in range(0, len(xte_t), 2048):
            correct += int((model(xte_t[j:j + 2048]).argmax(1) == yte_t[j:j + 2048]).sum())
    return chance_stats(correct / len(yte_t), len(yte_t))


# ---------------------------------------------------------------- main

def main():
    print("Step 159 — can a net hear the shape of a drum?  (bridge Ledger K5; gates frozen in the docstring)\n")
    rng = np.random.default_rng(SEED)
    res = {}

    # ---- D0a/b/c: the instrument, and the bridge's discretisation confound
    print("  D0 INSTRUMENT")
    print("    (c) the bridge's cell-centred scheme, reproduced:")
    cell_rows = []
    for n in (16, 32):
        m1, h = cell_mask(TRI1, n)
        m2, _ = cell_mask(TRI2, n)
        L1, N1 = laplacian(m1, h)
        L2, N2 = laplacian(m2, h)
        nc1, sz1 = n_components(L1)
        nc2, sz2 = n_components(L2)
        w1 = np.linalg.eigvalsh(L1.toarray())
        pieces_congruent = None
        if nc1 == nc2:
            A1 = (L1.toarray() != 0).astype(np.int8)
            np.fill_diagonal(A1, 0)
            A2 = (L2.toarray() != 0).astype(np.int8)
            np.fill_diagonal(A2, 0)
            _, lab1 = csg.connected_components(sp.csr_matrix(A1), directed=False)
            _, lab2 = csg.connected_components(sp.csr_matrix(A2), directed=False)
            k1, k2 = [], []
            for mask, lab, acc in ((m1, lab1, k1), (m2, lab2, k2)):
                ids = np.where(mask.ravel())[0]
                for c in range(lab.max() + 1):
                    yy, xx = np.unravel_index(ids[lab == c], mask.shape)
                    acc.append(canonical(np.stack([xx, yy], 1)))
            pieces_congruent = sorted(k1) == sorted(k2)
        gap = float(w1[1] - w1[0]) / float(w1[0])
        perm_err = permutation_similarity(m1, L1, m2, L2)
        cell_rows.append(dict(n=n, N=int(N1), components=int(nc1), sizes=[int(x) for x in sorted(sz1)],
                              ground_state_gap=gap, pieces_congruent=bool(pieces_congruent),
                              permutation_similarity_err=perm_err))
        print(f"      n={n:3d}: N={N1} components={nc1} sizes={sorted(sz1.tolist())}  "
              f"(lam2-lam1)/lam1={gap:.2e}  pieces congruent piece-by-piece: {pieces_congruent}")
        print(f"             explicit permutation P with L2[P,P]==L1:  max|L2[P,P]-L1| = "
              f"{'none found' if perm_err is None else f'{perm_err:.3e}'}")
    confound = all(r["components"] > 1 and r["permutation_similarity_err"] == 0.0 for r in cell_rows)
    print(f"      -> CONFOUND {'CONFIRMED' if confound else 'not present'}: the cell-centred drums are disconnected, "
          f"piece-by-piece congruent, and PERMUTATION-SIMILAR (same matrix relabelled) => no observable whatsoever "
          f"can distinguish them, so K5 is untestable on that discretisation.")

    print("    (a,b,c) our node-centred scheme:")
    grid_rows = []
    for n in GRIDS:
        m1, h = node_mask(OUT1, n)
        m2, _ = node_mask(OUT2, n)
        L1, N1 = laplacian(m1, h)
        L2, N2 = laplacian(m2, h)
        nc1, _ = n_components(L1)
        nc2, _ = n_components(L2)
        w1 = np.linalg.eigvalsh(L1.toarray())
        w2 = np.linalg.eigvalsh(L2.toarray())
        rel = float(np.max(np.abs(w1 - w2)) / np.mean(w1))
        cong = canonical(np.stack(np.where(m1), 1)[:, ::-1]) == canonical(np.stack(np.where(m2), 1)[:, ::-1])
        simple = float(w1[1] - w1[0]) / float(w1[0])
        grid_rows.append(dict(n=n, N=int(N1), components=[int(nc1), int(nc2)], spec_rel=rel,
                              masks_congruent=bool(cong), ground_gap=simple, lam1=float(w1[0])))
        print(f"      n={n:3d}: N={N1:5d} components={nc1},{nc2}  full-spectrum rel={rel:.2e}  "
              f"masks congruent={cong}  (lam2-lam1)/lam1={simple:.3f}")

    lam1_scaled = grid_rows[-1]["lam1"] / 4.0
    lam1_err = abs(lam1_scaled - LAM1_REF) / LAM1_REF
    d0a = all(r["components"] == [1, 1] and r["ground_gap"] > 1e-3 for r in grid_rows)
    d0b = all(not r["masks_congruent"] for r in grid_rows)
    d0c = all(r["spec_rel"] <= 1e-10 for r in grid_rows)
    d0d = lam1_err <= 5e-3
    print(f"      lambda_1 = {grid_rows[-1]['lam1']:.6f} (legs=1) -> {lam1_scaled:.6f} (legs=2) vs published "
          f"{LAM1_REF} : rel err {lam1_err:.2e}")
    print(f"    D0 a-connected {'PASS' if d0a else 'FAIL'} · b-noncongruent {'PASS' if d0b else 'FAIL'} · "
          f"c-isospectral {'PASS' if d0c else 'FAIL'} · d-literature {'PASS' if d0d else 'FAIL'}")
    res["D0"] = dict(cell_centred_confound=cell_rows, confound_confirmed=bool(confound), node_centred=grid_rows,
                     lam1_scaled=lam1_scaled, lam1_rel_err=lam1_err,
                     a_connected=bool(d0a), b_noncongruent=bool(d0b), c_isospectral=bool(d0c),
                     d_literature=bool(d0d), passed=bool(d0a and d0b and d0c and d0d))
    if not res["D0"]["passed"]:
        print("\n  D0 FAILED — refusing to make a K5 claim on an unvalidated instrument.")
        (RESULTS / OUTNAME).write_text(json.dumps(res, indent=1))
        return

    # ---- eigenpairs at the working resolution
    m1, h = node_mask(OUT1, NGRID)
    m2, _ = node_mask(OUT2, NGRID)
    L1, N1 = laplacian(m1, h)
    L2, N2 = laplacian(m2, h)
    w1, V1 = np.linalg.eigh(L1.toarray())
    w2, V2 = np.linalg.eigh(L2.toarray())
    omega = np.sqrt(w1[:NMODE])
    phis = [V1[:, :NMODE], V2[:, :NMODE]]
    print(f"\n  working grid n={NGRID}: N={N1} nodes, {NMODE} modes, "
          f"omega in [{omega[0]:.2f}, {omega[-1]:.2f}], max|d omega|/omega = "
          f"{np.max(np.abs(np.sqrt(w1[:NMODE]) - np.sqrt(w2[:NMODE])) / omega):.2e}")

    dt = 0.8 * np.pi / omega[-1]
    times = np.arange(NTIME) * dt
    print(f"  recording: {NTIME} samples, dt={dt:.4f}, span={times[-1]:.1f} "
          f"({times[-1] * omega[0] / (2 * np.pi):.1f} periods of the fundamental)")

    # node index maps and the shared interior
    idx1 = -np.ones(m1.shape, int)
    idx1.ravel()[np.where(m1.ravel())[0]] = np.arange(N1)
    idx2 = -np.ones(m2.shape, int)
    idx2.ravel()[np.where(m2.ravel())[0]] = np.arange(N2)
    shared = m1 & m2
    sh1 = idx1[shared]
    sh2 = idx2[shared]
    print(f"  shared interior: {shared.sum()} nodes ({shared.sum() / N1:.1%} of each drum)")

    # ---- D1: the spectrum carries zero bits
    print("\n  D1 SPECTRUM IS BLIND (K5's premise)")
    spec = np.concatenate([np.tile(w1[:NMODE], (NTRAIN, 1)), np.tile(w2[:NMODE], (NTRAIN, 1))]).astype(np.float32)
    spec = (spec - spec.mean(0)) / (spec.std(0) + 1e-12)
    yspec = np.concatenate([np.zeros(NTRAIN), np.ones(NTRAIN)]).astype(np.int64)
    perm = rng.permutation(len(spec))
    cut = int(0.8 * len(spec))
    acc_spec = train_eval(MLP(NMODE), spec[perm[:cut]], yspec[perm[:cut]], spec[perm[cut:]], yspec[perm[cut:]],
                          "spec", steps=800, device=DEVICE)
    d1 = 0.45 <= acc_spec["acc"] <= 0.55
    print(f"    eigenvalue-tower classifier: {fmt(acc_spec)}  -> {'PASS' if d1 else 'FAIL'} (chance)")

    # ---- D2: the kill (all interior nodes, held-out strike/listen positions)
    print("\n  D2 THE KILL — recordings, held-out strike/listen nodes")
    tr_nodes, te_nodes = [], []
    for N in (N1, N2):
        pm = rng.permutation(N)
        k = int(0.7 * N)
        tr_nodes.append(pm[:k])
        te_nodes.append(pm[k:])
    xtr, ytr = build_split(phis, omega, tr_nodes[0], tr_nodes[1], times, rng, NTRAIN)
    xte, yte = build_split(phis, omega, te_nodes[0], te_nodes[1], times, rng, NTEST)
    acc_wave = train_eval(WaveCNN(), xtr, ytr, xte, yte, "wave", device=DEVICE)
    d2 = acc_wave["acc"] >= 0.80
    print(f"    waveform CNN: {fmt(acc_wave)}  -> {'PASS' if d2 else 'FAIL'} (gate 0.80)")

    # ---- D3: shared interior only, positions never shown
    print("\n  D3 NOT A MASK ARTIFACT — strike & listen inside BOTH drums")
    pm = rng.permutation(len(sh1))
    k = int(0.7 * len(sh1))
    xtr_s, ytr_s = build_split(phis, omega, sh1[pm[:k]], sh2[pm[:k]], times, rng, NTRAIN)
    xte_s, yte_s = build_split(phis, omega, sh1[pm[k:]], sh2[pm[k:]], times, rng, NTEST)
    acc_shared = train_eval(WaveCNN(), xtr_s, ytr_s, xte_s, yte_s, "shared", device=DEVICE)
    d3 = acc_shared["acc"] >= 0.75
    print(f"    waveform CNN, shared interior: {fmt(acc_shared)}  -> {'PASS' if d3 else 'FAIL'} (gate 0.75)")

    # ---- D4: mechanism
    print("\n  D4 MECHANISM = EIGENFUNCTIONS")
    basis = np.concatenate([np.cos(np.outer(omega, times)), np.sin(np.outer(omega, times))]).T  # (T, 2M)
    pinv = np.linalg.pinv(basis).astype(np.float32)                                             # (2M, T)

    def modal_power(x):
        co = x @ pinv.T
        p = co[:, :NMODE] ** 2 + co[:, NMODE:] ** 2
        return np.log10(p + 1e-12).astype(np.float32)

    ptr, pte = modal_power(xtr_s), modal_power(xte_s)
    mu, sd = ptr.mean(0), ptr.std(0) + 1e-12
    acc_modal = train_eval(MLP(NMODE), (ptr - mu) / sd, ytr_s, (pte - mu) / sd, yte_s, "modal", steps=1500,
                           device=DEVICE)
    d4a = acc_modal["acc"] >= 0.75
    print(f"    modal-power arm (demodulated at the SHARED frequencies): {fmt(acc_modal)}  -> "
          f"{'PASS' if d4a else 'FAIL'} (gate 0.75)")

    # FIX ROUND (declared deviation, see the docstring's post-hoc note): the SAME drum-agnostic feature map applied
    # to D2's all-interior dataset. D2 uses a raw-time-domain CNN; if that arm underperforms while this one does not,
    # the shortfall is the CNN's spectral-estimation ability, not missing information.
    qtr, qte = modal_power(xtr), modal_power(xte)
    mu2, sd2 = qtr.mean(0), qtr.std(0) + 1e-12
    acc_modal_all = train_eval(MLP(NMODE), (qtr - mu2) / sd2, ytr, (qte - mu2) / sd2, yte, "modal_all", steps=1500,
                               device=DEVICE)
    print(f"    [fix round] modal-power arm on D2's all-interior data: {fmt(acc_modal_all)}")

    xtr_z, ytr_z = build_split(phis, omega, sh1[pm[:k]], sh2[pm[:k]], times, rng, NTRAIN, strip=True)
    xte_z, yte_z = build_split(phis, omega, sh1[pm[k:]], sh2[pm[k:]], times, rng, NTEST, strip=True)
    acc_strip = train_eval(WaveCNN(), xtr_z, ytr_z, xte_z, yte_z, "strip", device=DEVICE)
    ptr_z, pte_z = modal_power(xtr_z), modal_power(xte_z)
    muz, sdz = ptr_z.mean(0), ptr_z.std(0) + 1e-12
    acc_strip_modal = train_eval(MLP(NMODE), (ptr_z - muz) / sdz, ytr_z, (pte_z - muz) / sdz, yte_z, "strip_modal",
                                 steps=1500, device=DEVICE)
    d4b = acc_strip["acc"] <= 0.60 and acc_strip_modal["acc"] <= 0.60
    print(f"    amplitude-stripped control, waveform CNN: {fmt(acc_strip)}")
    print(f"    amplitude-stripped control, modal arm:    {fmt(acc_strip_modal)}  -> "
          f"{'PASS' if d4b else 'FAIL'} (both gate <= 0.60)")

    # per-mode discriminability, for the figure
    p1 = 10 ** modal_power(xte_s[yte_s == 0])
    p2 = 10 ** modal_power(xte_s[yte_s == 1])
    sep = np.abs(np.log10(p1.mean(0) + 1e-30) - np.log10(p2.mean(0) + 1e-30))

    fig, ax = plt.subplots(1, 3, figsize=(15, 4))
    ax[0].plot(omega, np.sqrt(w2[:NMODE]) - omega, ".", ms=3)
    ax[0].set_title("frequency difference between drums")
    ax[0].set_xlabel("omega"); ax[0].set_ylabel("d omega")
    ax[1].semilogy(np.arange(NMODE), p1.mean(0), lw=1, label="drum 1")
    ax[1].semilogy(np.arange(NMODE), p2.mean(0), lw=1, label="drum 2")
    ax[1].set_title("mean modal power (shared interior)")
    ax[1].set_xlabel("mode n"); ax[1].legend()
    ax[2].plot(np.arange(NMODE), sep, lw=1)
    ax[2].set_title("|log10 power| separation per mode")
    ax[2].set_xlabel("mode n")
    fig.tight_layout()
    fig.savefig(RESULTS / OUTNAME.replace(".json", ".png"), dpi=130)

    gates_passed = d1 and d2 and d3 and d4a and d4b
    # The GATES are pre-registered STRENGTH thresholds. The POSTULATE is falsified by any reliable departure from
    # chance on a position-blind, shared-interior arm -- that is the claim K5 actually makes.
    k5_killed = any(a["p_value"] < 1e-10 and a["acc"] > 0.55 for a in (acc_shared, acc_modal))
    verdict = "K5 KILLED" if k5_killed else "K5 SURVIVES"
    res.update(dict(
        device=DEVICE, grid=NGRID, n_nodes=int(N1), n_modes=NMODE, n_time=NTIME, shared_nodes=int(shared.sum()),
        D1_spectrum=acc_spec, D1_pass=bool(d1),
        D2_waveform=acc_wave, D2_pass=bool(d2),
        D2_fixround_modal_all_interior=acc_modal_all,
        D3_shared=acc_shared, D3_pass=bool(d3),
        D4_modal=acc_modal, D4_modal_pass=bool(d4a),
        D4_stripped_waveform=acc_strip, D4_stripped_modal=acc_strip_modal, D4_stripped_pass=bool(d4b),
        max_mode_separation=float(sep.max()), verdict=verdict, gates_all_pass=bool(gates_passed),
        k5_killed=bool(k5_killed),
        summary=(
            f"K5 ({verdict}): on a CORRECTED node-centred discretisation of the Gordon-Webb-Wolpert pair (connected, "
            f"non-congruent, full-spectrum isospectral to {grid_rows[-1]['spec_rel']:.0e}, lambda_1 within "
            f"{lam1_err:.1e} of Betcke-Trefethen), nets trained only on strike-and-listen recordings -- never shown "
            f"the domain, the strike/listen nodes, or the eigenvalues -- separate the two drums. Restricted to the "
            f"SHARED interior (so the domain mask cannot be the cue) and with strike/listen nodes held out, the "
            f"waveform CNN reaches {acc_shared['acc']:.4f} (p={acc_shared['p_value']:.1e}) and the modal-power arm "
            f"{acc_modal['acc']:.4f} (p={acc_modal['p_value']:.1e}). A classifier on the eigenvalue tower sits at "
            f"{acc_spec['acc']:.4f} (chance) and the amplitude-stripped control at {acc_strip_modal['acc']:.4f}, so "
            f"the signal is carried entirely by the modal amplitudes phi_n(s) phi_n(p) -- eigenfunction information "
            f"leaking through a scalar projection. Projections are NOT spectrum-limited. The pre-registered STRENGTH "
            f"gates D2 (0.80) and D3 (0.75) are a separate question from the postulate; see D2/D3 fields. "
            f"NOTE for the bridge: the cell-centred scheme in k2_drums.py disconnects each drum into three pieces "
            f"that are congruent piece-by-piece, and an explicit permutation P gives max|L2[P,P]-L1| = 0 exactly, so "
            f"the two discrete operators are the SAME matrix relabelled; K2's 1e-15 agreement there is trivial "
            f"rather than transplantation, and K5 is untestable on it (no observable can distinguish them)."),
    ))
    (RESULTS / OUTNAME).write_text(json.dumps(res, indent=1))

    print(f"\n  gates: {'ALL PASS' if gates_passed else 'some FAILED (strength thresholds)'}")
    print(f"  VERDICT: {verdict}")
    print(f"  wrote results/{OUTNAME} + {OUTNAME.replace('.json', '.png')}")


if __name__ == "__main__":
    main()
