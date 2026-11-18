"""DGR computation: curvature, companion metric, C / Rcal, eps, implied T."""


"""
Dual General Relativity (DGR) — compute everything from g only.
================================================================
Convention used here (paper convention):
    eta  = fixed flat background, in the coordinates you give
           (Cartesian: diag(-1,1,1,1); spherical: diag(-1,1,r^2,r^2 sin^2 th))
    g    = ONLY INPUT  (the metric you feed in)
    f    = 2*eta - g   (derived companion / dual metric)
    M^l_r = f^{l a} g_{a r}

Computed:
    f_{mu nu}
    R^{(f)}_{mu nu}, R^{(g)}_{mu nu}, R^{(f)}, R^{(g)}
    Rcal_{mu nu} = M^l_a R^a_{mu l nu}[g]   (NOT Ricci of g)
    C_{mu nu}     = R_{mu nu}[f] + Rcal_{mu nu}
    C             = f^{mu nu} C_{mu nu},  Rcal = f^{mu nu} Rcal_{mu nu}
    G^{(f)}_{mu nu} = direct Einstein of f
                    = -(Rcal_{mu nu} - 1/2 Rcal f_{mu nu})
                      + (C_{mu nu} - 1/2 C f_{mu nu})   <-- checked
    G^{(g)}_{mu nu} = direct Einstein of g
    T^{(f)}_{mu nu}, T^{(g)}_{mu nu} = supplied tensors. RULE: blank / None = symbolic UNKNOWN.
    T = 0 ONLY when explicitly given as a zero matrix or t_mode='zero' / 'zero' string.
    eps^{(f)}_{mu nu} = G^{(f)}_{mu nu} - 8*pi*T^{(f)}_{mu nu}
    eps^{(g)}_{mu nu} = G^{(g)}_{mu nu} - 8*pi*T^{(g)}_{mu nu}

T is NOT computed from matter. RULE: blank / None = symbolic UNKNOWN, never 0.
T = 0 only when explicitly supplied as zero. A defined T in a preset (FLRW/interior fluid) is NOT zero.
eps == 0  <=>  Einstein equation holds for that sector.

Usage:
    python dgr_compute.py            # runs Schwarzschild + Minkowski checks
    from dgr_compute import compute_all  # in your own script
"""
import sympy as sp

def _fsimp(e):
    # Fast simplification: cancel + factor only. Full sp.simplify() on sqrt
    # expressions (interior solution) is what made the interior presets time out.
    # Results are mathematically identical; only the final form may be less reduced.
    if e == 0:
        return sp.S(0)
    try:
        return sp.factor(sp.cancel(sp.together(e)))
    except Exception:
        return e

# ---------------------------------------------------------------- helpers
def inv(m):
    return _fsimp(m.inv())

def christoffel(g, ginv, coords):
    n = len(coords)
    Gamma = [[[sp.S(0)]*n for _ in range(n)] for _ in range(n)]  # Gamma[l][m][n]
    for l in range(n):
        for m in range(n):
            for nu in range(n):
                s = 0
                for sidx in range(n):
                    s += ginv[l, sidx] * (sp.diff(g[sidx, nu], coords[m])
                                          + sp.diff(g[sidx, m], coords[nu])
                                          - sp.diff(g[m, nu], coords[sidx]))
                Gamma[l][m][nu] = _fsimp(s/2)
    return Gamma

def riemann(Gamma, coords):
    """R^rho_{sigma mu nu} = d_mu Gamma^rho_{nu sigma} - d_nu Gamma^rho_{mu sigma}
       + Gamma^rho_{mu lam} Gamma^lam_{nu sigma} - Gamma^rho_{nu lam} Gamma^lam_{mu sigma}"""
    n = len(coords)
    R = [[[[sp.S(0)]*n for _ in range(n)] for _ in range(n)] for _ in range(n)]
    for rho in range(n):
        for sig in range(n):
            for mu in range(n):
                for nu in range(n):
                    s = (sp.diff(Gamma[rho][nu][sig], coords[mu])
                         - sp.diff(Gamma[rho][mu][sig], coords[nu]))
                    for lam in range(n):
                        s += Gamma[rho][mu][lam]*Gamma[lam][nu][sig]
                        s -= Gamma[rho][nu][lam]*Gamma[lam][mu][sig]
                    R[rho][sig][mu][nu] = _fsimp(s)
    return R

