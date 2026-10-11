import sys, numpy as np
m, n = int(sys.argv[1]), int(sys.argv[2])
A = np.random.default_rng(0).standard_normal((m, n))
R = np.linalg.qr(A, mode="r")
print(f"qr({m}x{n}) ok, R {R.shape}, |R00|={abs(R[0,0]):.4f}", flush=True)
