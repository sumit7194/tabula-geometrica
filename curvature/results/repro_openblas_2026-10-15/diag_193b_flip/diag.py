"""Diagnostic (The Bridge, 2026-10-15): recompute 193b t1o3 shared shell 0 Kerr cell CR/even/6/4 (seed 1) and report
the resolution rs[2]/rs[1], the floor rs[1], and SHA-256 fingerprints of the train/test trajectory arrays."""
import hashlib, json, sys, time
from importlib import import_module
from types import SimpleNamespace
code_dir, label = sys.argv[1], sys.argv[2]
sys.path.insert(0, code_dir)
m = import_module("193_ts2_screen")
import numpy as np
cfg = np.show_config(mode="dicts")["Build Dependencies"]["lapack"]["name"]
comps, p, q, sig = m.load_ts("t1o3")
mdl = m.Spacetime(m.kerr_components(-q, p), p, "Kerr").at(*m.SHELLS[0])
outer = m.outer_interval(mdl)
args = SimpleNamespace(n=60, nstep=20000, dt=0.1, stride=20)
t0 = time.time()
cell = ("CR", "even", 6, 4)
tr, te, xref, res = m.run_space(mdl, outer, args, 1, [cell])
rs = res[cell]["ratios"]
h = lambda a: hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()[:16]
out = {"label": label, "python": sys.version.split()[0], "lapack": cfg, "code_dir": code_dir,
       "outer": [float(v) for v in outer], "tr_sha": h(tr), "te_sha": h(te), "p": res[cell]["p"],
       "pruned": res[cell]["n_pruned"], "floor": float(rs[1]), "resolution": float(rs[2] / rs[1]),
       "ratios": [float(v) for v in rs[:4]], "seconds": time.time() - t0}
print(json.dumps(out))
open(f"{sys.argv[3]}/{label}.json", "w").write(json.dumps(out, indent=1))
