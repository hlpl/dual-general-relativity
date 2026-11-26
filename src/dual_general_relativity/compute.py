"""Core computation only - no theorems, no selection. Just GR calculus."""
import sympy as sp, threading
_FAST=threading.local()
def set_fast(v):
    _FAST.on=bool(v)
def is_fast():
    return bool(getattr(_FAST,'on',False))
def fsimp(e):
    if isinstance(e, sp.MatrixBase): return e.applyfunc(fsimp)
    if e==0: return sp.S(0)
    try:
        # Fast mode: together() ONLY - no cancel(), no factor(). Tested on Kerr:
        # together-only curvature finishes while cancel()/factor() hang >100s.
        # Same maths, expressions just stay as single fractions.
        if is_fast(): return sp.together(e)
        return sp.factor(sp.cancel(sp.together(e)))
    except Exception: return e
def is_zero(x):
    try:
        if isinstance(x, sp.MatrixBase): return all(fsimp(e)==0 for e in x)
        return fsimp(x)==0
    except Exception: return False
def is_diagonal(m):
    n=m.rows; return all(m[i,j]==0 for i in range(n) for j in range(n) if i!=j)
def christoffel(g, ginv, coords):
    n=len(coords); G=[[[sp.S(0)]*n for _ in range(n)] for _ in range(n)]
    for l in range(n):
        for m in range(n):
            for nu in range(m,n):
                s=0
                for k in range(n): s+=ginv[l,k]*(sp.diff(g[k,nu],coords[m])+sp.diff(g[k,m],coords[nu])-sp.diff(g[m,nu],coords[k]))
                G[l][m][nu]=G[l][nu][m]=fsimp(s/2)
    return G
def riemann(Gam, coords):
    n=len(coords); R=[[[[sp.S(0)]*n for _ in range(n)] for _ in range(n)] for _ in range(n)]
    for rho in range(n):
        for sig in range(n):
            for mu in range(n):
                for nu in range(mu+1,n):
                    s=sp.diff(Gam[rho][nu][sig],coords[mu])-sp.diff(Gam[rho][mu][sig],coords[nu])
                    for k in range(n): s+=Gam[rho][mu][k]*Gam[k][nu][sig]-Gam[rho][nu][k]*Gam[k][mu][sig]
                    s=fsimp(s); R[rho][sig][mu][nu]=s; R[rho][sig][nu][mu]=-s
    return R
def kretschmann_scalar(g, ginv, Riem, n):
    Rl=[[[[fsimp(sum(g[a,e]*Riem[e][b][c][d] for e in range(n))) for d in range(n)] for c in range(n)] for b in range(n)] for a in range(n)]
    diag=is_diagonal(g); tot=0
    for a in range(n):
        for b in range(n):
            for c in range(n):
                for d in range(n):
                    if Rl[a][b][c][d]==0: continue
                    if diag: up=Riem[a][b][c][d]*ginv[b,b]*ginv[c,c]*ginv[d,d]
                    else: up=sum(ginv[b,f]*ginv[c,gg]*ginv[d,h]*Riem[a][f][gg][h] for f in range(n) for gg in range(n) for h in range(n))
                    tot+=Rl[a][b][c][d]*up
    return fsimp(tot)
def curvature(g, coords, kretschmann=False):
    n=len(coords); ginv=fsimp(g.inv()); Gam=christoffel(g,ginv,coords); Riem=riemann(Gam,coords)
    Ric=sp.Matrix(n,n,lambda s,v: fsimp(sum(Riem[l][s][l][v] for l in range(n))))
    Rs=fsimp(sum(ginv[i,j]*Ric[i,j] for i in range(n) for j in range(n)))
    G=fsimp(Ric-sp.Rational(1,2)*Rs*g); Gmix=fsimp(ginv*G)
    out=dict(g=g,ginv=ginv,Gamma=Gam,Riem=Riem,Ric=Ric,R=Rs,G=G,Gmix=Gmix,K=None)
    if kretschmann: out['K']=kretschmann_scalar(g,ginv,Riem,n)
    return out
def swap_subs(coords): return {coords[0]:coords[1], coords[1]:coords[0]}
def swap_perm(n):
    P=sp.eye(n); P[0,0]=P[1,1]=0; P[0,1]=P[1,0]=1; return P
def pullback_cov(T, coords):
    n=len(coords); P=swap_perm(n); Ts=T.subs(swap_subs(coords), simultaneous=True); return fsimp(P.T*Ts*P)
def swap_metric(gt, coords, eps=-1): return fsimp(eps*pullback_cov(gt, coords))
def symmetrize(T):
    n=T.rows; return sp.Matrix(n,n,lambda i,j: T[min(i,j),max(i,j)])
def geodesic_acceleration(Gam, velocity):
    """d2x^mu/dlambda^2 = -Gamma^mu_{ab} v^a v^b, v^a = dx^a/dlambda.
    For g: lambda=t (x^0). For f: lambda=r (x^1). Velocity is user input."""
    n=len(velocity); out=[]
    for mu in range(n):
        s=0
        for a in range(n):
            for b in range(n): s+=Gam[mu][a][b]*velocity[a]*velocity[b]
        out.append(fsimp(-s))
    return out
def defect_tensor(g,f,eta,alpha,beta,gamma): return fsimp(alpha*g+beta*f-gamma*eta)
def mixing_metric(g,f,alpha,beta,gamma): return fsimp((alpha*g+beta*f)/gamma)
def signature_at(mat, subs):
    try:
        import numpy as np; A=np.array(mat.subs(subs).evalf().tolist(),dtype=float)
        ev=np.linalg.eigvalsh((A+A.T)/2); tol=1e-9*max(1.0,float(np.abs(ev).max()))
        return int((ev<-tol).sum()),int((ev>tol).sum()),int((np.abs(ev)<=tol).sum())
    except Exception: return None
def schwarzschild_pair_events(alpha,beta,gamma,r_s):
    import math; out=dict(q=None,events=[],notes=[]); a,b,c,rs=map(float,(alpha,beta,gamma,r_s))
    if a==0 or b==0 or c==0: out['notes'].append('alpha, beta, gamma must all be nonzero.'); return out
    if rs<=0: out['notes'].append('r_s must be > 0.'); return out
    q=(b*b+c*c-a*a)/(b*c); out['q']=q
    if abs(q)<2: out['notes'].append('|q|<2: no real event.'); return out
    k2=(a-c)/b
    if k2<=0: out['notes'].append('(alpha-gamma)/beta <= 0: no real event.'); return out
    disc=math.sqrt(q*q-4)
    for y in [(q+disc)/2,(q-disc)/2]:
        ev=dict(y=y,x=None,r=None,t=None,r_t=None,valid=False,why='')
        if y==0: ev['why']='y=0'; out['events'].append(ev); continue
        x=(c*y-b)/(a*y); ev['x']=x
        if x>=1: ev['why']='x>=1'
        elif y>=1: ev['why']='y>=1'
        elif x==0: ev['why']='x=0'
        else:
            r=rs/(1-x); t=math.sqrt(k2)*r; rt=t*(1-y); ev.update(r=r,t=t,r_t=rt,valid=(r>0 and t>0 and rt>0))
        out['events'].append(ev)
    return out