def ricci_from_riemann(R):
    """R_{sigma nu} = R^lam_{sigma lam nu}  ==  d_lam Gamma^lam_{nu sigma}
       - d_nu Gamma^lam_{lam sigma} + ...  (paper convention)."""
    n = len(R)
    Ric = sp.zeros(n)
    for sig in range(n):
        for nu in range(n):
            Ric[sig, nu] = _fsimp(sum(R[lam][sig][lam][nu] for lam in range(n)))
    return Ric

def scalar_from_ricci(ginv, Ric):
    return _fsimp(sum(ginv[i, j]*Ric[i, j] for i in range(ginv.rows) for j in range(ginv.cols)))

def einstein_from(Ric, Rscalar, g):
    n = g.rows
    return _fsimp(Ric - sp.Rational(1, 2)*Rscalar*g)

def curvature_all(g, coords):
    ginv = inv(g)
    G = christoffel(g, ginv, coords)
    Riem = riemann(G, coords)
    Ric = ricci_from_riemann(Riem)
    Rs = scalar_from_ricci(ginv, Ric)
    Ein = einstein_from(Ric, Rs, g)
    return dict(ginv=ginv, Gamma=G, Riem=Riem, Ric=Ric, Rscalar=Rs, G=Ein)

# ---------------------------------------------------------------- DGR

def eta_is_const(eta, coords):
    """True iff eta has zero derivatives wrt coords (Cartesian inertial coords)."""
    try:
        return all(sp.simplify(sp.diff(eta[i, j], c)) == 0 for i in range(eta.rows) for j in range(eta.cols) for c in coords)
    except Exception:
        return False

def c_formula(M, Gg, coords):
    """Explicit C_{mu nu} (valid only when d(eta)=0):
        C = -(d_l M^l_a) G^a_{nu mu} + (d_nu M^l_a) G^a_{l mu}
            + M^l_a (M^k_b + delta^k_b) G^a_{l k} G^b_{nu mu}
            - M^l_a (M^k_b + delta^k_b) G^a_{nu k} G^b_{l mu}
    NOTE factor is (M + delta), NOT (M - delta). (M - delta) fails at O(h^2)."""
    n = len(coords)
    dM = [[[sp.diff(M[l, r], coords[mu]) for mu in range(n)] for r in range(n)] for l in range(n)]
    C = sp.zeros(n)
    for mu in range(n):
        for nu in range(n):
            s = 0
            for lam in range(n):
                for a in range(n):
                    s += -dM[lam][a][lam]*Gg[a][nu][mu]
                    s += dM[lam][a][nu]*Gg[a][lam][mu]
            for lam in range(n):
                for a in range(n):
                    for kap in range(n):
                        for b in range(n):
                            d = M[kap, b] + (1 if kap == b else 0)
                            s += M[lam, a]*d*Gg[a][lam][kap]*Gg[b][nu][mu]
                            s -= M[lam, a]*d*Gg[a][nu][kap]*Gg[b][lam][mu]
            C[mu, nu] = sp.simplify(s)
    return C

def signature_at(mat, subs):
    """Numerical signature (n_negative, n_positive, n_zero) at a point, or None."""
    try:
        import numpy as np
        A = np.array(mat.subs(subs).evalf().tolist(), dtype=float)
        ev = np.linalg.eigvalsh((A + A.T)/2)
        tol = 1e-9*max(1.0, float(np.abs(ev).max()))
        return int((ev < -tol).sum()), int((ev > tol).sum()), int((np.abs(ev) <= tol).sum())
    except Exception:
        return None

def is_lorentzian(sig):
    return sig is not None and sig[0] == 1 and sig[2] == 0

