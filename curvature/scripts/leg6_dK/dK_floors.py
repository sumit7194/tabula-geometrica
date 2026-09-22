"""PER-ARM eps=0 FLOORS. The floor is basis-dependent: A+dK has one extra function,
so dividing its margins by A-alone's floor borrows a denominator from a different experiment
and can manufacture a collapse. Four arms, four floors.

ORIGINAL HEADER:
THE dK SPAN TEST. Add dK as one column to the library; A's exponent must collapse, B's must not.

Three arms, and the third is what makes the other two readable:
  A augmented   -> exponent must COLLAPSE from ~1.95 toward 0   (dK completes K_A(eps))
  B augmented   -> exponent must NOT move                       (nothing exact to complete)
  A unaugmented -> must REPRODUCE the banked ~1.947             (else the harness changed and
                                                                 nothing here is comparable)
Run at two chi: truncation error in dK scales as chi^2, the span question does not.
"""
import sys, os, json, numpy as np, sympy as sp, importlib.util
SP = os.environ["SP"]
spec = importlib.util.spec_from_file_location("s190","/Users/sumit/Github/SpaceTime/curvature/scripts/190_leg6_triple.py")
s190 = importlib.util.module_from_spec(spec); spec.loader.exec_module(s190)
# MATCH THE REFERENCE EXACTLY. The banked 1.947 exponent and the 8.2238e-15 floor were both produced
# with these values set explicitly; 190's own defaults are 90/9000 and `FAST` is read from argv, not
# the environment, so an env FAST=1 silently does nothing. Comparing margins computed at 90/9000
# against a floor computed at 40/3000 is the borrowed-denominator error in run parameters.
s190.NTRAJ, s190.NSTEP = 40, 3000
sys.path.insert(0,"/Users/sumit/Github/SpaceTime/curvature/scripts")
import importlib
s99 = importlib.import_module("99_emit_or_certify") if os.path.exists(
    "/Users/sumit/Github/SpaceTime/curvature/scripts/99_emit_or_certify.py") else s190.s99

r_, th_, pr_, pth_, E_, L_, a_ = sp.symbols("r theta p_r p_th E L a", positive=True)
SIGMA = -1     # u = cos th  =>  p_u = -p_th/sin th ; predicted, and confirmed by the control

def _load_dK():
    txt = open(f"{SP}/dK_A.txt").read().split("=\n")[1].split("=== readable")[0].strip()
    e = sp.sympify(txt); sub = {}
    for s_ in e.free_symbols:
        n = s_.name
        sub[s_] = {"x": r_, "y": sp.cos(th_), "p_r": pr_, "p_u": SIGMA*pth_/sp.sin(th_),
                   "p_t": -E_, "p_phi": L_, "chi": a_}[n]          # KeyError = incomplete bridge
    out = e.subs(sub)
    assert not ({z.name for z in out.free_symbols} - {"r","theta","p_r","p_th","E","L","a"})
    return sp.lambdify((r_,th_,pr_,pth_,E_,L_,a_), out, "numpy")
DK = _load_dK()

def aug_features(T4, deg, rational, E, L, chi, add):
    F, names = s190.features(T4, deg, rational)
    if not add:
        return F, names
    R, TH, PR, PT = T4[:,0,:].T, T4[:,1,:].T, T4[:,2,:].T, T4[:,3,:].T
    col = DK(R, TH, PR, PT, E, L, chi)
    return np.concatenate([F, col[...,None]], -1), names + ["dK"]

def margin(obj, ep, seed, chi, add):
    s190.A_SPIN = chi
    M = s190.build(obj)
    y0, E, L = s190.launch(M, ep, seed, s190.NTRAJ)
    y0te,_,_  = s190.launch(M, ep, seed+50, s190.NTRAJ)
    Ttr = s190.rk4(M, y0, E, L, ep, s190.DT, s190.NSTEP)
    Tte = s190.rk4(M, y0te, E, L, ep, s190.DT, s190.NSTEP)
    Ftr,_ = aug_features(Ttr, 2, True, E, L, chi, add)
    Fte,_ = aug_features(Tte, 2, True, E, L, chi, add)
    ev, C, mu, sd = s190.conserved(Ftr)
    return float(min(s190.s99.heldout(Fte, C[:,k], mu, sd) for k in range(C.shape[1])))

EPS = [0.0]
out = {}
print(f"  {'chi':>7} {'arm':>16} " + " ".join(f"{e:>12}" for e in EPS) + f" {'exponent':>9}")
for chi in (0.075,):
    for label, obj, add in (("A unaugmented","A",False), ("A + dK","A",True), ("B unaugmented","B",False), ("B + dK","B",True)):
        try:
            ms = [margin(obj, e, 1, chi, add) for e in EPS]
            expo = float("nan")
            out[f"chi{chi}_{label}"] = {"margins": ms, "exponent": expo}
            print(f"  {chi:>7} {label:>16} " + " ".join(f"{m:>12.4e}" for m in ms) + f" {expo:>9.3f}", flush=True)
        except Exception as ex:
            print(f"  {chi:>7} {label:>16}  ERROR {type(ex).__name__}: {str(ex)[:60]}", flush=True)
json.dump(out, open(f"{SP}/dK_floors.json","w"), indent=2)
print(f"  wrote {SP}/dK_floors.json")
