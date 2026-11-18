"""Dual General Relativity (DGR).

Constraint: 2 eta = g + f.  g is the input metric, f = 2 eta - g is the
companion.  GR: R[g] + S_g -> G[g] = 8 pi T(g).  DGR: R[f] + S_f -> G[f] = 8 pi T(f).
The two systems are separate; the constraint links solutions only.

T rule: blank = symbolic UNKNOWN, never 0.  T = 0 only when explicitly
written as a zero matrix, or when Vacuum mode is chosen.
"""
from .compute import compute_all, curvature_all, implied_T, mixed_T

__version__ = "1.0.2"
__all__ = ["compute_all", "curvature_all", "implied_T", "mixed_T", "create_app", "main"]

def __getattr__(name):
    # create_app / main need Flask, so import them lazily:
    # `import dual_general_relativity` works for library use without Flask.
    if name in ("create_app", "main"):
        from .server import create_app, main
        return {"create_app": create_app, "main": main}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
