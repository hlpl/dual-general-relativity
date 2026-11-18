"""Smoke tests: Minkowski must pass both sectors; interior (Fast) must pass g, N/A f."""
import sys, types

def _load_server():
    flask = types.ModuleType("flask")
    class FakeFlask:
        def __init__(self, *a, **k): pass
        def route(self, *a, **k):
            def deco(f): return f
            return deco
        def run(self, *a, **k): pass
    flask.Flask = FakeFlask
    flask.render_template_string = lambda *a, **k: ""
    flask.request = types.SimpleNamespace()
    flask.jsonify = lambda **k: k
    sys.modules["flask"] = flask
    from dual_general_relativity import server as m
    return m

def test_minkowski():
    m = _load_server()
    res = m.staged_compute(dict(m.PRESETS["minkowski"]), lambda p, l: None)
    checks = dict(res["checks"])
    assert checks.get("\\varepsilon^{(g)}=0 (N/A if T^{(g)} unknown)") is True
    assert checks.get("\\varepsilon^{(f)}=0 (N/A if T^{(f)} unknown)") is True

def test_interior_fast():
    m = _load_server()
    form = dict(m.PRESETS["interior"]); form["compute_mode"] = "fast"
    res = m.staged_compute(form, lambda p, l: None)
    checks = dict(res["checks"])
    assert checks.get("\\varepsilon^{(g)}=0 (N/A if T^{(g)} unknown)") is True
    assert checks.get("\\varepsilon^{(f)}=0 (N/A if T^{(f)} unknown)") is None
    assert "rho^{(f)}_{imp}" in res["numeric"]
# v1.0.2
