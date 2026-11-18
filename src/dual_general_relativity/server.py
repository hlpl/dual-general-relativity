import re, traceback, threading, uuid
import sympy as sp
from flask import Flask, render_template_string, request, jsonify
try:
    from . import compute as dc  # package import: dual_general_relativity.server
except ImportError:
    import dgr_compute as dc  # standalone: server.py next to dgr_compute.py
app = Flask(__name__)
PRESETS = {
 'minkowski': {'coords':'t,x,y,z','eta_preset':'cartesian','g':'-1,0,0,0; 0,1,0,0; 0,0,1,0; 0,0,0,1','t_mode':'zero','Tg':'','Tf':'','point':''},
 'minkowski-companion': {'coords':'t,x,y,z','eta_preset':'cartesian','g':'-1,0,0,0; 0,1,0,0; 0,0,1,0; 0,0,0,1','t_mode':'zero','Tg':'','Tf':'','point':''},
 'schwarzschild': {'coords':'t,r,theta,phi','eta_preset':'spherical','g':'-(1-2*M/r),0,0,0; 0,1/(1-2*M/r),0,0; 0,0,r**2,0; 0,0,0,r**2*sin(theta)**2','t_mode':'zero','Tg':'','Tf':'','point':'r=5, M=1, theta=1'},
 'schwarzschild-companion': {'coords':'t,r,theta,phi','eta_preset':'spherical','g':'-1-2*M/r,0,0,0; 0,(1-4*M/r)/(1-2*M/r),0,0; 0,0,r**2,0; 0,0,0,r**2*sin(theta)**2','t_mode':'separate','Tg':'','Tf':'0,0,0,0; 0,0,0,0; 0,0,0,0; 0,0,0,0','point':'r=5, M=1, theta=1'},
 'flrw': {'coords':'t,x,y,z','eta_preset':'cartesian','g':'-1,0,0,0; 0,a(t)**2,0,0; 0,0,a(t)**2,0; 0,0,0,a(t)**2','t_mode':'separate','Tg':'3*Derivative(a(t),t)**2/(8*pi*a(t)**2),0,0,0; 0,-(2*Derivative(a(t),t,t)/a(t) + Derivative(a(t),t)**2/a(t)**2)*a(t)**2/(8*pi),0,0; 0,0,-(2*Derivative(a(t),t,t)/a(t) + Derivative(a(t),t)**2/a(t)**2)*a(t)**2/(8*pi),0; 0,0,0,-(2*Derivative(a(t),t,t)/a(t) + Derivative(a(t),t)**2/a(t)**2)*a(t)**2/(8*pi)','Tf':'','point':''},
 'flrw-companion': {'coords':'t,x,y,z','eta_preset':'cartesian','g':'-1,0,0,0; 0,2-a(t)**2,0,0; 0,0,2-a(t)**2,0; 0,0,0,2-a(t)**2','t_mode':'separate','Tg':'','Tf':'3*Derivative(a(t),t)**2/(8*pi*a(t)**2),0,0,0; 0,-(2*Derivative(a(t),t,t)/a(t) + Derivative(a(t),t)**2/a(t)**2)*a(t)**2/(8*pi),0,0; 0,0,-(2*Derivative(a(t),t,t)/a(t) + Derivative(a(t),t)**2/a(t)**2)*a(t)**2/(8*pi),0; 0,0,0,-(2*Derivative(a(t),t,t)/a(t) + Derivative(a(t),t)**2/a(t)**2)*a(t)**2/(8*pi)','point':''},
 'interior': {'coords':'t,r,theta,phi','eta_preset':'spherical','g':'-(3*sqrt(1-2*M/R)-sqrt(1-2*M*r**2/R**3))**2/4,0,0,0; 0,1/(1-2*M*r**2/R**3),0,0; 0,0,r**2,0; 0,0,0,r**2*sin(theta)**2','t_mode':'separate','Tg':'(3*M/(4*pi*R**3))*(3*sqrt(1-2*M/R)-sqrt(1-2*M*r**2/R**3))**2/4,0,0,0; 0,((3*M/(4*pi*R**3))*(sqrt(1-2*M*r**2/R**3)-sqrt(1-2*M/R))/(3*sqrt(1-2*M/R)-sqrt(1-2*M*r**2/R**3)))/(1-2*M*r**2/R**3),0,0; 0,0,((3*M/(4*pi*R**3))*(sqrt(1-2*M*r**2/R**3)-sqrt(1-2*M/R))/(3*sqrt(1-2*M/R)-sqrt(1-2*M*r**2/R**3)))*r**2,0; 0,0,0,((3*M/(4*pi*R**3))*(sqrt(1-2*M*r**2/R**3)-sqrt(1-2*M/R))/(3*sqrt(1-2*M/R)-sqrt(1-2*M*r**2/R**3)))*r**2*sin(theta)**2','Tf':'','point':'r=1, M=1, R=3, theta=1'},
 'interior-companion': {'coords':'t,r,theta,phi','eta_preset':'spherical','g':'(3*sqrt(1-2*M/R)-sqrt(1-2*M*r**2/R**3))**2/4-2,0,0,0; 0,(1-4*M*r**2/R**3)/(1-2*M*r**2/R**3),0,0; 0,0,r**2,0; 0,0,0,r**2*sin(theta)**2','t_mode':'separate','Tg':'','Tf':'(3*M/(4*pi*R**3))*(3*sqrt(1-2*M/R)-sqrt(1-2*M*r**2/R**3))**2/4,0,0,0; 0,((3*M/(4*pi*R**3))*(sqrt(1-2*M*r**2/R**3)-sqrt(1-2*M/R))/(3*sqrt(1-2*M/R)-sqrt(1-2*M*r**2/R**3)))/(1-2*M*r**2/R**3),0,0; 0,0,((3*M/(4*pi*R**3))*(sqrt(1-2*M*r**2/R**3)-sqrt(1-2*M/R))/(3*sqrt(1-2*M/R)-sqrt(1-2*M*r**2/R**3)))*r**2,0; 0,0,0,((3*M/(4*pi*R**3))*(sqrt(1-2*M*r**2/R**3)-sqrt(1-2*M/R))/(3*sqrt(1-2*M/R)-sqrt(1-2*M*r**2/R**3)))*r**2*sin(theta)**2','point':'r=1, M=1, R=3, theta=1'},
}
JOBS = {}
def split_top_level(text, delims):
    parts=[]; depth=0; cur=[]
    for ch in text:
        if ch in '([{': depth+=1
        elif ch in ')]}': depth-=1
        if depth==0 and ch in delims:
            parts.append(''.join(cur)); cur=[]
        else:
            cur.append(ch)
    parts.append(''.join(cur))
    return [p.strip() for p in parts if p.strip()!='']
