"""Pipeline: inputs -> f, Tf, G, epsilon, geodesics, EE checks. No theorems."""
import re, sympy as sp
from . import compute as dc
_FORBIDDEN=re.compile(r'__|import|eval|exec|open\s*\(|lambda|getattr|setattr|subprocess|\bos\b|\bsys\b|globals|locals|compile')
def sanitize(t):
    if _FORBIDDEN.search(t or ''): raise ValueError('Forbidden token. Use plain SymPy math only.')
    return t
def split_top(text, delims):
    parts,depth,cur=[],0,[]
    for ch in text:
        if ch in '([{': depth+=1
        elif ch in ')]}': depth-=1
        if depth==0 and ch in delims: parts.append(''.join(cur)); cur=[]
        else: cur.append(ch)
    parts.append(''.join(cur)); return [p.strip() for p in parts if p.strip()!='']
def make_locals(coords):
    loc={str(c):c for c in coords}
    for n in ['alpha','beta','gamma','Lambda','Lambda_g','Lambda_f','r_s','r_t','R','c','k','q','K','N','kappa','a']:
        if n not in loc: loc[n]=sp.Symbol(n)
    for fn in ['S','rho','p','M','H','f','A','B']:
        loc[fn]=sp.Function(fn)
    return loc
def sym(text,loc): return sp.sympify(sanitize(text),locals=loc,rational=True)
def parse_matrix(text,loc):
    text=(text or '').strip()
    if not text: return None
    rows=split_top(sanitize(text),';\n'); mat=[[sp.sympify(e,locals=loc,rational=True) for e in split_top(row,',')] for row in rows]
    n=len(mat)
    if any(len(r)!=n for r in mat): raise ValueError('matrix must be square')
    return sp.Matrix(mat)
def parse_point(text,loc):
    subs={}
    for part in (text or '').split(','):
        if '=' in part:
            k,v=part.split('=',1); subs[sym(k.strip(),loc)]=sym(v.strip(),loc)
    return subs
def parse_vec(text,loc,n):
    parts=[p.strip() for p in (text or '').split(',') if p.strip()!='']
    if len(parts)!=n: raise ValueError(f'velocity needs {n} components, got {len(parts)}')
    return [sym(p,loc) for p in parts]
def fmt(x):
    try: return '0' if abs(float(x))<1e-15 else '%.6g'%float(x)
    except Exception: return str(x)
def num(e,subs):
    try: return '%.6g'%float(sp.N(e.subs(subs)))
    except Exception:
        try: return sp.latex(e.subs(subs))
        except Exception: return '?'
FORM_KEYS=['preset','coords','g','Tg','Tf_mode','Tf','alpha','beta','gamma','eps','kappa','eta_preset','eta','point','vg','vf','opt_K','fast']
_PARAM_GLOBAL={'alpha','beta','gamma','kappa','eps','epsilon'}
_MATH_FN={'sin','cos','tan','asin','acos','atan','atan2','sinh','cosh','tanh','exp','log','sqrt','Abs','sign','floor','ceiling'}
def _f_param_name(name):
    if name=='r_s': return 'r_t'
    if name.endswith('_t'): return name
    return name+'_t'
def rename_params(expr,coords):
    coord_names={str(c) for c in coords}; coord_syms=set(coords)
    def ren(e):
        if isinstance(e, sp.Expr) and e.is_Function:
            fname=getattr(e.func,'__name__',None)
            if fname and fname not in _MATH_FN and fname not in coord_names and fname not in _PARAM_GLOBAL:
                newf=sp.Function(_f_param_name(fname)); return newf(*[ren(a) for a in e.args])
        if isinstance(e, sp.Symbol):
            if e in coord_syms or e==sp.pi or str(e) in coord_names or str(e) in _PARAM_GLOBAL: return e
            return sp.Symbol(_f_param_name(str(e)))
        if not isinstance(e, sp.Expr): return e
        if not e.args: return e
        try: return e.func(*[ren(a) for a in e.args])
        except Exception: return e
    if isinstance(expr, sp.MatrixBase): return expr.applyfunc(lambda x: ren(x))
    return ren(expr)
def param_mapping(expr,coords):
    coord_names={str(c) for c in coords}; m={}
    for s in expr.free_symbols:
        if str(s) in coord_names or str(s) in _PARAM_GLOBAL or s==sp.pi: continue
        m[str(s)]=_f_param_name(str(s))
    for fn in expr.atoms(sp.Function):
        fname=getattr(fn.func,'__name__',None)
        if fname and fname not in _MATH_FN and fname not in coord_names and fname not in _PARAM_GLOBAL: m.setdefault(fname,_f_param_name(fname))
    return m
