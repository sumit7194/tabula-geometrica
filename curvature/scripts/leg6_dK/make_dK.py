"""Produce dK = -(K1 - 56 chi^2 dH)/8 to O(chi^2), in the SOURCE repo's convention.
READ-ONLY on conjecture_machine; writes only to the scratchpad."""
import sys, os, time
sys.path.insert(0, '/Users/sumit/Github/conjecture_machine/scripts')
os.chdir('/Users/sumit/Github/conjecture_machine')
import sympy as sp
import _kt_double as KD, _kt_search as K
from _kt_carter_space import build_space, setup, x, y
from _kt_q2_candidate import combine
chi = KD.chi; Pt,Px,Py,Pph = K.MOM
t0=time.time()
ctx = setup(2, 8, 10, 0)
A_COEF={"l2tt_2":1,"l2tt_5":-32,"l2tt_6":48,"l2rr_3":4,"l2rr_4":-84,
        "l2ang_3":4,"l2ang_4":8,"l2ang_5":-48}
names,gis,roles = build_space(ctx["GI"], 6, slots=("l2tt","l2rr","l2ang"))
keep=[i for i,r_ in enumerate(roles) if r_=="slot"]
names=[names[i] for i in keep]; gis=[gis[i] for i in keep]
dgi = combine(gis,[sp.Rational(A_COEF.get(n,0)) for n in names])
dH = [KD.hamiltonian(g) for g in dgi]
_loc = {"P_t": Pt, "P_x": Px, "P_y": Py, "P_phi": Pph, "x": x, "y": y, "chi": chi}
txt = open("data/triple/K1_A.txt").read().split("K1 =")[1].split("=== chi^2")[0]
K1expr = sp.sympify(txt.strip(), locals=_loc)
print(f"  loaded [{time.time()-t0:.0f}s]", flush=True)
# only dH[0] survives into O(chi^2) once multiplied by 56 chi^2
dK = sp.cancel(sp.together(-(K1expr - 56*chi**2*dH[0])/8))
# truncate to O(chi^2)
ser = sum(sp.expand(sp.diff(dK, chi, n).subs(chi,0)/sp.factorial(n))*chi**n for n in range(3))
ser = sp.cancel(sp.together(ser))
print(f"  dK built [{time.time()-t0:.0f}s]")
print(f"  chi-levels nonzero: {[n for n in range(3) if sp.expand(sp.diff(ser,chi,n).subs(chi,0))!=0]}")
print(f"  momentum monomials present: {sorted(set(sp.Poly(sp.expand(sp.numer(ser)),Pt,Px,Py,Pph).monoms()))}")
out = os.environ['SP'] + "/dK_A.txt"
open(out,"w").write("dK_A (source convention, O(chi^2)) =\n" + sp.srepr(ser) + "\n\n=== readable ===\n" + str(ser) + "\n")
print(f"  wrote {out}  [{time.time()-t0:.0f}s]")
print(f"  ops = {sp.count_ops(ser)}")
