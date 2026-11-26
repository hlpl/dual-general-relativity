"""Presets: pure starting points. No theorems."""
BASE=dict(preset='custom (blank)',coords='t,r,theta,phi',g='',Tg='',Tf_mode='vacuum',Tf='',alpha='1',beta='-1',gamma='3',eps='-1',kappa='8*pi',eta_preset='spherical',eta='',point='r=3, t=0.5, r_s=1, theta=1',vg='1,0,0,0',vf='0,1,0,0',opt_K='1')
def _diag(a,b,c='r**2',d='r**2*sin(theta)**2'): return f'{a},0,0,0; 0,{b},0,0; 0,0,{c},0; 0,0,0,{d}'
def _schw(rname): return _diag(f'-(1-{rname}/r)',f'1/(1-{rname}/r)')
def _dS_T(rname,Lname):
    A=f'(1-{rname}/r-{Lname}*r**2/3)'; return _diag(f'{Lname}*{A}/(8*pi)',f'-{Lname}/(8*pi*{A})',f'-{Lname}*r**2/(8*pi)',f'-{Lname}*r**2*sin(theta)**2/(8*pi)')
def _dS(rname,Lname): return _diag(f'-(1-{rname}/r-{Lname}*r**2/3)',f'1/(1-{rname}/r-{Lname}*r**2/3)')
PRESETS={}
def _add():
    D=dict(BASE)
    PRESETS['custom (blank)']=dict(D)
    PRESETS['minkowski']=dict(D,g=_diag('-1','1'),Tg='0,0,0,0; 0,0,0,0; 0,0,0,0; 0,0,0,0',Tf_mode='vacuum',point='r=3, t=0.5, theta=1')
    PRESETS['schwarzschild (vacuum)']=dict(D,g=_schw('r_s'),Tg='0,0,0,0; 0,0,0,0; 0,0,0,0; 0,0,0,0',Tf_mode='vacuum',point='r=3, t=0.5, r_s=1, theta=1')
    PRESETS['schwarzschild pair flavour (Tf = Tg)']=dict(D,g=_schw('r_s'),Tg='0,0,0,0; 0,0,0,0; 0,0,0,0; 0,0,0,0',Tf_mode='same',point='r=3, t=0.5, r_s=1, theta=1')
    PRESETS['schwarzschild interior (constant density star)']=dict(D,g='-((3*sqrt(1-r_s/Rstar)-sqrt(1-r_s*r**2/Rstar**3))/2)**2,0,0,0; 0,1/(1-r_s*r**2/Rstar**3),0,0; 0,0,r**2,0; 0,0,0,r**2*sin(theta)**2',Tg='(3*r_s/(8*pi*Rstar**3))*((3*sqrt(1-r_s/Rstar)-sqrt(1-r_s*r**2/Rstar**3))/2)**2,0,0,0; 0,(3*r_s/(8*pi*Rstar**3))*((sqrt(1-r_s*r**2/Rstar**3)-sqrt(1-r_s/Rstar))/(3*sqrt(1-r_s/Rstar)-sqrt(1-r_s*r**2/Rstar**3)))/(1-r_s*r**2/Rstar**3),0,0; 0,0,r**2*(3*r_s/(8*pi*Rstar**3))*((sqrt(1-r_s*r**2/Rstar**3)-sqrt(1-r_s/Rstar))/(3*sqrt(1-r_s/Rstar)-sqrt(1-r_s*r**2/Rstar**3))),0; 0,0,0,r**2*sin(theta)**2*(3*r_s/(8*pi*Rstar**3))*((sqrt(1-r_s*r**2/Rstar**3)-sqrt(1-r_s/Rstar))/(3*sqrt(1-r_s/Rstar)-sqrt(1-r_s*r**2/Rstar**3)))',Tf_mode='same',point='r=2, t=0.5, r_s=1, Rstar=5, theta=1')
    PRESETS['schwarzschild-de Sitter (Kottler)']=dict(D,g=_dS('r_s','Lambda'),Tg=_dS_T('r_s','Lambda'),Tf_mode='same',point='r=3, t=0.5, r_s=1, Lambda=0.01, theta=1')
    _rn='(1-r_s/r+r_Q**2/r**2)'
    PRESETS['reissner-nordstrom (charged)']=dict(D,g=f'-{_rn},0,0,0; 0,1/{_rn},0,0; 0,0,r**2,0; 0,0,0,r**2*sin(theta)**2',Tg=f'-(r_Q**2/(8*pi*r**4))*(-{_rn}),0,0,0; 0,(r_Q**2/(8*pi*r**4))*(1/{_rn})*(-1),0,0; 0,0,r**2*(r_Q**2/(8*pi*r**4)),0; 0,0,0,r**2*sin(theta)**2*(r_Q**2/(8*pi*r**4))',Tf_mode='same',point='r=3, t=0.5, r_s=1, r_Q=0.5, theta=1')
    PRESETS['kerr (rotating vacuum)']=dict(D,g='-(1-r_s*r/(r**2+a**2*cos(theta)**2)),0,0,-r_s*a*r*sin(theta)**2/(r**2+a**2*cos(theta)**2); 0,(r**2+a**2*cos(theta)**2)/(r**2-r_s*r+a**2),0,0; 0,0,r**2+a**2*cos(theta)**2,0; -r_s*a*r*sin(theta)**2/(r**2+a**2*cos(theta)**2),0,0,(r**2+a**2+(r_s*a**2*r*sin(theta)**2)/(r**2+a**2*cos(theta)**2))*sin(theta)**2',Tg='0,0,0,0; 0,0,0,0; 0,0,0,0; 0,0,0,0',Tf_mode='vacuum',opt_K='',point='r=3, t=0.5, r_s=1, a=0.5, theta=1')
    PRESETS['kerr-newman (rotating charged)']=dict(D,g='-(1-(r_s*r-r_Q**2)/(r**2+a**2*cos(theta)**2)),0,0,-(r_s*r-r_Q**2)*a*sin(theta)**2/(r**2+a**2*cos(theta)**2); 0,(r**2+a**2*cos(theta)**2)/(r**2-r_s*r+a**2+r_Q**2),0,0; 0,0,r**2+a**2*cos(theta)**2,0; -(r_s*r-r_Q**2)*a*sin(theta)**2/(r**2+a**2*cos(theta)**2),0,0,(r**2+a**2+((r_s*r-r_Q**2)*a**2*sin(theta)**2)/(r**2+a**2*cos(theta)**2))*sin(theta)**2',Tg='r_Q**2*(-(r**2+a**2*cos(theta)**2)+r_s*r-r_Q**2)/(8*pi*(r**2+a**2*cos(theta)**2)**3),0,0,-a*r_Q**2*(r_s*r-r_Q**2)*sin(theta)**2/(8*pi*(r**2+a**2*cos(theta)**2)**3); 0,-r_Q**2/(8*pi*(r**2+a**2*cos(theta)**2)*(r**2-r_s*r+a**2+r_Q**2)),0,0; 0,0,r_Q**2/(8*pi*(r**2+a**2*cos(theta)**2)),0; -a*r_Q**2*(r_s*r-r_Q**2)*sin(theta)**2/(8*pi*(r**2+a**2*cos(theta)**2)**3),0,0,r_Q**2*(-a**2*(r**2-r_s*r+a**2+r_Q**2)*sin(theta)**2+(r**2+a**2)**2)*sin(theta)**2/(8*pi*(r**2+a**2*cos(theta)**2)**3)',Tf_mode='same',opt_K='',point='r=3, t=0.5, r_s=1, a=0.5, r_Q=0.3, theta=1')
    PRESETS['anti-de Sitter']=dict(D,g=_dS('r_s','Lambda'),Tg=_dS_T('r_s','Lambda'),Tf_mode='same',point='r=2, t=0.5, r_s=0, Lambda=-0.1, theta=1')
    # FLRW closed/open: de Sitter slicing, rho=3H0^2/(8pi), p=-rho, S=cosh/sinh(H0 t)/H0 satisfies Friedmann with k=+-1.
    PRESETS['FLRW closed (k=+1, de Sitter, explicit)']=dict(D,g='-1,0,0,0; 0,cosh(H0*t)**2/(H0**2*(1-r**2)),0,0; 0,0,cosh(H0*t)**2*r**2/H0**2,0; 0,0,0,cosh(H0*t)**2*r**2*sin(theta)**2/H0**2',Tg='3*H0**2/(8*pi),0,0,0; 0,-3*H0**2/(8*pi)*cosh(H0*t)**2/(H0**2*(1-r**2)),0,0; 0,0,-3*H0**2/(8*pi)*cosh(H0*t)**2*r**2/H0**2,0; 0,0,0,-3*H0**2/(8*pi)*cosh(H0*t)**2*r**2*sin(theta)**2/H0**2',Tf_mode='same',point='r=0.5, t=0.5, theta=1, H0=0.1')
    PRESETS['FLRW open (k=-1, de Sitter, explicit)']=dict(D,g='-1,0,0,0; 0,sinh(H0*t)**2/(H0**2*(1+r**2)),0,0; 0,0,sinh(H0*t)**2*r**2/H0**2,0; 0,0,0,sinh(H0*t)**2*r**2*sin(theta)**2/H0**2',Tg='3*H0**2/(8*pi),0,0,0; 0,-3*H0**2/(8*pi)*sinh(H0*t)**2/(H0**2*(1+r**2)),0,0; 0,0,-3*H0**2/(8*pi)*sinh(H0*t)**2*r**2/H0**2,0; 0,0,0,-3*H0**2/(8*pi)*sinh(H0*t)**2*r**2*sin(theta)**2/H0**2',Tf_mode='same',point='r=0.5, t=1, theta=1, H0=0.1')
    PRESETS['FLRW flat (de Sitter, explicit)']=dict(D,g='-1,0,0,0; 0,exp(2*H0*t),0,0; 0,0,exp(2*H0*t)*r**2,0; 0,0,0,exp(2*H0*t)*r**2*sin(theta)**2',Tg='3*H0**2/(8*pi),0,0,0; 0,-3*H0**2/(8*pi)*exp(2*H0*t),0,0; 0,0,-3*H0**2/(8*pi)*exp(2*H0*t)*r**2,0; 0,0,0,-3*H0**2/(8*pi)*exp(2*H0*t)*r**2*sin(theta)**2',Tf_mode='same',point='r=1, t=1, theta=1, H0=0.1')
    # Explicit Friedmann-satisfying FLRW: S, rho, p are NOT free here, they satisfy Friedmann, so EE must be SATISFIED for both g and f.
    # Flat matter-dominated: S=t**(2/3), H=2/(3t), rho=3H^2/(8pi)=1/(6 pi t^2), p=0.
    PRESETS['FLRW flat matter-dominated (Friedmann, explicit)']=dict(D,g='-1,0,0,0; 0,t**(4/3),0,0; 0,0,t**(4/3)*r**2,0; 0,0,0,t**(4/3)*r**2*sin(theta)**2',Tg='1/(6*pi*t**2),0,0,0; 0,0,0,0; 0,0,0,0; 0,0,0,0',Tf_mode='same',point='r=1, t=2, theta=1')
    # Flat radiation-dominated: S=t**(1/2), H=1/(2t), rho=3H^2/(8pi)=3/(32 pi t^2), p=rho/3.
    PRESETS['FLRW flat radiation-dominated (Friedmann, explicit)']=dict(D,g='-1,0,0,0; 0,t,0,0; 0,0,t*r**2,0; 0,0,0,t*r**2*sin(theta)**2',Tg='3/(32*pi*t**2),0,0,0; 0,t*(1/(32*pi*t**2)),0,0; 0,0,t*r**2*(1/(32*pi*t**2)),0; 0,0,0,t*r**2*sin(theta)**2*(1/(32*pi*t**2))',Tf_mode='same',point='r=1, t=2, theta=1')
    PRESETS['einstein static universe']=dict(D,g='-1,0,0,0; 0,1/(1-r**2),0,0; 0,0,r**2,0; 0,0,0,r**2*sin(theta)**2',Tg='3/(8*pi),0,0,0; 0,-1/(8*pi*(1-r**2)),0,0; 0,0,-r**2/(8*pi),0; 0,0,0,-r**2*sin(theta)**2/(8*pi)',Tf_mode='same',point='r=0.5, t=1, theta=1')
    PRESETS['godel (rotating dust)']=dict(D,coords='t,x,y,z',eta_preset='cartesian',g='-1,0,-exp(x),0; 0,1,0,0; -exp(x),0,-exp(2*x)/2,0; 0,0,0,1',Tg='1/(16*pi),0,exp(x)/(16*pi),0; 0,1/(16*pi),0,0; exp(x)/(16*pi),0,3*exp(2*x)/(32*pi),0; 0,0,0,1/(16*pi)',Tf_mode='same',point='x=0, t=1, y=0, z=0')
    PRESETS['kasner (vacuum anisotropic)']=dict(D,coords='t,x,y,z',eta_preset='cartesian',g='-1,0,0,0; 0,t**(2*p1),0,0; 0,0,t**(2*p2),0; 0,0,0,t**(2*p3)',Tg='0,0,0,0; 0,0,0,0; 0,0,0,0; 0,0,0,0',Tf_mode='vacuum',point='t=2, x=2, y=0, z=0, p1=0.6666666667, p2=0.6666666667, p3=-0.3333333333')
    PRESETS['vaidya (radiating)']=dict(D,coords='v,r,theta,phi',g='-(1-2*M(v)/r),1,0,0; 1,0,0,0; 0,0,r**2,0; 0,0,0,r**2*sin(theta)**2',Tg='Derivative(M(v),v)/(4*pi*r**2),0,0,0; 0,0,0,0; 0,0,0,0; 0,0,0,0',Tf_mode='same',point='r=3, v=1, theta=1')
    PRESETS['schwarzschild eddington-finkelstein']=dict(D,coords='v,r,theta,phi',g='-(1-r_s/r),1,0,0; 1,0,0,0; 0,0,r**2,0; 0,0,0,r**2*sin(theta)**2',Tg='0,0,0,0; 0,0,0,0; 0,0,0,0; 0,0,0,0',Tf_mode='vacuum',point='r=3, v=1, r_s=1, theta=1')
    PRESETS['schwarzschild painleve-gullstrand']=dict(D,coords='T,r,theta,phi',g='-(1-r_s/r),sqrt(r_s/r),0,0; sqrt(r_s/r),1,0,0; 0,0,r**2,0; 0,0,0,r**2*sin(theta)**2',Tg='0,0,0,0; 0,0,0,0; 0,0,0,0; 0,0,0,0',Tf_mode='vacuum',point='r=3, T=1, r_s=1, theta=1')
    PRESETS['morris-thorne wormhole (exotic)']=dict(D,g='-1,0,0,0; 0,1/(1-r0/r),0,0; 0,0,r**2,0; 0,0,0,r**2*sin(theta)**2',Tg='0,0,0,0; 0,r0/(8*pi*r**2*(-r+r0)),0,0; 0,0,r0/(16*pi*r),0; 0,0,0,r0*sin(theta)**2/(16*pi*r)',Tf_mode='same',point='r=3, t=1, r0=1, theta=1')
    PRESETS['alcubierre warp (metric only, exotic)']=dict(D,coords='t,x,y,z',eta_preset='cartesian',g='-(1-vs**2*exp(-2*((x-vs*t)**2+y**2+z**2)/Rwarp**2)),-vs*exp(-((x-vs*t)**2+y**2+z**2)/Rwarp**2),0,0; -vs*exp(-((x-vs*t)**2+y**2+z**2)/Rwarp**2),1,0,0; 0,0,1,0; 0,0,0,1',Tg='',Tf_mode='vacuum',point='t=1, x=0, y=0, z=0, vs=1, Rwarp=2')
    PRESETS['cosmic string (deficit angle)']=dict(D,coords='t,r,theta,z',g='-1,0,0,0; 0,1,0,0; 0,0,(1-4*mu)**2*r**2,0; 0,0,0,1',Tg='0,0,0,0; 0,0,0,0; 0,0,0,0; 0,0,0,0',Tf_mode='vacuum',point='r=2, t=1, theta=1, z=0, mu=0.01')
    PRESETS['BTZ (2+1 black hole)']=dict(D,coords='t,r,phi',eta_preset='cartesian',g='-(r**2/l**2-Mbtz),0,-J/2; 0,1/(r**2/l**2-Mbtz+J**2/(4*r**2)),0; -J/2,0,r**2',Tg='-(r**2/l**2-Mbtz)/(8*pi*l**2),0,-J/(16*pi*l**2); 0,1/(8*pi*l**2*(r**2/l**2-Mbtz+J**2/(4*r**2))),0; -J/(16*pi*l**2),0,r**2/(8*pi*l**2)',Tf_mode='same',vg='1,0,0',vf='0,1,0',point='r=3, t=1, phi=0, Mbtz=1, J=0.5, l=1')
    PRESETS['nariai (dS x S2)']=dict(D,g='-(1-Lambda*r**2),0,0,0; 0,1/(1-Lambda*r**2),0,0; 0,0,1/Lambda,0; 0,0,0,sin(theta)**2/Lambda',Tg='Lambda*(1-Lambda*r**2)/(8*pi),0,0,0; 0,-Lambda/(8*pi*(1-Lambda*r**2)),0,0; 0,0,-1/(8*pi),0; 0,0,0,-sin(theta)**2/(8*pi)',Tf_mode='same',point='r=1, t=1, Lambda=0.1, theta=1')
    PRESETS['bertotti-robinson (AdS2 x S2, EM)']=dict(D,g='-(1+r**2),0,0,0; 0,1/(1+r**2),0,0; 0,0,1,0; 0,0,0,sin(theta)**2',Tg='(1+r**2)/(8*pi),0,0,0; 0,-1/(8*pi*(1+r**2)),0,0; 0,0,1/(8*pi),0; 0,0,0,sin(theta)**2/(8*pi)',Tf_mode='same',point='r=1, t=1, theta=1')
    PRESETS['mcvittie (BH in de Sitter FLRW, isotropic)']=dict(D,coords='t,R,theta,phi',eta_preset='cartesian',g='-((1-m/(2*exp(H0*t)*R))/(1+m/(2*exp(H0*t)*R)))**2,0,0,0; 0,exp(2*H0*t)*(1+m/(2*exp(H0*t)*R))**4,0,0; 0,0,exp(2*H0*t)*(1+m/(2*exp(H0*t)*R))**4*R**2,0; 0,0,0,exp(2*H0*t)*(1+m/(2*exp(H0*t)*R))**4*R**2*sin(theta)**2',Tg='3*H0**2/(8*pi)*((1-m/(2*exp(H0*t)*R))/(1+m/(2*exp(H0*t)*R)))**2,0,0,0; 0,-3*H0**2/(8*pi)*exp(2*H0*t)*(1+m/(2*exp(H0*t)*R))**4,0,0; 0,0,-3*H0**2/(8*pi)*exp(2*H0*t)*(1+m/(2*exp(H0*t)*R))**4*R**2,0; 0,0,0,-3*H0**2/(8*pi)*exp(2*H0*t)*(1+m/(2*exp(H0*t)*R))**4*R**2*sin(theta)**2',Tf_mode='same',point='R=3, t=1, m=0.5, theta=1, H0=0.1')
    PRESETS['c-metric (accelerating BH, exact)']=dict(D,coords='t,y,x,phi',eta_preset='cartesian',g='-(-1+y**2-2*m*Aacc*y**3)/(Aacc**2*(x+y)**2),0,0,0; 0,1/(Aacc**2*(x+y)**2*(-1+y**2-2*m*Aacc*y**3)),0,0; 0,0,1/(Aacc**2*(x+y)**2*(1-x**2-2*m*Aacc*x**3)),0; 0,0,0,(1-x**2-2*m*Aacc*x**3)/(Aacc**2*(x+y)**2)',Tg='0,0,0,0; 0,0,0,0; 0,0,0,0; 0,0,0,0',Tf_mode='vacuum',point='t=1, y=2, x=0, phi=0, m=0.5, Aacc=0.01')
    PRESETS['de sitter planar (inflation)']=dict(D,coords='t,x,y,z',eta_preset='cartesian',g='-1,0,0,0; 0,exp(2*H0*t),0,0; 0,0,exp(2*H0*t),0; 0,0,0,exp(2*H0*t)',Tg='3*H0**2/(8*pi),0,0,0; 0,-exp(2*H0*t)*3*H0**2/(8*pi),0,0; 0,0,-exp(2*H0*t)*3*H0**2/(8*pi),0; 0,0,0,-exp(2*H0*t)*3*H0**2/(8*pi)',Tf_mode='same',point='t=1, x=0, y=0, z=0, H0=0.1')
    PRESETS['taub-nut (vacuum, NUT charge)']=dict(D,g='-(r**2-2*m*r-n**2)/(r**2+n**2),0,0,2*n*cos(theta)*(r**2-2*m*r-n**2)/(r**2+n**2); 0,(r**2+n**2)/(r**2-2*m*r-n**2),0,0; 0,0,r**2+n**2,0; 2*n*cos(theta)*(r**2-2*m*r-n**2)/(r**2+n**2),0,0,(r**2+n**2)*sin(theta)**2-4*n**2*cos(theta)**2*(r**2-2*m*r-n**2)/(r**2+n**2)',Tg='0,0,0,0; 0,0,0,0; 0,0,0,0; 0,0,0,0',Tf_mode='vacuum',opt_K='',point='r=3, t=1, m=0.5, n=0.3, theta=1')
    PRESETS['schwarzschild isotropic coords']=dict(D,coords='t,R,theta,phi',eta_preset='cartesian',g='-((1-r_s/(4*R))/(1+r_s/(4*R)))**2,0,0,0; 0,(1+r_s/(4*R))**4,0,0; 0,0,(1+r_s/(4*R))**4*R**2,0; 0,0,0,(1+r_s/(4*R))**4*R**2*sin(theta)**2',Tg='0,0,0,0; 0,0,0,0; 0,0,0,0; 0,0,0,0',Tf_mode='vacuum',point='R=3, t=1, r_s=1, theta=1')
