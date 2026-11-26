# Dual General Relativity (DGR) 

**Two metrics. One manifold. You bring the metric, it does the algebra.**

DGR is a local web app that computes what a second, companion metric implies —
given a metric you already trust from general relativity. It proves nothing and
selects nothing. It computes, checks, and shows its work.

> ⚠️ **Local use only.** The app runs `sympify` on text you type. Never expose it
> to the internet. Run it on your own machine, with your own inputs.

---

## The model in 30 seconds

You give it a metric `g` — the physical GR metric. The app builds a companion
metric `f` by a **coordinate swap**:

```
φ swaps x⁰ ↔ x¹
f = ε · φ*g        ε = +1 or −1, your choice
```

`f` gets **its own renamed parameters** (`r_s → r_t`, `a → a_t`,
`Λ → Λ_t`, `ρ → ρ_t`, …), so `g` and `f` are genuinely two different
geometries on the same coordinates — not two copies of one metric.

Matter couples to `h = g + F(g)`, where `F(g)` is a slave field (`V = 0`, no
second graviton). `D` and `h` are shown as **information only** — the app never
solves for `f` from `D = 0`, and never treats `h` as the physical metric.

Then, for **both** `g` and `f`, the app computes the Einstein tensor `G`,
the residual `ε = G − κT`, the geodesic accelerations, and checks:

```
EE satisfied?   ε = G − κT = 0 ?
```

If `g` passes and `Tᶠ` is the swapped `Tᵍ` with renamed parameters, then `f`
must pass too. If it doesn’t, that’s a preset bug or a code bug — the check is
never forced to pass. The app never sets `T := G/κ` to manufacture a pass
(Alcubierre is the one exception: there that *is* the literature definition,
and it is labelled metric-only).

---

## What you get from one Compute

| Output | What it is |
|---|---|
| `f_μν` | Companion metric, swap-built, own parameters |
| `Tᶠ_μν` | Companion stress-energy, per the Tᶠ rule below |
| `G_μν[g]`, `G_μν[f]` | Einstein tensors of both metrics |
| `ε[g]`, `ε[f]` | Residuals `G − κT`, shown explicitly |
| Geodesic accelerations | `d²r/dt²`, … for both metrics, at your point |
| **EE checks** | `SATISFIED` / `NOT SATISFIED` for `g` and `f` |
| **Kretschmann `K`** | Curvature scalar, when ticked (slow — see Modes) |
| **Notes** | The app reads its own output: e.g. a `d²r/dt² = c·r` term is reported as *possibly explaining* expansion, with the responsible term named |
| **All tensors** | Every tensor, collapsible, one click per tensor |
| **Why this metric matters** | On highlighted presets: *why* it matters + *which term does it* |

---

## Quick start

```bash
git clone https://github.com/hlpl/dual-general-relativity.git
cd dual-general-relativity
chmod +x start.sh
./start.sh
# open http://127.0.0.1:5000 — hard refresh: Ctrl+Shift+R
```

`start.sh` kills any stale server on the port, clears `__pycache__`, creates
`.venv` if needed, and installs Flask + SymPy + NumPy **inside the venv only**.
No system pip, no sudo, nothing global.

Or as a library:

```python
from dual_general_relativity import analyze
from dual_general_relativity.presets import PRESETS

r = analyze(dict(PRESETS["schwarzschild (vacuum)"]))
for name, ok, _ in r["checks"]:
    print(name, ok)
```

---

## Presets — 32, not 8

The dropdown is grouped. ★ = highlighted, with a **Why this metric matters**
card below the output. Pick a preset, then change anything — a preset is just
a starting point, never a commitment.

**★ GR TESTS + DARK MATTER (highlighted)** — the metrics GR is actually tested
against, plus the ones dark matter is invoked to explain:
Schwarzschild (vacuum), Kerr, FLRW flat matter-dominated (Friedmann, explicit),
and more.

**★ DARK ENERGY (highlighted)** — the metrics dark energy is invoked to
explain: FLRW de Sitter variants, Einstein static universe, and more. These are
**explanations, not tests** — the card says so.

