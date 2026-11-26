from dual_general_relativity import analyze
from dual_general_relativity.presets import PRESETS
def test_schwarzschild_vacuum():
    r=analyze(dict(PRESETS["schwarzschild (vacuum)"]))
    d={n:ok for n,ok,k in r["checks"]}
    assert d["EE satisfied for g: G - kappa*Tg = 0 ?"] is True
    assert d["EE satisfied for f: G - kappa*Tf = 0 ?"] is True
def test_tf_same():
    r=analyze(dict(PRESETS["schwarzschild pair flavour (Tf = Tg)"]))
    assert (r["raw"]["Tf"]==r["raw"]["Tg"])
