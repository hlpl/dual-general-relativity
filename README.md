# DGR Calculator v3 - computation only

Inputs: g, Tg, alpha, beta, gamma, epsilon (+ kappa, Tf rule, velocities).
Outputs: f, Tf, G[g], epsilon[g]=G-kappa*Tg, G[f], epsilon[f], d2x/dt2 for g, d2x/dr2 for f, EE satisfied? for g/f.

Run: ./start.sh  (creates .venv, installs deps, runs app)
Do NOT run `pip install -e .` by hand on system Python - use ./start.sh.

Tf rule: same (=Tg), vacuum (=0), set (=your matrix). Set-but-blank = vacuum.
Tg blank = vacuum.
Geodesic: d2x^mu/dlambda^2 = -Gamma^mu_ab v^a v^b, lambda=t for g, lambda=r for f.
No theorems, no selection - just computation.
