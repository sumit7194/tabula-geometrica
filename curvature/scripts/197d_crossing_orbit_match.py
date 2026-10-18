import importlib.util, sys, numpy as np
spec = importlib.util.spec_from_file_location("k20", "scripts/197_k20_mn_screen.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
lib = m._lib(); pp = m.point_params("P0"); dom = m.build_domain(pp); tol = m.load_level("C0_inner")["tol"]
pairs = {"1->1": ((2.847765, 0.474744), (2.725602, 0.113769)), "3->3": ((2.845564, -0.478662), (2.725602, -0.113769)),
         "2->4": ((3.615937, 0.002647), (3.621321, 6e-06)), "3->4": ((3.505235, 0.059693), (3.609747, 0.005682)),
         "4->1": ((3.505236, -0.059692), (3.609747, -0.005682))}
for k, (t, v) in pairs.items():
    best = (np.hypot(t[0]-v[0], t[1]-v[1]), 0)
    for f, s in ((m._forward_map, 1), (m._inverse_map, -1)):
        q = np.array(t)
        for n in range(1, 13):
            r = f(lib, dom, pp, 0.95, 3.0, q[0], q[1], tol)
            if r is None: break
            q = r[0]; dd = np.hypot(q[0]-v[0], q[1]-v[1])
            if dd < best[0]: best = (dd, s*n)
    print(k, "min dist to V13 crossing %.2e at P^%d" % best)
