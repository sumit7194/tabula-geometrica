/* A8 second integrable null: separable double well, H = p1^2/2 + q1^4/4 - q1^2/2 + p2^2/2 + q2^2/2 (total energy h).
   Same out[] layout as mn_eval.c. z = (q1, q2, p1, p2) in the kernel's (x, y, px, py) slots, so the section
   y = 0, p_y > 0 is q2 = 0, p2 > 0. out[23] = H - h - 1/2, so the kernel's drift |H + 1/2| / (1/2) is |dH| / (1/2).
   par = {unused, unused, unused, h, unused}. */
void mn_eval(const double *par, const double *z, double *out) {
    const double h = par[3];
    const double q1 = z[0], q2 = z[1], p1 = z[2], p2 = z[3];
    for (int i = 0; i < 26; i++) out[i] = 0.0;
    out[0] = p1; out[1] = p2; out[2] = -(q1 * q1 * q1 - q1); out[3] = -q2;
    /* Jacobian rows: d(rhs_i)/d(q1, q2, p1, p2) */
    out[4 + 0 * 4 + 2] = 1.0;
    out[4 + 1 * 4 + 3] = 1.0;
    out[4 + 2 * 4 + 0] = -(3.0 * q1 * q1 - 1.0);
    out[4 + 3 * 4 + 1] = -1.0;
    out[20] = 1.0; out[21] = 1.0; out[22] = 1.0;
    out[23] = 0.5 * p1 * p1 + 0.25 * q1 * q1 * q1 * q1 - 0.5 * q1 * q1 + 0.5 * p2 * p2 + 0.5 * q2 * q2 - h - 0.5;
    out[24] = 1.0; out[25] = 1.0;
}