**OTHER METRICS** — Reissner–Nordström, Kerr–Newman, Gödel, Kasner, Vaidya,
BTZ, Morris–Thorne, Alcubierre (metric-only), cosmic string, Nariai,
Bertotti–Robinson, McVittie, C-metric, Taub–NUT, Schwarzschild interior
(constant density star), Schwarzschild in Eddington–Finkelstein,
Painlevé–Gullstrand, and isotropic coordinates, and more.

---

## The Tᶠ rule — read this before using the app

The companion stress-energy is **not** assumed. You choose:

| Rule | Meaning |
|---|---|
| **Same as Tᵍ** | `Tᶠ = φ*Tᵍ`, parameters renamed, **no** extra ε factor |
| **Vacuum** | `Tᶠ = 0` |
| **Set** | You type `Tᶠ` yourself — if left blank, it means vacuum |

Blank `Tᵍ` in a preset means *unknown*, not zero. Only an explicit zero matrix
or Vacuum mode means zero.

---

## Modes: Fast vs Normal

Toggle with the **Mode** button (top right, saved between visits). The note at
the bottom of the page opens and closes with a click.

| | Normal (default) | Fast |
|---|---|---|
| Simplification | Full: factor + cancel + together | Light: `together()` only |
| Kretschmann `K` | Computed if ticked | **Skipped** |
| EE check | Symbolic: `G − κT` simplified to exactly zero | Numeric: evaluated at your point |
| Use it when | You want the cleanest expressions | You want an answer in seconds |

Measured on Schwarzschild interior: **Normal ~39 s, Fast ~3 s**.
Kerr and Alcubierre stay slow in both modes (Kerr + Kretschmann: 10–40 min;
~60% of that is the curvature of `f`). That’s the algebra, not the app.

---

## The interface

- **White / Dark** toggle (top right, saved). White is the default.
- **Preset dropdown** starts on *“— pick a preset —”*. Every item selects,
  including the first one.
- **Results** sit full-width below the input panel. Equations are left-aligned
  and MathJax-rendered. Input labels are plain text, never MathJax.
- **Timer** (`MM:SS`) runs during every computation.
- **Notes** say *“may explain”*, never *“proves”* — they describe the computed
  terms, not a conclusion.

---

## Files

```
src/dual_general_relativity/
  server.py    Flask app, routes, HTML template, Mode/Theme toggles
  engine.py    analyze(): inputs → f, Tᶠ, G, ε, geodesics, EE checks, Notes
  compute.py   swap_metric, curvature, geodesic_acceleration, Fast/Normal paths
  presets.py   all 32 presets + the 12 highlighted explanations
  __init__.py  public API: analyze, swap_metric, curvature, ...
  __main__.py  `python -m dual_general_relativity`
tests/test_dgr.py   pytest: Schwarzschild EE for g and f, Tᶠ = Tᵍ pair flavour
start.sh           venv + server, kills stale servers, clears __pycache__
pyproject.toml / setup.py / setup.cfg   packaging (src layout)
requirements.txt   Flask, SymPy, NumPy
```

---

## Behaviour / limitations

- **Computation only.** No theorems, no model selection, no fitted parameters.
- **Exact values preserved.** The app never invents details or rounds your
  inputs away.
- **Only confirmed metrics.** The interior preset uses the constant-density
  star; non-symmetric fields requiring extra coordinates not present in the
  solution are excluded.
- **Exotic presets are labelled.** Morris–Thorne needs exotic matter,
  Alcubierre is metric-only — the app doesn’t hide that.
- **Kerr / Kerr–Newman are slow** (see Modes). Everything else is seconds.
- **Security:** `sympify` on user input is not sandboxed. Local use only.

---

## Version

**v2.0.0** — replaces the v1.x `f = 2η − g` model with the swap model. The old
model is still available under release **v1.0.2**. The change of model is why
this is a major version bump: v1 results do not reproduce under v2.

## License

MIT — see `LICENSE`.
