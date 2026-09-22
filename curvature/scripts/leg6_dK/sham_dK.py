"""SHAM dK: same function class, NOT the Killing solution.

Separates two readings of the void:
  sham collapses BOTH     -> the collapse is generic to the FUNCTION CLASS. dK is not special,
                             any such column absorbs deformation amplitude. Void, EXPLAINED.
  sham collapses NEITHER  -> dK IS special and the void is about the READOUT, not the object.

CONSTRUCTION. dK's numerator is a polynomial in (x, y, p_r, p_u, p_phi, p_t). Keep every monomial and
the denominator -- so the sham has the same momentum degree, the same chi^2 scaling, the same
coordinate degrees, and the same magnitude class -- but PERMUTE the numeric coefficients among the
terms with a fixed seed. That leaves it in the same function class and outside d2_rat's span for the
same structural reason, while no longer solving the Killing equation.
"""
import os, sys, numpy as np, sympy as sp, importlib.util
SP=os.environ["SP"]
spec=importlib.util.spec_from_file_location("s190","/Users/sumit/Github/SpaceTime/curvature/scripts/190_leg6_triple.py")
s190=importlib.util.module_from_spec(spec); spec.loader.exec_module(s190)
s190.NTRAJ, s190.NSTEP = 40, 3000
r_,th_,pr_,pth_,E_,L_,a_ = sp.symbols("r theta p_r p_th E L a", positive=True)
SIGMA=-1

txt=open(f"{SP}/dK_A.txt").read().split("=\n")[1].split("=== readable")[0].strip()
dK=sp.sympify(txt)
num,den = sp.fraction(sp.together(dK))
P=sp.Poly(sp.expand(num), *sorted(num.free_symbols, key=lambda s:s.name))
mons, coeffs = P.monoms(), [sp.Rational(c) for c in P.coeffs()]
rng=np.random.default_rng(20260922)
perm=rng.permutation(len(coeffs))
assert not np.all(perm==np.arange(len(coeffs))), "permutation is identity"
gens=P.gens
sham_num=sum(coeffs[perm[i]]*sp.prod([g**e for g,e in zip(gens,m)]) for i,m in enumerate(mons))
sham=sp.cancel(sham_num/den)
print(f"  dK terms {len(coeffs)};  sham is a coefficient permutation (seed 20260922)")
print(f"  identical to dK? {sp.simplify(sham-dK)==0}")

def bridge(e):
    sub={}
    for s_ in e.free_symbols:
        sub[s_]={"x":r_,"y":sp.cos(th_),"p_r":pr_,"p_u":SIGMA*pth_/sp.sin(th_),
                 "p_t":-E_,"p_phi":L_,"chi":a_}[s_.name]
    out=e.subs(sub)
    assert not ({z.name for z in out.free_symbols}-{"r","theta","p_r","p_th","E","L","a"})
    return sp.lambdify((r_,th_,pr_,pth_,E_,L_,a_), out, "numpy")
SH=bridge(sham)

def margin(obj, ep, seed, chi, add):
    s190.A_SPIN=chi; M=s190.build(obj)
    y0,E,L=s190.launch(M,ep,seed,s190.NTRAJ); y1,_,_=s190.launch(M,ep,seed+50,s190.NTRAJ)
    Ttr=s190.rk4(M,y0,E,L,ep,s190.DT,s190.NSTEP); Tte=s190.rk4(M,y1,E,L,ep,s190.DT,s190.NSTEP)
    def F(T4):
        f,_=s190.features(T4,2,True)
        if not add: return f
        R,TH,PR,PT=T4[:,0,:].T,T4[:,1,:].T,T4[:,2,:].T,T4[:,3,:].T
        return np.concatenate([f, SH(R,TH,PR,PT,E,L,chi)[...,None]],-1)
    Ftr,Fte=F(Ttr),F(Tte)
    ev,C,mu,sd=s190.conserved(Ftr)
    return float(min(s190.s99.heldout(Fte,C[:,k],mu,sd) for k in range(C.shape[1])))

EPS=[0.05,0.0158,0.005]
print(f"\n  {'arm':>16} " + " ".join(f"{e:>12}" for e in EPS) + f" {'exponent':>9}")
for label,obj in (("A + SHAM","A"),("B + SHAM","B")):
    ms=[margin(obj,e,1,0.075,True) for e in EPS]
    ex=float(np.polyfit(np.log10(EPS),np.log10(ms),1)[0])
    print(f"  {label:>16} " + " ".join(f"{m:>12.4e}" for m in ms) + f" {ex:>9.3f}", flush=True)
print(f"\n  reference: A-alone 1.947 / B-alone 1.955 ; A+dK -0.504 / B+dK -0.081")
