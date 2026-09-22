"""CONTROL for the dK bridge. Does Q + eps*dK drift at O(eps^2) along A's flow?
Two-sided: K1 must reproduce its banked 1.001 in the same harness, and BOTH sigma must be able to fail."""
import sys, os, numpy as np, sympy as sp
sys.path.insert(0, '/Users/sumit/Github/SpaceTime/curvature/scripts')
os.environ.setdefault("FAST","1")
import importlib.util
spec = importlib.util.spec_from_file_location("s190","/Users/sumit/Github/SpaceTime/curvature/scripts/190_leg6_triple.py")
s190 = importlib.util.module_from_spec(spec); spec.loader.exec_module(s190)

SP = os.environ["SP"]
r_, th_, pr_, pth_, E_, L_, a_ = sp.symbols("r theta p_r p_th E L a", positive=True)
Pt,Px,Py,Pph,xs,ys,chis = sp.symbols("P_t P_x P_y P_phi x y chi")

def load(path, key):
    txt = open(path).read().split(key)[1].split("=== readable")[0].strip()
    return sp.sympify(txt)

dK_src = load(f"{SP}/dK_A.txt", "=\n")
# K1 in the SAME pipeline, as the known-fail
sys.path.insert(0,'/Users/sumit/Github/conjecture_machine/scripts')
_cwd=os.getcwd(); os.chdir('/Users/sumit/Github/conjecture_machine')
import _kt_double as KD, _kt_search as K
_loc={"P_t":K.MOM[0],"P_x":K.MOM[1],"P_y":K.MOM[2],"P_phi":K.MOM[3],
      "x":sp.Symbol("x"),"y":sp.Symbol("y"),"chi":KD.chi}
K1_src = sp.sympify(open("data/triple/K1_A.txt").read().split("K1 =")[1].split("=== chi^2")[0].strip(), locals=_loc)
os.chdir(_cwd)

MAPPED = {"x", "y", "p_r", "p_u", "p_t", "p_phi", "chi"}


def bridge(expr, sigma, chi_val):
    """x->r, y=u=cos th, p_r->p_r, p_u->sigma*p_th/sin th, p_t->-E, p_phi->L, chi->a.

    ASSERTS COMPLETENESS. The first version matched "P_x"/"P_y"; the source names are p_r/p_u, so the
    dict matched NO momentum and `subs` silently did nothing -- subs never errors on a key that is not
    there. Worse, `p_r` exists in both namespaces with different assumptions, so lambdify would have
    bound that one correctly BY NAME while the rest became undefined globals: a bridge that is right
    about one coordinate and silently absent on three."""
    sub = {}
    for s_ in expr.free_symbols:
        n = s_.name
        if   n == "x":     sub[s_] = r_
        elif n == "y":     sub[s_] = sp.cos(th_)
        elif n == "p_r":   sub[s_] = pr_
        elif n == "p_u":   sub[s_] = sigma * pth_ / sp.sin(th_)
        elif n == "p_t":   sub[s_] = -E_
        elif n == "p_phi": sub[s_] = L_
        elif n == "chi":   sub[s_] = a_
        else:
            raise AssertionError(f"UNMAPPED source symbol {n!r} -- bridge is incomplete")
    out = expr.subs(sub)
    leftover = {z.name for z in out.free_symbols} - {"r", "theta", "p_r", "p_th", "E", "L", "a"}
    assert not leftover, f"after subs, unmapped symbols remain: {leftover}"
    return sp.lambdify((r_, th_, pr_, pth_, E_, L_, a_), out, "numpy")


def carter(R,T,PR,PT,E,L,a):
    return PT**2 + np.cos(T)**2*(a**2*(1-E**2) + L**2/np.sin(T)**2)

def drift(fn, ep, chi_val, seed=0, n=24):
    s190.A_SPIN = chi_val
    M = s190.build("A")
    y0,E,L = s190.launch(M, ep, seed, n)
    T4 = s190.rk4(M, y0, E, L, ep, 2.0e-3, 4000)
    R,TH,PR,PT = T4[:,0,:],T4[:,1,:],T4[:,2,:],T4[:,3,:]
    Q = carter(R,TH,PR,PT,E,L,chi_val)
    tot = Q if fn is None else Q + ep*fn(R,TH,PR,PT,E,L,chi_val)
    scale = np.abs(Q).mean()
    d = (np.nanmax(tot,0)-np.nanmin(tot,0))/scale
    return float(np.nanmedian(d))

import time; _t0=time.time()
print("  Does Q + eps*dK drift at O(eps^2)?  exponent from eps 0.05 -> 0.005 (one decade)")
print("  banked known-fail: K1 gave 1.001 (bare Q 1.002) -- no improvement\n")
print(f"  {'chi':>7} {'object':>10} {'d(.05)':>12} {'d(.005)':>12} {'exponent':>9}")
for chi_val in (0.6, 0.075):
    for label, fn in (("bare Q", None), ("K1", bridge(K1_src,+1,chi_val)),
                      ("dK s=+1", bridge(dK_src,+1,chi_val)), ("dK s=-1", bridge(dK_src,-1,chi_val))):
        try:
            d1 = drift(fn, 0.05, chi_val); d2 = drift(fn, 0.005, chi_val)
            expo = np.log10(d1/d2)
            print(f"  {chi_val:>7} {label:>10} {d1:>12.4e} {d2:>12.4e} {expo:>9.3f}", flush=True)
        except Exception as ex:
            print(f"  {chi_val:>7} {label:>10}  ERROR {type(ex).__name__}: {str(ex)[:60]}", flush=True)
