from .compute import swap_metric, curvature, geodesic_acceleration, schwarzschild_pair_events
from .engine import analyze
__version__ = "2.0.0"
__all__=["analyze","swap_metric","curvature","geodesic_acceleration","schwarzschild_pair_events","create_app","main"]
def __getattr__(name):
    if name in ("create_app","main"):
        from .server import create_app, main
        return {"create_app": create_app, "main": main}[name]
    raise AttributeError(name)
