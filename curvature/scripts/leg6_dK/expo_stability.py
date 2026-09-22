"""Is the EXPONENT stable against the perturbation that moved the floor 2.8x?

The pair check could not test this: A and B are the same metric only at eps=0, where there is no
exponent. So construct A' = sp.expand(A) -- mathematically identical to A at EVERY eps, a DIFFERENT
expression tree, hence different lambdify rounding. That is the same ULP mechanism, available at
eps > 0 where an exponent exists.

Plus seed variation, a much LARGER perturbation: if the exponent survives that it survives a ulp.
"""
import os, sys, numpy as np, sympy as sp, importlib.util
spec=importlib.util.spec_from_file_location("s190","/Users/sumit/Github/SpaceTime/curvature/scripts/190_leg6_triple.py")
s190=importlib.util.module_from_spec(spec); spec.loader.exec_module(s190)
s190.NTRAJ, s190.NSTEP = 40, 3000
s190.A_SPIN = 0.075
_A_orig = s190.OBJECTS["A"]
s190.OBJECTS["Aexp"] = lambda: tuple(sp.expand(c) for c in _A_orig())

EPS=[0.05,0.0158,0.005]
def margin(obj, ep, seed):
    M=s190.build(obj)
    y0,E,L=s190.launch(M,ep,seed,s190.NTRAJ); y1,_,_=s190.launch(M,ep,seed+50,s190.NTRAJ)
    Ttr=s190.rk4(M,y0,E,L,ep,s190.DT,s190.NSTEP); Tte=s190.rk4(M,y1,E,L,ep,s190.DT,s190.NSTEP)
    Ftr,_=s190.features(Ttr,2,True); Fte,_=s190.features(Tte,2,True)
    ev,C,mu,sd=s190.conserved(Ftr)
    return float(min(s190.s99.heldout(Fte,C[:,k],mu,sd) for k in range(C.shape[1])))

# confirm A and Aexp really are a ULP-level difference, not a real one
MA, MX = s190.build("A"), s190.build("Aexp")
y0,E,L = s190.launch(MA,0.05,1,s190.NTRAJ)
R,T,PR,PT=y0
diffs={k: float(np.max(np.abs(MA[k](R,T,PR,PT,E,L,0.075,0.05)-MX[k](R,T,PR,PT,E,L,0.075,0.05)))) for k in ("H","irr","ith","dHdr","dHdth")}
print("  A vs A' (expanded tree) at eps=0.05, max abs component diff:")
for k,v in diffs.items(): print(f"    {k:<6} {v:.3e}")
print()
print(f"  {'arm':>16} {'seed':>5} " + " ".join(f"{e:>12}" for e in EPS) + f" {'exponent':>9}")
rows={}
for obj,seed in (("A",1),("A",2),("A",3),("Aexp",1)):
    ms=[margin(obj,e,seed) for e in EPS]
    ex=float(np.polyfit(np.log10(EPS),np.log10(ms),1)[0])
    rows[(obj,seed)]=(ms,ex)
    print(f"  {obj:>16} {seed:>5} " + " ".join(f"{m:>12.4e}" for m in ms) + f" {ex:>9.3f}", flush=True)
ex=[v[1] for v in rows.values()]; fl=[v[0][0] for v in rows.values()]
print(f"\n  EXPONENT  spread {max(ex)-min(ex):.4f}  (max/min ratio {max(ex)/min(ex):.4f})")
print(f"  MARGIN@.05 ratio max/min {max(fl)/min(fl):.4f}   <- the absolute number, for contrast")
print(f"\n  floor scatter measured earlier: 2.79x")
print(f"  exponent stable if its spread is small where the absolute number scatters")
