"""Shared machinery for the quantum corner study: lattice, correlators, regions, entropy, fits.

FROZEN PRE-REGISTRATION: notes/quantum_corner_PREREG_FROZEN.md @ e283d21 (+A1 triangle-inequality/two-sided
G1b, +A2, +A3 anti-guard absolute bounds). Nothing here may deviate from it; deviations are amendments.

GROUND STATE. For H = 1/2 sum p^2 + 1/2 q^T K q with K diagonal in Fourier space with eigenvalue omega^2(k):

    X_ij = <q_i q_j> = 1/2 (K^{-1/2})_ij      P_ij = <p_i p_j> = 1/2 (K^{1/2})_ij

Both are translation invariant, so each is one inverse FFT of 1/(2*omega) and omega/2 over the mode grid.
Restricted to a region A, the symplectic spectrum is nu = sqrt(eig(X_A P_A)) with nu >= 1/2, and

    S = sum [ (nu+1/2) ln(nu+1/2) - (nu-1/2) ln(nu-1/2) ]

THE CLIP is the floor imposed on (nu - 1/2) before the log. It is swept in G4, never fixed silently: the corner
coefficient is a small residual on a large area term, and a floor silently caps small residuals.
"""

import numpy as np

N, MASS = 160, 0.01
C_QUARTIC, B_SMEAR, C4 = 0.25, 0.15, 1.0 / 16.0
REGULATORS = ("nn", "improved", "quartic", "smeared")

_A1 = np.array([1.0, 0.0])
_A2 = np.array([0.5, np.sqrt(3.0) / 2.0])


def omega_grid(reg):
    """omega(k) on the full N x N mode grid, in lattice-index space."""
    m = np.arange(N)
    t1 = 2 * np.pi * m[:, None] / N                      # k . a1
    t2 = 2 * np.pi * m[None, :] / N                      # k . a2
    K = (4.0 / 3.0) * ((1 - np.cos(t1)) + (1 - np.cos(t2)) + (1 - np.cos(t1 - t2)))
    if reg == "nn":
        w2 = MASS ** 2 + K
    elif reg == "improved":
        w2 = MASS ** 2 + K + C4 * K ** 2
    elif reg == "quartic":
        w2 = MASS ** 2 + K + C_QUARTIC * K ** 2
    elif reg == "smeared":
        w2 = MASS ** 2 + K * np.exp(B_SMEAR * K)
    else:
        raise ValueError(reg)
    return np.sqrt(w2)


def correlators(reg):
    """(X, P) as N x N arrays indexed by lattice-coordinate DIFFERENCE (d1, d2)."""
    w = omega_grid(reg)
    X = np.real(np.fft.ifft2(1.0 / (2.0 * w)))
    P = np.real(np.fft.ifft2(w / 2.0))
    return X, P


def hexagon(p, q, r):
    """H(p,q,r) = {(n1,n2): |n1|<=p, |n2|<=q, |n1+n2|<=r}. Six exact 120-deg corners iff |p-q| < r < p+q
    (verified exhaustively, 3146 cases, Amendment 2)."""
    assert abs(p - q) < r < p + q, f"H({p},{q},{r}) is not a six-corner hexagon"
    n1, n2 = np.meshgrid(np.arange(-p, p + 1), np.arange(-q, q + 1), indexing="ij")
    msk = (np.abs(n1) <= p) & (np.abs(n2) <= q) & (np.abs(n1 + n2) <= r)
    return np.stack([n1[msk], n2[msk]], 1)


def triangle(L):
    """Equilateral triangle with three exact 60-deg corners: n1>=0, n2>=0, n1+n2<=L."""
    n1, n2 = np.meshgrid(np.arange(0, L + 1), np.arange(0, L + 1), indexing="ij")
    msk = (n1 + n2) <= L
    return np.stack([n1[msk], n2[msk]], 1)


def perimeter(sites):
    """Boundary length in lattice units: count of nearest-neighbour bonds leaving the region."""
    S = {(int(a), int(b)) for a, b in sites}
    nbrs = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, -1), (-1, 1)]
    return sum(1 for (a, b) in S for (da, db) in nbrs if (a + da, b + db) not in S)


def entropy(sites, X, P, clip=1e-12):
    """Entanglement entropy of the region, and its symplectic spectrum."""
    d1 = sites[:, 0][:, None] - sites[:, 0][None, :]
    d2 = sites[:, 1][:, None] - sites[:, 1][None, :]
    XA = X[d1 % N, d2 % N]
    PA = P[d1 % N, d2 % N]
    # nu^2 are the eigenvalues of X_A P_A. X_A is SPD, so that is SIMILAR to the symmetric PSD matrix
    # X^{1/2} P X^{1/2} -- same spectrum, but eigvalsh is faster and returns reals by construction instead of
    # by discarding an imaginary part. Amendment 4.6: a numerical change, not a model change.
    w, V = np.linalg.eigh((XA + XA.T) / 2)
    Xh = V @ np.diag(np.sqrt(np.maximum(w, 0))) @ V.T
    M = Xh @ ((PA + PA.T) / 2) @ Xh
    ev = np.linalg.eigvalsh((M + M.T) / 2)
    nu = np.sqrt(np.maximum(ev, 0.25))
    a = nu + 0.5
    b = np.maximum(nu - 0.5, clip)
    return float(np.sum(a * np.log(a) - b * np.log(b))), nu


def fit_area_log(Ls, Ps, Ss):
    """FROZEN model: S = alpha*P + beta*ln(L) + gamma.  Returns (alpha, beta, gamma, R2, cond)."""
    A = np.stack([np.asarray(Ps, float), np.log(np.asarray(Ls, float)), np.ones(len(Ls))], 1)
    coef, *_ = np.linalg.lstsq(A, np.asarray(Ss, float), rcond=None)
    pred = A @ coef
    ss_res = float(((Ss - pred) ** 2).sum())
    ss_tot = float(((Ss - np.mean(Ss)) ** 2).sum())
    r2 = 1.0 - ss_res / (ss_tot + 1e-300)
    return float(coef[0]), float(coef[1]), float(coef[2]), r2, float(np.linalg.cond(A))