_add()

# Highlighted presets: metrics behind the well-established tests of GR, and metrics
# behind the dark-matter / dark-energy explanations. Dark matter / dark energy are
# NOT tests - they are explanations of observed data. Each entry says which term does it.
HIGHLIGHTS = {
 'schwarzschild (vacuum)': dict(badge='GR TEST + DARK MATTER', kind='gr-test',
   why='The classic GR tests: Mercury perihelion precession (43 arcsec/century), light bending by the Sun (1.75 arcsec), Shapiro time delay, and gravitational redshift. In the weak-field limit the same metric gives galaxy rotation curves: v^2 = GM(r)/r. Observed curves stay flat where visible mass ends, so M(r) must keep growing - that is the dark-matter inference. Schwarzschild does not supply the halo; it shows extra mass is needed.',
   term='The factor (1 - r_s/r) in g_tt = -(1 - r_s/r) and g_rr = 1/(1 - r_s/r), with r_s = 2GM/c^2. Perihelion, bending and Shapiro all come from expanding this factor; the Newtonian limit v^2 = GM(r)/r comes from the same factor.'),
 'schwarzschild eddington-finkelstein': dict(badge='GR TEST', kind='gr-test',
   why='Same physical tests as Schwarzschild, in coordinates that stay regular at the horizon. It shows the horizon is a coordinate effect, not a curvature singularity.',
   term='The same (1 - r_s/r) in g_vv, plus the off-diagonal g_vr = 1. That cross term is what makes ingoing light fall through r = r_s smoothly.'),
 'schwarzschild painleve-gullstrand': dict(badge='GR TEST', kind='gr-test',
   why='Same physical tests as Schwarzschild, in the frame of a freely falling observer. It is the form used for infall, horizon crossing, and Hawking-radiation derivations.',
   term='g_TT = -(1 - r_s/r) and the cross term g_Tr = +sqrt(r_s/r). The cross term is the infall speed sqrt(r_s/r) of a freely falling observer.'),
 'schwarzschild isotropic coords': dict(badge='GR TEST', kind='gr-test',
   why='Same physical tests as Schwarzschild, in the coordinates used for the PPN / weak-field comparison with solar-system data.',
   term='The factor ((1 - r_s/(4R))/(1 + r_s/(4R)))^2 in g_tt. Expanding it gives the PPN parameters gamma = beta = 1.'),
 'kerr (rotating vacuum)': dict(badge='GR TEST', kind='gr-test',
   why='Frame dragging / Lense-Thirring precession, measured by Gravity Probe B and by LAGEOS satellites, and the geodetic precession of gyroscopes in orbit. Also the spin of astrophysical black holes.',
   term='The off-diagonal g_tphi = -r_s a r sin^2(theta)/Sigma, with Sigma = r^2 + a^2 cos^2(theta) and a = J/M the spin. With a = 0 this term vanishes and Kerr reduces to Schwarzschild.'),
 'FLRW flat matter-dominated (Friedmann, explicit)': dict(badge='GR TEST + DARK MATTER', kind='gr-test',
   why='A GR test of cosmic expansion: the Hubble law, the age of the Universe, and the growth of structure. It is also the dark-matter case: the CMB acoustic peaks, galaxy clustering, lensing and rotation curves cannot be fitted with visible matter alone. About 85% of the matter in rho(t) must be dark.',
   term='S(t) = t^(2/3) and rho(t) = 1/(6 pi t^2), p = 0. The t^(2/3) expansion law is the Friedmann solution for a matter-dominated universe; rho(t) is the total matter density, visible + dark.'),
 'FLRW flat radiation-dominated (Friedmann, explicit)': dict(badge='GR TEST', kind='gr-test',
   why='A GR test of the early Universe: Big Bang nucleosynthesis (light-element abundances) and the CMB. Radiation domination is what sets the expansion rate during nucleosynthesis.',
   term='S(t) = t^(1/2) and rho(t) = 3/(32 pi t^2), p = rho/3. The t^(1/2) law and p = rho/3 are the radiation equation of state.'),
 'schwarzschild-de Sitter (Kottler)': dict(badge='DARK ENERGY + GR TEST', kind='dark-energy',
   why='Not a test of GR alone - it is the dark-energy explanation: Type Ia supernovae show the expansion is accelerating. Locally it still gives the Schwarzschild solar-system tests; at large r the Lambda term takes over and gives repulsion. That is why the same metric covers both regimes.',
   term='The term -Lambda r^2/3 inside (1 - r_s/r - Lambda r^2/3). The r_s/r part gives the local tests; the -Lambda r^2/3 part gives cosmic acceleration, with Lambda > 0.'),
 'de sitter planar (inflation)': dict(badge='DARK ENERGY', kind='dark-energy',
   why='Not a test - it is the dark-energy / inflation explanation: exponential expansion, used both for cosmic inflation in the early Universe and for the present accelerated expansion driven by Lambda.',
   term='The factor exp(2 H0 t) in the spatial metric, with H0^2 = Lambda/3 and rho_Lambda = 3 H0^2/(8 pi). The exponential, not a power law, is the signature of Lambda domination; the pressure is p = -rho.'),
 'FLRW closed (k=+1, de Sitter, explicit)': dict(badge='DARK ENERGY', kind='dark-energy',
   why='Not a test - the dark-energy explanation in a closed universe: with Lambda domination the expansion accelerates, and the closed geometry is carried along by the de Sitter expansion.',
   term='S(t) = cosh(H0 t)/H0 and p = -rho, rho = 3 H0^2/(8 pi). The cosh and the negative pressure are the Lambda signature.'),
 'FLRW open (k=-1, de Sitter, explicit)': dict(badge='DARK ENERGY', kind='dark-energy',
   why='Not a test - the dark-energy explanation in an open universe: same Lambda-driven acceleration as the flat case, with negative spatial curvature.',
   term='S(t) = sinh(H0 t)/H0 and p = -rho, rho = 3 H0^2/(8 pi). The sinh and the negative pressure are the Lambda signature.'),
 'FLRW flat (de Sitter, explicit)': dict(badge='DARK ENERGY', kind='dark-energy',
   why='Not a test - the dark-energy explanation in a flat universe: the present accelerated expansion, fitted by Lambda in the Friedmann equation.',
   term='S(t) = exp(H0 t) and p = -rho, rho = 3 H0^2/(8 pi). The exponential expansion is the Lambda signature.'),
}