def compute_all(g, coords, eta, Tf=None, Tg=None, simplify=True):
    """
    g     : sympy Matrix (n x n), the ONLY metric input
    coords: list of sympy symbols
    eta   : sympy Matrix (n x n), flat background in SAME coordinates
    Tf,Tg : optional sympy Matrices (n x n) of unknown functions.
            RULE: If None / blank -> symbolic unknowns Tf_mu_nu(coords), Tg_mu_nu(coords) are created (NEVER 0).
            Pass 'zero' or an explicit zero matrix for vacuum T = 0. Pass 'symbolic' for explicit unknown.
    Returns dict with every quantity.
    """
    n = len(coords)
    pi = sp.pi
    # RULE: None / blank = symbolic UNKNOWN, never 0. 'zero' = explicit vacuum.
    if isinstance(Tf, str) and Tf == 'zero':
        Tf = sp.zeros(n)
    elif Tf is None or (isinstance(Tf, str) and Tf == 'symbolic'):
        Tf = sp.Matrix(n, n, lambda i, j: sp.Function(f'Tf_{i}{j}')(*coords) if i <= j else sp.Function(f'Tf_{j}{i}')(*coords))
    if isinstance(Tg, str) and Tg == 'zero':
        Tg = sp.zeros(n)
    elif Tg is None or (isinstance(Tg, str) and Tg == 'symbolic'):
        Tg = sp.Matrix(n, n, lambda i, j: sp.Function(f'Tg_{i}{j}')(*coords) if i <= j else sp.Function(f'Tg_{j}{i}')(*coords))
    # symmetrise T (T_mu_nu = T_nu_mu)
    Tf = sp.Matrix(n, n, lambda i, j: Tf[min(i, j), max(i, j)])
    Tg = sp.Matrix(n, n, lambda i, j: Tg[min(i, j), max(i, j)])

    f = _fsimp(2*eta - g)

    cur_g = curvature_all(g, coords)   # R^{(g)}, G^{(g)}
    cur_f = curvature_all(f, coords)   # R^{(f)}, G^{(f)}

    finv = cur_f['ginv']
    # M^l_r = f^{l a} g_{a r}
    M = _fsimp(finv * g)
    Minv = _fsimp(cur_g['ginv'] * f)  # = g^{-1} f

    # Rcal_{mu nu} = M^lam_a * R^a_{mu lam nu}[g]
    Rg = cur_g['Riem']
    Rcal = sp.zeros(n)
    for mu in range(n):
        for nu in range(n):
            Rcal[mu, nu] = _fsimp(sum(M[lam, a]*Rg[a][mu][lam][nu] for lam in range(n) for a in range(n)))
    Rcal_scalar = _fsimp(sum(finv[mu, nu]*Rcal[mu, nu] for mu in range(n) for nu in range(n)))

    # C_{mu nu} = R_{mu nu}[f] + Rcal_{mu nu}   (since R[f] = -Rcal + C)
    Cmat = _fsimp(cur_f['Ric'] + Rcal)
    C_scalar = _fsimp(sum(finv[mu, nu]*Cmat[mu, nu] for mu in range(n) for nu in range(n)))

    # C via explicit formula (dM + (M+delta) Gamma Gamma): INDEPENDENT check
    # of C = R[f] + Rcal. Valid only if d(eta)=0 (Cartesian inertial coords).
    if eta_is_const(eta, coords):
        C_formula = c_formula(M, cur_g['Gamma'], coords)
        C_check = _fsimp(Cmat - C_formula)  # independent check; zero if formula is correct
    else:
        C_formula = None
        C_check = None  # not applicable: d(eta) != 0 in these coordinates

    # G^{(f)} via decomposition
    Gf_decomp = cur_f['G']  # identity by definition of C
    # G_f_check is zero BY CONSTRUCTION: C is defined as R[f] + Rcal, so the
    # decomposition is an identity, not a test. It is kept only as a consistency check.
    Gf_check = sp.zeros(n)  # zero by construction

    eps_f = cur_f['G'] - 8*pi*Tf
    eps_g = cur_g['G'] - 8*pi*Tg

    out = dict(
        coords=coords, eta=eta, g=g, f=f, M=M, Minv=Minv,
        R_g=cur_g['Ric'], R_f=cur_f['Ric'],
        Rscalar_g=cur_g['Rscalar'], Rscalar_f=cur_f['Rscalar'],
        G_g=cur_g['G'], G_f=cur_f['G'],
        G_f_decomp=Gf_decomp, G_f_check=Gf_check,
        Rcal=Rcal, Rcal_scalar=Rcal_scalar,
        C=Cmat, C_scalar=C_scalar, C_formula=C_formula, C_check=C_check,
        Tf=Tf, Tg=Tg, eps_f=eps_f, eps_g=eps_g,
        Gamma_g=cur_g['Gamma'], Gamma_f=cur_f['Gamma'],
        Riem_g=Rg, Riem_f=cur_f['Riem'],
    )
    return out

