"""A14 (post-hoc, labelled; pre-registered in notes/k20_build_log.md @13ef69f): reproduce V13's confirmed edges in
tabula's kernel. For an edge i->j with crossing q: iterate P forward to UPO j and P^-1 back to UPO i, s = max of the
two closest normalised approaches; domain status along the way. Threshold fixed by POS/NEG controls from tabula's own
A13 crossings before any V13 point is read."""
import hashlib
import importlib.util
import json
import re
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("k20", HERE / "197_k20_mn_screen.py")
k20 = importlib.util.module_from_spec(spec); spec.loader.exec_module(k20)
RESULTS = HERE.parent / "results"
V13 = Path("/Users/sumit/Github/TheBridge/falsification/V13_mn_chaotic_sea/results")
SEALS = {"v13_a10_F5R.json": "3e098030b6296ca99d13678a7d2fc9074d967e8a631b17d956bf71e6e575e589",
         "v13_a10_C0.json": "a4602110e1fe3e2d7de7762f59e71097d2757e17bd8b76c80b21f3e490287710"}
CFG = {"F5R": {"point": "F5R", "M": 89.0, "v13": "v13_a10_F5R.json", "upo": "v13_upo_F5R_19o20_3.json",
               "txt": "v13_s7_F5R_edges_bridge.txt"},
       "C0": {"point": "P0", "M": 1.0, "v13": "v13_a10_C0.json", "upo": "v13_upo_C0_19o20_3.json",
              "txt": "v13_s7_C0_edges_bridge.txt"}}
E, LZ, NMAX = 0.95, 3.0, 30


def setup(tag):
    a13 = json.load(open(RESULTS / "197_a13.json"))[tag][0]
    pp = k20.point_params(CFG[tag]["point"])
    xa, xb = a13["component"]
    box = k20.refined_box(pp, E, LZ, xa, xb)
    tol = k20.load_level("C0_inner")["tol"] if tag == "C0" else None
    if tol is None:
        d = json.load(open(RESULTS / "197_analysis_F5R.json"))
        tol = 1e-12
        for ext in d.get("extension_A10", []):
            if abs(ext["E"] - E) < 1e-12 and abs(ext["Lz"] - LZ) < 1e-12 and abs(ext["x"][0] - xa) < 0.05:
                tol = ext["tol"]
    return a13, pp, k20.build_domain(pp), box, tol


def probe(lib, dom, pp, tol, box, q, src_pts, dst_pts):
    nrm = lambda a, b: float(np.min(np.hypot((a[0] - b[:, 0]) / (box["xb"] - box["xa"]), (a[1] - b[:, 1]) / (2 * box["pm"]))))
    out = {}
    for side, f, tgt in (("f", k20._forward_map, dst_pts), ("b", k20._inverse_map, src_pts)):
        z, best, nbest, left9, base_fail, track = np.array(q, float), np.inf, 0, [], None, []
        for n in range(1, NMAX + 1):
            r = f(lib, dom, pp, E, LZ, z[0], z[1], tol)
            if r is None:
                base_fail = n; break
            z, orb = r
            left9.append(bool(orb[3] >= 0))
            d = nrm(z, tgt)
            if d < best:
                best, nbest = d, n
        out[side] = {"d": best, "n": nbest, "left_B9_by_argmin": any(left9[:nbest]),
                     "base_fail_at": base_fail, "base_fail_by_argmin": base_fail is not None and base_fail <= nbest}
    out["s"] = max(out["f"]["d"], out["b"]["d"])
    return out


def classify(r, thr):
    if r["s"] >= thr:
        return "NOT-REPRODUCED"
    if r["f"]["base_fail_by_argmin"] or r["b"]["base_fail_by_argmin"]:
        return "REAL-OUT"
    if r["f"]["left_B9_by_argmin"] or r["b"]["left_B9_by_argmin"]:
        return "REAL-BAND"
    return "REAL-IN-D"


def v13_upos(tag):
    """V13 UPO index -> full-precision section points (tabula units), indices from the bridge txt listing."""
    full = json.load(open(V13 / CFG[tag]["upo"]))["upos"]
    M, out = CFG[tag]["M"], {}
    for line in open(V13 / CFG[tag]["txt"]):
        m = re.match(r"UPO(\d+) p(\d): (.*)", line)
        if not m:
            continue
        pts = [tuple(map(float, t.strip("() ").split(","))) for t in m[3].split(";")]
        cand = [u for u in full if u["period"] == int(m[2])
                and all(min(np.hypot(p[0] - a, p[1] - b) for a, b in u["points"]) < 1e-5 for p in pts)]
        assert len(cand) >= 1, (tag, m[1])
        out[int(m[1])] = np.array([[a, b / M] for a, b in cand[0]["points"]])
    return out