def parse_matrix(text, local):
    text=(text or '').strip()
    if not text: raise ValueError('empty matrix')
    rows=split_top_level(text, ';\n')
    mat=[]
    for row in rows:
        entries=split_top_level(row, ',')
        mat.append([sp.sympify(e, locals=local) for e in entries])
    n=len(mat)
    if any(len(r)!=n for r in mat): raise ValueError('matrix must be square')
    return sp.Matrix(mat)
def is_zero_mat(M):
    try: return all(dc._fsimp(x)==0 for x in M)
    except Exception: return False
def parse_point(text, local):
    subs={}
    for part in (text or '').split(','):
        if '=' in part:
            k,v=part.split('=',1); subs[sp.sympify(k.strip(), locals=local)]=sp.sympify(v.strip(), locals=local)
    return subs
def staged_compute(form, set_progress):
    coord_names=[c.strip() for c in form['coords'].split(',') if c.strip()]
    if len(coord_names) not in (2,3,4): raise ValueError('need 2-4 coordinates')
    coords=list(sp.symbols(' '.join(coord_names)))
    local={str(c): c for c in coords}
    for name in ['M','R','rho','p']:
        if name not in local: local[name]=sp.Symbol(name)
    if 'a' not in local: local['a']=sp.Function('a')
    set_progress(5, 'Parsing g and T ...')
    g=parse_matrix(form['g'], local)
    if form['eta_preset']=='cartesian': eta=sp.diag(*([-1]+[1]*(len(coords)-1)))
    elif form['eta_preset']=='spherical':
        r=local.get('r'); th=local.get('theta')
        if r is None or th is None: raise ValueError('spherical eta needs coords r and theta')
        eta=sp.diag(-1,1,r**2,r**2*sp.sin(th)**2)
    else: eta=parse_matrix(form['eta'], local)
    n=len(coords)
    fast_mode = (form.get('compute_mode') == 'fast')
    if fast_mode:
        _subs_early = parse_point(form.get('point',''), local)
        _param_subs = {k: v for k, v in _subs_early.items() if k not in coords}
        if _param_subs:
            g = g.subs(_param_subs)
            eta = eta.subs(_param_subs)
    # T RULE (T rule): blank = symbolic UNKNOWN, never 0.
    # T = 0 ONLY when explicitly written as a zero matrix, or t_mode == 'zero' (Vacuum).
    # A defined T in a preset (FLRW / interior fluid) is NOT zero.
    Tf=Tg=None
    def T_or_unknown(text):
        return parse_matrix(text, local) if (text or '').strip() else None  # None -> symbolic below
    if form['t_mode']=='unknown': Tf=Tg=None            # both symbolic
    elif form['t_mode']=='zero': Tg=Tf=sp.zeros(n)      # explicit vacuum only
    elif form['t_mode']=='same':
        Tg=T_or_unknown(form['Tg']); Tf=Tg
    else:  # 'separate'
        Tg=T_or_unknown(form['Tg']); Tf=T_or_unknown(form['Tf'])
    Tg_symbolic = Tg is None
    Tf_symbolic = Tf is None
    if fast_mode and '_param_subs' in dir() and _param_subs:
        if Tg is not None: Tg = Tg.subs(_param_subs)
        if Tf is not None: Tf = Tf.subs(_param_subs)
    set_progress(12, 'Computing f = 2 eta - g and M ...')
    f=dc._fsimp(2*eta-g)
    set_progress(28, 'Curvature of g: Gamma, Riemann, Ricci, G(g) ...')
    cur_g=dc.curvature_all(g, coords)
    set_progress(48, 'Curvature of f: Gamma, Riemann, Ricci, G(f) ...')
    cur_f=dc.curvature_all(f, coords)
    finv=cur_f['ginv']; M=dc._fsimp(finv*g)
    set_progress(66, 'Mixed Ricci Rcal and C = R(f) + Rcal ...')
    Rg=cur_g['Riem']
    if fast_mode:
        Rcal=sp.zeros(n); Rcal_scalar=sp.S(0); Cmat=cur_f['Ric']; C_scalar=cur_f['Rscalar']
    else:
        Rcal=sp.zeros(n)
        for mu in range(n):
            for nu in range(n):
                Rcal[mu,nu]=dc._fsimp(sum(M[lam,a]*Rg[a][mu][lam][nu] for lam in range(n) for a in range(n)))
        Rcal_scalar=dc._fsimp(sum(finv[mu,nu]*Rcal[mu,nu] for mu in range(n) for nu in range(n)))
        Cmat=dc._fsimp(cur_f['Ric']+Rcal)
        C_scalar=dc._fsimp(sum(finv[mu,nu]*Cmat[mu,nu] for mu in range(n) for nu in range(n)))
    set_progress(78, 'Einstein tensors and eps = G - 8 pi T ...')
    if Tf is None:
        Tf=sp.Matrix(n,n,lambda i,j: sp.Function(f'Tf_{i}{j}')(*coords) if i<=j else sp.Function(f'Tf_{j}{i}')(*coords))
    if Tg is None:
        Tg=sp.Matrix(n,n,lambda i,j: sp.Function(f'Tg_{i}{j}')(*coords) if i<=j else sp.Function(f'Tg_{j}{i}')(*coords))
    Tf=sp.Matrix(n,n,lambda i,j: Tf[min(i,j),max(i,j)]); Tg=sp.Matrix(n,n,lambda i,j: Tg[min(i,j),max(i,j)])
    eps_f=cur_f['G']-8*sp.pi*Tf; eps_g=cur_g['G']-8*sp.pi*Tg  # raw difference, no simplify
    set_progress(88, 'Checking G(f) decomposition ...')
    Gf_decomp=cur_f['G']  # identity by definition of C, no recomputation
    Gf_check=sp.zeros(n)  # zero by construction
    set_progress(94, 'Rendering results ...')
    # Implied stress tensors: T_imp = G / (8 pi) is the T that WOULD make eps = 0.
    # Shown always (it is informative even when T is supplied: compare it with the
    # supplied T). When T is unknown it is the only matter content the app can test.
    Timp_g=dc.implied_T(cur_g['G']); Timp_f=dc.implied_T(cur_f['G'])
    # Mixed components for rho / pressures, only meaningful for a diagonal metric.
    def _diag_mixed(Tcov, ginv):
        try:
            if all(ginv[i,j]==0 for i in range(n) for j in range(n) if i!=j):
                Mmix=dc._fsimp(ginv*Tcov)
                return [dc._fsimp(Mmix[i,i]) for i in range(n)]
        except Exception:
            return None
        return None
    mix_g=_diag_mixed(Timp_g, cur_g['ginv']); mix_f=_diag_mixed(Timp_f, finv)
    # rho = -T^t_t, p_i = T^i_i. Scalars appended below when diagonal.
    extra_scalars=[]
    if mix_g is not None:
        extra_scalars.append((r"\rho^{(g)}_{imp}=-T^{(g)t}{}_{t}", sp.latex(-mix_g[0])))
        for i in range(1,n):
            extra_scalars.append((r"p^{(g)}_{imp,%d}=T^{(g)%d}{}_{%d}" % (i,i,i), sp.latex(mix_g[i])))
    if mix_f is not None:
        extra_scalars.append((r"\rho^{(f)}_{imp}=-T^{(f)t}{}_{t}", sp.latex(-mix_f[0])))
        for i in range(1,n):
            extra_scalars.append((r"p^{(f)}_{imp,%d}=T^{(f)%d}{}_{%d}" % (i,i,i), sp.latex(mix_f[i])))
    titles=[r"Input\ g_{\mu\nu}",r"Background\ \eta_{\mu\nu}",r"Companion\ f_{\mu\nu}=2\eta-g",r"M^\lambda{}_{\rho}=f^{\lambda\alpha}g_{\alpha\rho}",r"Ricci\ R^{(g)}_{\mu\nu}",r"Ricci\ R^{(f)}_{\mu\nu}",r"\mathcal{R}_{\mu\nu}",r"C_{\mu\nu}=R^{(f)}_{\mu\nu}+\mathcal{R}_{\mu\nu}",r"Einstein\ G^{(g)}_{\mu\nu}",r"Einstein\ G^{(f)}_{\mu\nu}",r"T^{(g)}_{\mu\nu}",r"T^{(f)}_{\mu\nu}",r"\varepsilon^{(g)}_{\mu\nu}=G^{(g)}_{\mu\nu}-8\pi T^{(g)}_{\mu\nu}",r"\varepsilon^{(f)}_{\mu\nu}=G^{(f)}_{\mu\nu}-8\pi T^{(f)}_{\mu\nu}",r"T^{(g)}_{imp,\mu\nu}=G^{(g)}_{\mu\nu}/8\pi",r"T^{(f)}_{imp,\mu\nu}=G^{(f)}_{\mu\nu}/8\pi"]
    mats=[g,eta,f,M,cur_g['Ric'],cur_f['Ric'],Rcal,Cmat,cur_g['G'],cur_f['G'],Tg,Tf,eps_g,eps_f,Timp_g,Timp_f]
    sections=[(t, sp.latex(m, mat_str='bmatrix')) for t,m in zip(titles,mats)]
    scalars=[(r"Mode", 'Fast - Rcal/C skipped' if fast_mode else 'Full'),(r"R^{(g)}", sp.latex(cur_g['Rscalar'])),(r"R^{(f)}", sp.latex(cur_f['Rscalar'])),(r"\mathcal{R}", sp.latex(Rcal_scalar)),(r"C", sp.latex(C_scalar)),(r"\det g", sp.latex(sp.factor(dc._fsimp(g.det())))),(r"\det f", sp.latex(sp.factor(dc._fsimp(f.det())))),(r"R^{(f)}+\mathcal{R}-C\ (identity,\ holds\ by\ definition\ of\ C)", sp.latex(dc._fsimp(cur_f['Rscalar']+Rcal_scalar-C_scalar)))] + extra_scalars
    # Independent test of C (explicit formula with (M+delta)); only valid if d(eta)=0.
    if fast_mode:
        c_check_ok=None
    elif dc.eta_is_const(eta, coords):
        C_formula=dc.c_formula(M, cur_g['Gamma'], coords)
        c_check_ok=is_zero_mat(dc._fsimp(Cmat-C_formula))
    else:
        c_check_ok=None   # not applicable: d(eta) != 0 in these coordinates
    subs=parse_point(form['point'], local)
    sig_g=dc.signature_at(g, subs) if subs else None
    sig_f=dc.signature_at(f, subs) if subs else None
    checks=[(r"C = explicit\ formula\ with\ (M+\delta)\ [independent;\ Cartesian\ eta\ only]", c_check_ok),
            (r"G^{(f)}\ decomposition\ [identity\ by\ definition\ of\ C,\ not\ a\ test]", is_zero_mat(Gf_check)),
            (r"\varepsilon^{(g)}=0 (N/A if T^{(g)} unknown)", None if Tg_symbolic else is_zero_mat(eps_g)),(r"\varepsilon^{(f)}=0 (N/A if T^{(f)} unknown)", None if Tf_symbolic else is_zero_mat(eps_f))]
    if subs:
        checks.append((r"g\ Lorentzian\ at\ point\ (sig=%s)" % (sig_g,), dc.is_lorentzian(sig_g) if sig_g else None))
        checks.append((r"f\ Lorentzian\ at\ point\ (sig=%s)" % (sig_f,), dc.is_lorentzian(sig_f) if sig_f else None))
    numeric=None
    if subs:
        def num(e):
            try: return '%.6g' % float(sp.N(e.subs(subs)))
            except Exception: return sp.latex(e.subs(subs))
        numeric=r"R^{(g)}=%s,\ R^{(f)}=%s,\ \mathcal{R}=%s,\ C=%s" % (num(cur_g['Rscalar']), num(cur_f['Rscalar']), num(Rcal_scalar), num(C_scalar))
        if mix_g is not None and mix_f is not None:
            numeric += r",\ \rho^{(g)}_{imp}=%s,\ p^{(g)}_{imp,1}=%s,\ \rho^{(f)}_{imp}=%s,\ p^{(f)}_{imp,1}=%s,\ \rho^{(f)}_{imp}+p^{(f)}_{imp,1}=%s" % (num(-mix_g[0]), num(mix_g[1]), num(-mix_f[0]), num(mix_f[1]), num(-mix_f[0]+mix_f[1]))
    set_progress(100, 'Done')
    return dict(sections=sections, scalars=scalars, checks=checks, numeric=numeric)