def point_for_f(point,coords):
    out=dict(point); coord_names={str(c) for c in coords}
    for k,v in list(point.items()):
        if isinstance(k, sp.Symbol) and str(k) not in coord_names and str(k) not in _PARAM_GLOBAL and k!=sp.pi:
            nk=sp.Symbol(_f_param_name(str(k)))
            if nk not in out: out[nk]=v
    return out

def _terms(expr):
    try: e=sp.expand(expr)
    except Exception: e=expr
    if e==0: return []
    return list(sp.Add.make_args(e))
def _has(expr, syms):
    try: return bool(set(expr.free_symbols) & set(syms))
    except Exception: return False
def _term_str(term):
    try: return sp.latex(term)
    except Exception: return str(term)
def _find_term(expr, pred):
    for t in _terms(expr):
        try:
            if pred(t): return t
        except Exception: pass
    return None
def _coeff_of_r(term, r):
    # term = coeff * r**k (k>=1) -> return (coeff, k) or None
    try:
        if r is None: return None
        poly=sp.Poly(sp.expand(term), r)
        if poly is None: return None
        for mon, coeff in poly.terms():
            if mon[0]>=1: return (coeff, mon[0])
    except Exception: pass
    return None

def build_notes(g, Tg, cg, acc_g, coords, kappa):
    notes=[]
    def add(txt):
        if txt and txt not in notes: notes.append(txt)
    n=len(coords)
    t_sym=coords[0] if n>=1 else None
    r_sym=coords[1] if n>=2 else None
    # Symbols / functions present
    all_exprs=[g, Tg]
    free=set()
    for e in all_exprs:
        try: free |= set(e.free_symbols)
        except Exception: pass
    free_names={str(x) for x in free}
    has_lambda = ('Lambda' in free_names) or ('Lambda_g' in free_names)
    # --- gather candidate expressions ---
    g00=g[0,0] if n>=1 else sp.Integer(0)
    grr=g[1,1] if n>=2 else sp.Integer(0)
    gtt_str=_term_str(g00)
    # --- 1. Lambda / dark energy: term in g_tt / g_rr / T ---
    lam_term=None
    for expr in (g00, grr):
        lam_term=_find_term(expr, lambda tt: 'Lambda' in {str(x) for x in tt.free_symbols})
        if lam_term is not None: break
    if lam_term is not None:
        add(f"This metric may explain dark energy because of the term: ${ _term_str(lam_term) }$ in $g_{{\\mu\\nu}}$ (a $\\Lambda$ term; $\\Lambda>0$ gives repulsion at large $r$).")
    elif has_lambda:
        add("This metric may explain dark energy because it contains a $\\Lambda$ term (repulsion at large $r$ when $\\Lambda>0$).")
    # --- 2. Radial acceleration analysis: d2r/dt2 = acc_g[1] ---
    if n>=2 and acc_g is not None and len(acc_g)>=2:
        acc_r=acc_g[1]
        # a) term proportional to r (c*r, Lambda*r, H^2*r, ...)
        for term in _terms(acc_r):
            cr=_coeff_of_r(term, r_sym)
            if cr is None: continue
            coeff, power=cr
            if power!=1: continue
            coeff_s=str(coeff)
            # skip pure Schwarzschild-like -1/r^2 (handled below, power check excludes it)
            if 'Lambda' in coeff_s:
                add(f"This metric may explain the accelerated expansion of the universe because of the term: ${ _term_str(term) }$ in $\\ddot r = { _term_str(acc_r) }$ ($+\\Lambda r$ pushes outward; this is the dark-energy term).")
            elif coeff_s.strip() in ('0',): continue
            else:
                # sign: try numeric sign, else treat symbolic coeff as reported
                try:
                    v=float(sp.N(coeff))
                    if v>0:
                        add(f"This metric may explain universe expansion because of the term: ${ _term_str(term) }$ in $\\ddot r = { _term_str(acc_r) }$ (a positive term proportional to $r$ accelerates test particles outward).")
                    elif v<0:
                        add(f"This metric may explain gravitational collapse / deceleration because of the term: ${ _term_str(term) }$ in $\\ddot r = { _term_str(acc_r) }$ (a negative term proportional to $r$ pulls inward).")
                except Exception:
                    add(f"This metric may explain universe expansion because of the term: ${ _term_str(term) }$ in $\\ddot r = { _term_str(acc_r) }$ (a term proportional to $r$: if its coefficient is positive it accelerates test particles outward).")
        # b) Newtonian 1/r^2 gravity
        if _find_term(acc_r, lambda tt: r_sym is not None and tt.has(1/r_sym**2)) is not None:
            add(f"This metric may explain Newtonian gravity / orbits because of the term: ${ _term_str(_find_term(acc_r, lambda tt: tt.has(1/r_sym**2))) }$ in $\\ddot r$ (a $1/r^2$ attraction, the $GM/r^2$ form).")
    # --- 3. Scale factor / FLRW: spatial metric depends on t ---
    scale_fn=None; scale_expr=None
    # Scale factor = a function of t (coords[0]) in the spatial metric, e.g. S(t).
    # A function of r, e.g. b(r) in a wormhole, is NOT a scale factor.
    try:
        for fn in g[1,1].atoms(sp.Function):
            fname=getattr(fn.func,'__name__',None)
            if fname and fname not in ('sin','cos','tan','sinh','cosh','exp','log','sqrt','Abs') and t_sym is not None and t_sym in fn.args:
                scale_fn=fname; scale_expr=g[1,1]; break
    except Exception: pass
    # also exp(H0*t) / t**power in spatial entries
    if scale_fn is not None:
        add(f"This metric may explain cosmic expansion because of the term: ${ _term_str(scale_expr) }$ in the spatial metric (a scale factor ${scale_fn}(t)$; the universe expands as ${scale_fn}$ grows, with $H = {scale_fn}'/{scale_fn}$).")
        # radiation / matter from the Tg equation of state is checked below; scale-factor power hints
        if 'exp' in str(scale_expr) and 'H0' in str(scale_expr):
            add(f"This metric may explain dark energy / inflation because of the term: ${ _term_str(scale_expr) }$ (exponential expansion, $p=-\\rho$, the $\\Lambda$ signature).")
    # --- 4. Dark matter: log(r) potential, 1/r^2 density, M(r), or matter-dominated FLRW ---
    dm_term=None
    dm_term=_find_term(g00, lambda tt: tt.has(sp.log(r_sym)) if r_sym is not None else False)
    if dm_term is not None:
        add(f"This metric may explain dark matter (flat galaxy rotation curves) because of the term: ${ _term_str(dm_term) }$ in $g_{{tt}}$ (a $\\log r$ potential gives $v^2 = r\\,d\\Phi/dr \\approx$ constant).")
    if dm_term is None:
        dm_term=_find_term(Tg[0,0] if n>=1 else sp.Integer(0), lambda tt: r_sym is not None and tt.has(1/r_sym**2))
        if dm_term is not None:
            add(f"This metric may explain dark matter because of the term: ${ _term_str(dm_term) }$ in $T^g_{{tt}}$ (a density $\\rho \\propto 1/r^2$ is the isothermal dark-matter halo profile, giving flat rotation curves).")
    # M(r) / M function in g_tt: 1 - 2M(r)/r
    for fn in g00.atoms(sp.Function):
        fname=getattr(fn.func,'__name__',None)
        if fname and fname in ('M','m','Mh'):
            add(f"This metric may explain dark matter because of the term: ${ _term_str(g00) }$ in $g_{{tt}}$ (an enclosed mass $M(r)$; if $M(r)$ keeps growing with $r$ beyond the visible mass, that extra mass is the dark-matter halo).")
            break
    # --- 5. CMB / radiation / matter equation of state from T ---
    if n>=2:
        try:
            t00=Tg[0,0]; t11=Tg[1,1]
            # FLRW-style: spatial T entries carry a(t)^2 factor; check ratio p/rho via Tg with metric: p ~ -T11/g11, rho ~ -T00/g00 (sign conventions vary, so use symbolic ratio of Tg entries to g entries)
            if scale_fn is not None:
                add(f"This metric may explain the CMB because of the term: ${ _term_str(scale_expr) }$ (the scale factor; radiation cools as $T \\propto 1/{scale_fn}(t)$, so the CMB is the redshifted relic of the hot early universe).")
            # p = rho/3 radiation: Tg11/g11 approx -1/3 * Tg00/g00 -> check if Tg has explicit 1/3 factor with same density symbol
            if '1/3' in str(Tg) or '/3' in str(Tg):
                pass
        except Exception: pass
    # --- 6. Schwarzschild-like GR tests: (1 - r_s/r) ---
    if 'r_s' in free_names or 'r_t' in free_names:
        sch_term=_find_term(g00, lambda tt: 'r_s' in {str(x) for x in tt.free_symbols})
        if sch_term is not None:
            add(f"This metric may explain the classic GR tests (Mercury perihelion, light bending, Shapiro delay, gravitational redshift) because of the term: ${ _term_str(sch_term) }$ in $g_{{tt}}$ (the $(1-r_s/r)$ factor; expanding it gives the test predictions).")
    # --- 7. Frame dragging: off-diagonal g_t-phi / g_t-x ---
    for i in range(n):
        for j in range(n):
            if i!=j and g[i,j]!=0:
                # skip swap-trivial? any off-diagonal is dragging / rotation
                add(f"This metric may explain frame dragging (Lense-Thirring precession) because of the term: ${ _term_str(g[i,j]) }$ in $g_{{{i}{j}}}$ (an off-diagonal $g_{{t\\phi}}$-type term drags inertial frames).")
                break
        else: continue
        break
    # --- 8. Horizon: g_tt = 0 factor ---
    if _find_term(g00, lambda tt: False) is None and n>=2:
        # factor g00: if it contains a factor (r - X) or (1 - X/r), report horizon
        try:
            fac=sp.factor(g00)
            fac_s=str(fac)
            if ('1 -' in fac_s or 'r -' in fac_s or '- r' in fac_s) and ('r_s' in fac_s or 'r_h' in fac_s or 'Lambda' in fac_s or '/r' in fac_s):
                add(f"This metric may describe a black-hole horizon because of the term: ${ _term_str(g00) }$ in $g_{{tt}}$ ($g_{{tt}}=0$ at the horizon).")
        except Exception: pass
    # --- 9. Gravitational redshift: g_tt varies with r ---
    if r_sym is not None:
        try:
            if sp.diff(g00, r_sym)!=0 and 'r_s' not in free_names:
                add(f"This metric may explain gravitational redshift because of the term: ${ _term_str(g00) }$ in $g_{{tt}}$ (clocks run at a rate $\\sqrt{{-g_{{tt}}}}$; $g_{{tt}}$ varying with $r$ means clocks at different $r$ tick differently).")
        except Exception: pass
    # --- 10. Gravitational waves: cos/sin whose ARGUMENT mixes t with a spatial coord, e.g. cos(t-z) ---
    # sin(theta) alone is NOT a wave (Kerr has it), so the argument itself must contain t AND a spatial coord.
    for i in range(n):
        for j in range(n):
            try:
                _is_wave=False
                for fn in g[i,j].atoms(sp.Function):
                    fname=getattr(fn.func,'__name__',None)
                    if fname in ('cos','sin') and t_sym is not None and len(fn.args)>=1:
                        _arg_syms=set(fn.args[0].free_symbols) if hasattr(fn.args[0],'free_symbols') else set()
                        if t_sym in _arg_syms and (_arg_syms & set(coords[1:])):
                            _is_wave=True; break
                if _is_wave:
                    add(f"This metric may describe gravitational waves because of the term: ${ _term_str(g[i,j]) }$ in $g_{{{i}{j}}}$ (an oscillatory term $\cos/\sin(t - x)$: a wave travelling in $x$).")
                    break
            except Exception: pass
        else: continue
        break
    # --- 11. Wormhole: 1/(1 - b(r)/r) in g_rr ---
    if n>=2:
        try:
            _has_b = any(getattr(fn.func,'__name__',None)=='b' for fn in grr.atoms(sp.Function))
            if _has_b and '/r' in str(grr):
                add(f"This metric may describe a wormhole because of the term: ${ _term_str(grr) }$ in $g_{{rr}}$ (a $1/(1-b(r)/r)$ form; $b(r)$ is the shape function, $b=r$ is the throat).")
        except Exception: pass
    # Fallback: if nothing found, say so honestly instead of inventing
    if not notes:
        add("No specific explanatory advantage was found from the terms of this metric alone (no $\\Lambda$, $r$-proportional acceleration, scale factor, $\\log r$ / $1/r^2$ halo, $(1-r_s/r)$, or off-diagonal dragging term was detected).")
    return notes