def main():
    for f, h in SEALS.items():
        assert hashlib.sha256((V13 / f).read_bytes()).hexdigest() == h, f
    lib = k20._lib()
    res = {"label": "POST-HOC A14 (pre-registered 13ef69f); registered verdicts unchanged", "nmax": NMAX}
    ctx, pos, neg, pos_cap = {}, [], [], []
    rng = np.random.default_rng(0)
    for tag in CFG:                                   # controls first: tabula's own crossings
        a13, pp, dom, box, tol = setup(tag)
        ctx[tag] = (pp, dom, box, tol)
        ups = [np.array([u]) for u in a13["upos"]]   # tier-1 section point (one per UPO; other points via orbit below)
        full = {}
        for i, u in enumerate(a13["upos"]):          # all section points of each tabula UPO from its own orbit
            pts, z = [u], np.array(u)
            for _ in range(5):
                r = k20._forward_map(lib, dom, pp, E, LZ, z[0], z[1], tol)
                if r is None:
                    break
                z = r[0]
                if np.hypot(z[0] - u[0], z[1] - u[1]) < 1e-6:
                    break
                pts.append(list(z))
            full[i] = np.array(pts)
        for e in a13["edges"]:
            if not e["edge_confirmed"]:
                continue
            q = np.array(e["crossing"])
            rp = probe(lib, dom, pp, tol, box, q, full[e["from"]], full[e["to"]])
            pos.append(rp["s"]); pos_cap.append(rp["f"]["n"] == NMAX or rp["b"]["n"] == NMAX)
            th = rng.uniform(0, 2 * np.pi)
            qn = q + 1e-2 * np.array([np.cos(th) * (box["xb"] - box["xa"]), np.sin(th) * 2 * box["pm"]])
            if k20.launch(pp, E, LZ, qn[0], qn[1]) is None:
                continue
            neg.append(probe(lib, dom, pp, tol, box, qn, full[e["from"]], full[e["to"]])["s"])
        print(f"{tag}: controls pos {len(pos)} neg {len(neg)}", flush=True)
    p95, p5 = float(np.percentile(pos, 95)), float(np.percentile(neg, 5))
    cap_frac = float(np.mean(pos_cap))
    valid = p95 < p5 / 10 and cap_frac <= 0.25
    thr = float(np.sqrt(p95 * p5))
    res["controls"] = {"pos": pos, "neg": neg, "p95_pos": p95, "p5_neg": p5, "thr": thr, "valid": bool(valid), "pos_cap_frac": cap_frac}
    print(f"controls: p95(POS) {p95:.3e}  p5(NEG) {p5:.3e}  thr {thr:.3e}  POS at cap {cap_frac:.2f}  VALID {valid}", flush=True)
    # tabula-confirmed pairs in V13 indices (for the 'both' vs 'V13-only' split)
    tab_pairs = {"F5R": {(2, 2), (2, 4), (3, 3), (4, 2), (4, 4), (4, 8), (6, 3), (6, 6), (8, 2)},
                 "C0": {(1, 1), (3, 3), (2, 4), (3, 4), (4, 1)}}
    for tag in CFG:
        pp, dom, box, tol = ctx[tag]
        vu = v13_upos(tag)
        rows = []
        for e in json.load(open(V13 / CFG[tag]["v13"]))["edges"]:
            if not e["CONFIRMED_MS"]:
                continue
            q = np.array([e["ms_13"]["point"][0], e["ms_13"]["point"][1] / CFG[tag]["M"]])
            r = probe(lib, dom, pp, tol, box, q, vu[e["src"]], vu[e["dst"]])
            r.update({"src": e["src"], "dst": e["dst"], "both": (e["src"], e["dst"]) in tab_pairs[tag],
                      "class": classify(r, thr) if valid else "ABSTAIN"})
            rows.append(r)
            print(f"{tag} {e['src']}->{e['dst']} {'BOTH' if r['both'] else 'V13 '} s {r['s']:.2e} "
                  f"(f {r['f']['d']:.1e}@{r['f']['n']}, b {r['b']['d']:.1e}@{r['b']['n']}) {r['class']}", flush=True)
        res[tag] = rows
        for grp in (True, False):
            c = {}
            for r in rows:
                if r["both"] == grp:
                    c[r["class"]] = c.get(r["class"], 0) + 1
            print(f"{tag} {'both' if grp else 'V13-only'}: {c}", flush=True)
    fn = RESULTS / "197_a14.json"
    fn.write_text(json.dumps(res, indent=1, default=k20._jsonable))
    print(f"SEALED {fn.name} sha256 {hashlib.sha256(fn.read_bytes()).hexdigest()}", flush=True)


if __name__ == "__main__":
    main()