def run_job(job_id, form):
    job=JOBS[job_id]
    def set_progress(p, label):
        job['progress']=p; job['label']=label
    try:
        job['result']=staged_compute(form, set_progress); job['status']='done'
    except Exception:
        job['status']='error'; job['error']=traceback.format_exc()
def start_job(form):
    job_id=str(uuid.uuid4())
    JOBS[job_id]={'status':'running','progress':0,'label':'Starting ...','result':None,'error':None}
    threading.Thread(target=run_job, args=(job_id, form), daemon=True).start()
    return job_id
RESULT_HTML = '''{% if error %}<div class="error">{{error}}</div>{% endif %}{% if result %}<div class="card"><h2>Scalars</h2>{% for name,val in scalars %}<div class="scalar">$$ {{name}} = {{val}} $$</div>{% endfor %}<h2>Checks</h2>{% for name,ok in checks %}<div>{{name}} - {% if ok is none %}<span>N/A</span>{% else %}<span class="{{'pass' if ok else 'fail'}}">{{'PASS' if ok else 'FAIL / non-zero'}}</span>{% endif %}</div>{% endfor %}{% if numeric %}<h2>Numeric evaluation at point</h2><div class="scalar">$$ {{numeric}} $$</div>{% endif %}</div>{% for title,mat in sections %}<div class="card scroll"><h3>$$ {{title}} $$</h3><div>$$ {{mat}} $$</div></div>{% endfor %}{% endif %}'''
HTML = '''<!doctype html><html><head><meta charset="utf-8"><title>DGR Calculator</title>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<style>body{font-family:system-ui,sans-serif;max-width:1100px;margin:24px auto;padding:0 16px;background:#f7f7f5}h1{margin-bottom:4px}.card{background:#fff;border:1px solid #ddd;border-radius:12px;padding:16px;margin:14px 0}label{font-weight:600;display:block;margin:12px 0 4px}textarea,input[type=text],select{width:100%;box-sizing:border-box;padding:8px;font-family:ui-monospace,monospace;font-size:14px}textarea{height:110px}.row{display:grid;grid-template-columns:1fr 1fr;gap:16px}button{background:#111;color:#fff;border:0;border-radius:8px;padding:10px 18px;font-size:16px;cursor:pointer}button:disabled{opacity:.5;cursor:wait}.error{background:#ffe9e9;border:1px solid #f99;padding:12px;border-radius:8px;white-space:pre-wrap}.pass{color:#0a7a2f;font-weight:700}.fail{color:#b00;font-weight:700}.scroll{overflow-x:auto}.scalar{font-size:17px;margin:6px 0}.note{color:#555;font-size:14px}.bar-wrap{background:#eee;border-radius:999px;height:22px;overflow:hidden}.bar{background:#111;height:100%;width:0%;transition:width .3s}.bar-label{margin:6px 0 0;font-size:14px}</style></head><body>
<h1>Dual General Relativity - g + T calculator</h1>
<p class="note">Enter g (and T, if known) as SymPy expressions. A blank T means <b>symbolic unknown</b>, never 0. T = 0 only if you write a zero matrix or choose <b>Vacuum</b>. Rows separated by <code>;</code> or newline, entries by <code>,</code>. Use <code>a(t)</code> for a function, <code>M</code>, <code>R</code> as free parameters. Each preset has its companion $f = 2\\eta - g$ as a separate preset; applying $D$ twice returns the original. A blank $T$ box means $T$ is <b>symbolic unknown</b>, never $0$. $T=0$ only if you write a zero matrix or choose Vacuum. A defined $T$ in a preset (FLRW / interior fluid) is NOT zero.</p>
<form id="calc-form" method="post"><div class="card">
<label>Preset (loads example into the form)</label><select name="preset" onchange="this.form.submit()">{% for k in presets %}<option value="{{k}}" {% if form.preset==k %}selected{% endif %}>{{k}}</option>{% endfor %}</select>
<label>Coordinates</label><input type="text" name="coords" value="{{form.coords}}">
<div class="row"><div><label>Background eta preset</label><select name="eta_preset"><option value="cartesian" {% if form.eta_preset=='cartesian' %}selected{% endif %}>Cartesian diag(-1,1,1,1)</option><option value="spherical" {% if form.eta_preset=='spherical' %}selected{% endif %}>Spherical diag(-1,1,r^2,r^2 sin^2 theta)</option><option value="custom" {% if form.eta_preset=='custom' %}selected{% endif %}>Custom (below)</option></select></div>
<div><label>Evaluation point (optional, e.g. r=5, M=1)</label><input type="text" name="point" value="{{form.point}}"></div></div>
<label>Custom eta (only if Custom)</label><textarea name="eta" style="height:70px">{{form.eta}}</textarea>
<label>g</label><textarea name="g">{{form.g}}</textarea>
<label>Compute mode</label><select name="compute_mode"><option value="full" {% if form.compute_mode!='fast' %}selected{% endif %}>Full - all quantities incl. Rcal / C (slow on interior)</option><option value="fast" {% if form.compute_mode=='fast' %}selected{% endif %}>Fast - substitute M, R, ... from the point, skip Rcal / C, keep G, eps, T_imp, rho/p</option></select>
<label>T mode</label><select name="t_mode"><option value="unknown" {% if form.t_mode=='unknown' %}selected{% endif %}>Unknown - keep T(g), T(f) symbolic (same as leaving both blank)</option><option value="zero" {% if form.t_mode=='zero' %}selected{% endif %}>Vacuum - T = 0 in both sectors</option><option value="same" {% if form.t_mode=='same' %}selected{% endif %}>Known - one T, used for both sectors</option><option value="separate" {% if form.t_mode=='separate' %}selected{% endif %}>Known - separate T(g) and T(f)</option></select>
<label>T / T(g) (ignored in Unknown / Vacuum modes; blank = symbolic unknown)</label><textarea name="Tg">{{form.Tg}}</textarea>
<label>T(f) (only in Separate mode; blank = symbolic unknown)</label><textarea name="Tf">{{form.Tf}}</textarea>
<p><button id="compute-btn" type="submit" name="action" value="compute">Compute all</button></p>
<div id="progress" style="display:none"><div class="bar-wrap"><div id="bar" class="bar"></div></div><div class="bar-label"><span id="bar-pct">0%</span> - <span id="bar-label">Starting ...</span></div></div>
</div></form>
<div id="results"></div>
<script>
var form=document.getElementById('calc-form');
var btn=document.getElementById('compute-btn');
function poll(jobId){
  fetch('/api/progress/'+jobId).then(r=>r.json()).then(function(j){
    document.getElementById('bar').style.width=j.progress+'%';
    document.getElementById('bar-pct').textContent=j.progress+'%';
    document.getElementById('bar-label').textContent=j.label;
    if(j.status==='done'){
      fetch('/api/result/'+jobId).then(r=>r.text()).then(function(html){
        document.getElementById('results').innerHTML=html;
        if(window.MathJax) MathJax.typesetPromise();
        document.getElementById('progress').style.display='none'; btn.disabled=false; btn.textContent='Compute all';
      });
    } else if(j.status==='error'){
      fetch('/api/result/'+jobId).then(r=>r.text()).then(function(html){
        document.getElementById('results').innerHTML=html;
        document.getElementById('progress').style.display='none'; btn.disabled=false; btn.textContent='Compute all';
      });
    } else { setTimeout(function(){poll(jobId);}, 500); }
  });
}
form.addEventListener('submit', function(e){
  if(e.submitter && e.submitter.value==='compute'){
    e.preventDefault();
    document.getElementById('results').innerHTML='';
    document.getElementById('progress').style.display='block';
    btn.disabled=true; btn.textContent='Computing ...';
    fetch('/api/start', {method:'POST', body:new FormData(form)}).then(r=>r.json()).then(function(j){ poll(j.job_id); });
  }
});
</script>
</body></html>'''
@app.route('/', methods=['GET','POST'])
def index():
    form=dict(PRESETS['minkowski']); form['preset']='minkowski'; form['eta']=''; form['compute_mode']='full'
    if request.method=='POST':
        form={k: request.form.get(k,'') for k in ['preset','coords','eta_preset','eta','g','t_mode','Tg','Tf','point','compute_mode']}
        if request.form.get('action')!='compute':
            p=PRESETS.get(form['preset'], PRESETS['minkowski']); form.update(p); form['preset']=request.form.get('preset'); form['eta']=''
    return render_template_string(HTML, presets=list(PRESETS), form=form)