def analyze(form,set_progress=lambda p,l: None):
    names=[c.strip() for c in form['coords'].split(',') if c.strip()]
    if len(names) not in (2,3,4): raise ValueError('need 2-4 coordinates')
    coords=list(sp.symbols(' '.join(names))); n=len(coords); loc=make_locals(coords)
    _fast=str(form.get('fast','')).strip().lower() in ('1','fast','true','yes')
    dc.set_fast(_fast)
    eps=-1 if str(form.get('eps','-1')).strip() in ('-1','-') else 1
    kappa=sym(form.get('kappa') or '8*pi',loc)
    alpha,beta,gamma=(sym(form.get(k) or d,loc) for k,d in (('alpha','1'),('beta','-1'),('gamma','3')))
    g=parse_matrix(form['g'],loc)
    if g is None: raise ValueError('g is required')
    if g.rows!=n: raise ValueError(f'g must be {n}x{n}')
    Tg=parse_matrix(form.get('Tg'),loc)
    if Tg is None: Tg=sp.zeros(n); Tg_note='Tg blank -> vacuum (0)'
    else: Tg_note='Tg given'
    if Tg.rows!=n: raise ValueError(f'Tg must be {n}x{n}')
    mode=(form.get('Tf_mode') or 'vacuum').strip()
    if mode=='same': Tf=rename_params(dc.swap_metric(Tg,coords,1),coords); Tf_note='Tf = phi^* Tg, with f own params (r_s -> r_t, ...)'
    elif mode=='set':
        Tf=parse_matrix(form.get('Tf'),loc)
        if Tf is None: Tf=sp.zeros(n); Tf_note='Tf set but blank -> vacuum (0)'
        else: Tf_note='Tf given (set)'
        if Tf.rows!=n: raise ValueError(f'Tf must be {n}x{n}')
    else: Tf=sp.zeros(n); Tf_note='Tf = vacuum (0)'
    ep=form.get('eta_preset','spherical')
    if ep=='cartesian': eta=sp.diag(*([-1]+[1]*(n-1)))
    elif ep=='spherical':
        r,th=loc.get('r'),loc.get('theta')
        if r is None or th is None or n!=4: raise ValueError('spherical eta needs 4 coords incl. r, theta - use cartesian/custom')
        eta=sp.diag(-1,1,r**2,r**2*sp.sin(th)**2)
    else:
        eta=parse_matrix(form.get('eta'),loc)
        if eta is None: raise ValueError('custom eta required')
    point=parse_point(form.get('point',''),loc)
    vg=parse_vec(form.get('vg') or ','.join(['1']+['0']*(n-1)),loc,n)
    vf=parse_vec(form.get('vf') or ','.join(['0','1']+['0']*(n-2)) if n>=2 else '1',loc,n)
    set_progress(20,'Swap f = eps * phi^* g, own params ...'); f=rename_params(dc.swap_metric(g,coords,eps),coords); f_param_map=param_mapping(g,coords)
    set_progress(40,'Curvature of g ...'); cg=dc.curvature(g,coords,kretschmann=(bool(form.get('opt_K')) and not _fast))
    set_progress(60,'Curvature of f ...'); cf=dc.curvature(f,coords,kretschmann=(bool(form.get('opt_K')) and not _fast))
    eps_g=dc.fsimp(cg['G']-kappa*Tg); eps_f=dc.fsimp(cf['G']-kappa*Tf)
    acc_g=dc.geodesic_acceleration(cg['Gamma'],vg); acc_f=dc.geodesic_acceleration(cf['Gamma'],vf)
    D=dc.defect_tensor(g,f,eta,alpha,beta,gamma); h=None
    if not dc.is_zero(gamma): h=dc.mixing_metric(g,f,alpha,beta,gamma)
    def _ee_zero(eps_res,subs):
        if _fast and subs:
            try:
                vals=[abs(float(sp.N(e.subs(subs)))) for e in eps_res]; return max(vals)<1e-6
            except Exception: pass
        if dc.is_zero(eps_res): return True
        if not subs: return False
        try:
            vals=[abs(float(sp.N(e.subs(subs)))) for e in eps_res]; return max(vals)<1e-6
        except Exception: return False
    try:
        _notes=build_notes(g, Tg, cg, acc_g, coords, kappa)
        # Notes were built with $...$ delimiters; the page's MathJax is configured
        # for \(...\) inline math, so convert $...$ pairs to \(...\) here.
        # $...$ was never reliably typeset after the AJAX insert.
        def _to_paren(note):
            parts=note.split('$')
            if len(parts)<3: return note
            out=[]
            for i,part in enumerate(parts):
                out.append('\\('+part+'\\)' if i%2==1 else part)
            return ''.join(out)
        _notes=[_to_paren(n) for n in _notes]
    except Exception:
        _notes=['Note analysis failed for this metric.']
    checks=[('EE satisfied for g: G - kappa*Tg = 0 ?',_ee_zero(eps_g,point),'check'),('EE satisfied for f: G - kappa*Tf = 0 ?',_ee_zero(eps_f,point_for_f(point,coords)),'check')]
    L=sp.latex; B=lambda m_: L(m_,mat_str='bmatrix')
    def gamma_str(Gam):
        rows=[]
        for mu in range(n):
            for a in range(n):
                for b in range(a,n):
                    if Gam[mu][a][b]!=0: rows.append((rf'\Gamma^{{{mu}}}_{{{a}{b}}}',L(Gam[mu][a][b])))
        return rows or [('(all zero)','')]
    sections=[('g_{\\mu\\nu}\\ \\text{(input)}',B(g)),('T^{g}_{\\mu\\nu}\\ \\text{(input)}',B(Tg)),('f_{\\mu\\nu} = \\epsilon\\,\\varphi^* g\\ \\text{, own params}',B(f)),('T^{f}_{\\mu\\nu}\\ \\text{('+Tf_note+')}',B(Tf)),('G_{\\mu\\nu}[g]',B(cg['G'])),('\\\\varepsilon_{\\mu\\nu}[g] = G - \\kappa T^g',B(eps_g)),('G_{\\mu\\nu}[f]',B(cf['G'])),('\\\\varepsilon_{\\mu\\nu}[f] = G - \\kappa T^f',B(eps_f)),('D_{\\mu\\nu} = \\alpha g + \\beta f - \\gamma\\eta\\ \\text{(info only)}',B(D))]
    if h is not None: sections.append(('h_{\\mu\\nu} = (\\alpha g + \\beta f)/\\gamma\\ \\text{(info only)}',B(h)))
    scalars=[('Mode',r'\text{'+('Fast --- K skipped, light simplification, EE checked numerically at the point' if _fast else 'Normal --- full simplification, K computed if ticked')+'}'),('kappa',L(kappa)),('epsilon',str(eps)),('Tf rule',Tf_note),('Tg rule',Tg_note),(r'f\ \text{parameters}',r'\text{'+', '.join(f'{k} \\to {v}' for k,v in sorted(f_param_map.items()))+'}'),(r'R[g]',L(cg['R'])),(r'R[f]',L(cf['R'])),(r'\det g',L(sp.factor(dc.fsimp(g.det())))),(r'\det f',L(sp.factor(dc.fsimp(f.det()))))]
    if cg['K'] is not None: scalars+=[(r'K[g]',L(cg['K'])),(r'K[f]',L(cf['K']))]
    scalars+=[(r'\ddot x^\mu[g] = -\Gamma^\mu_{ab} v^a v^b, \ v=d/d t',L(sp.Matrix(acc_g).T)),(r'\ddot x^\mu[f] = -\Gamma^\mu_{ab} v^a v^b, \ v=d/d r',L(sp.Matrix(acc_f).T))]
    scalars+=[(r'\Gamma[g] \ nonzero',', '.join(f'{a}={b}' for a,b in gamma_str(cg['Gamma']))),(r'\Gamma[f] \ nonzero',', '.join(f'{a}={b}' for a,b in gamma_str(cf['Gamma'])))]
    numeric=None
    if point:
        point_f=point_for_f(point,coords)
        parts=[r'R[g]=%s'%num(cg['R'],point),r'R[f]=%s'%num(cf['R'],point_f)]
        if cg['K'] is not None: parts+=[r'K[g]=%s'%num(cg['K'],point),r'K[f]=%s'%num(cf['K'],point_f)]
        parts+=[r'\ddot x^\mu[g]=[%s]'%(', '.join(num(x,point) for x in acc_g)),r'\ddot x^\mu[f]=[%s]'%(', '.join(num(x,point_f) for x in acc_f))]
        parts+=[r'\varepsilon[g]_{00}=%s'%num(eps_g[0,0],point),r'\varepsilon[f]_{00}=%s'%num(eps_f[0,0],point_f)]
        numeric=r',\ '.join(parts)
    dc.set_fast(False)
    set_progress(100,'Done')
    return dict(sections=sections,scalars=scalars,checks=checks,numeric=numeric,notes=_notes,events=[],raw=dict(g=g,Tg=Tg,f=f,Tf=Tf,cg=cg,cf=cf,eps_g=eps_g,eps_f=eps_f,acc_g=acc_g,acc_f=acc_f,D=D,h=h,coords=coords,vg=vg,vf=vf,kappa=kappa))