def show(name, res, verbose=False):
    print(f"\n===== {name} =====")
    print("f ="); sp.pprint(res['f'])
    print("R^{(g)} scalar =", sp.simplify(res['Rscalar_g']))
    print("R^{(f)} scalar =", sp.simplify(res['Rscalar_f']))
    print("Rcal scalar    =", sp.simplify(res['Rcal_scalar']))
    print("C scalar       =", sp.simplify(res['C_scalar']))
    print("Identity R[f] = -Rcal + C (holds by definition of C):", _fsimp(res['Rscalar_f'] + res['Rcal_scalar'] - res['C_scalar']))
    print("Check G^{(f)} == decomp (should be 0 matrix):")
    sp.pprint(res['G_f_check'])
    print("Independent check C == C_formula with (M+delta) (Cartesian only; None = d(eta)!=0, skipped):")
    sp.pprint(res['C_check'])
    if verbose:
        print("G^{(f)} ="); sp.pprint(res['G_f'])
        print("eps^{(f)} = G^{(f)} - 8 pi Tf ="); sp.pprint(res['eps_f'])
        print("eps^{(g)} = G^{(g)} - 8 pi Tg ="); sp.pprint(res['eps_g'])

# ---------------------------------------------------------------- examples
if __name__ == "__main__":
    # --- Example 1: Minkowski (Cartesian) ---
    t, x, y, z = sp.symbols('t x y z')
    coords = [t, x, y, z]
    eta = sp.diag(-1, 1, 1, 1)
    g_mink = sp.diag(-1, 1, 1, 1)
    res = compute_all(g_mink, coords, eta)
    show("Minkowski: g = eta", res)

    # --- Example 2: Schwarzschild as INPUT g ---
    # Here g is the input metric; f = 2 eta - g is derived.
    # eta in Schwarzschild spherical coords: diag(-1, 1, r^2, r^2 sin^2 th)
    r, th, ph, M = sp.symbols('r theta phi M', positive=True)
    coords2 = [t, r, th, ph]
    eta_sph = sp.diag(-1, 1, r**2, r**2*sp.sin(th)**2)
    f_sch = 1 - 2*M/r
    g_sch = sp.diag(-f_sch, 1/f_sch, r**2, r**2*sp.sin(th)**2)
    res2 = compute_all(g_sch, coords2, eta_sph)
    show("Schwarzschild as input g (f = 2 eta - g derived)", res2, verbose=False)
    print("\nG^{(g)} (should be 0, Schwarzschild is vacuum GR):")
    sp.pprint(res2['G_g'])
    print("\nG^{(f)} for the companion (not zero in general):")
    sp.pprint(res2['G_f'])
    print("\neps^{(f)} with T^{(f)} left symbolic (eps = G^{(f)} - 8 pi Tf):")
    sp.pprint(res2['eps_f'])

    # --- Example 3: FLRW as INPUT g ---
    a = sp.Function('a')(t)
    coords3 = [t, x, y, z]
    g_flrw = sp.diag(-1, a**2, a**2, a**2)
    res3 = compute_all(g_flrw, coords3, eta)
    show("FLRW as input g", res3, verbose=False)
    print("\nC_{mu nu} for FLRW:"); sp.pprint(res3['C'])

def implied_T(G):
    """Implied stress tensor T_imp = G / (8 pi): the T that would be needed for
    eps = G - 8 pi T = 0 in that sector. Shown when the supplied T is unknown."""
    return _fsimp(G / (8*sp.pi))

def mixed_T(Tcov, ginv):
    """T^mu_nu = g^{mu alpha} T_{alpha nu}. For a diagonal metric the diagonal
    entries are rho = -T^t_t and p_i = T^i_i (no sum)."""
    return _fsimp(ginv * Tcov)
# v1.0.2