@app.route('/api/start', methods=['POST'])
def api_start():
    form={k: request.form.get(k,'') for k in ['preset','coords','eta_preset','eta','g','t_mode','Tg','Tf','point']}
    return jsonify({'job_id': start_job(form)})
@app.route('/api/progress/<job_id>')
def api_progress(job_id):
    job=JOBS.get(job_id)
    if not job: return jsonify({'status':'error','progress':0,'label':'unknown job'}), 404
    return jsonify({'status':job['status'],'progress':job['progress'],'label':job['label']})
@app.route('/api/result/<job_id>')
def api_result(job_id):
    job=JOBS.get(job_id)
    if not job: return 'Unknown job', 404
    if job['status']=='error':
        return render_template_string(RESULT_HTML, error=job['error'], result=False)
    if job['status']!='done': return 'Not ready yet', 409
    r=job['result']
    return render_template_string(RESULT_HTML, error=None, result=True, sections=r['sections'], scalars=r['scalars'], checks=r['checks'], numeric=r['numeric'])


def create_app():
    """Return the Flask app (same app as `python -m dual_general_relativity`)."""
    return app


def main(host="127.0.0.1", port=5000):
    """Entry point for the `dual-general-relativity` console script. Local only."""
    print("Dual General Relativity — open http://127.0.0.1:5000")
    print("T rule: blank T = symbolic unknown, never 0. T = 0 only if written as zero or Vacuum mode.")
    app.run(host=host, port=port, debug=True)


if __name__ == "__main__":
    main()
