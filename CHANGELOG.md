# Changelog

## 1.0.2

- FIX (critical): the 1.0.1 wheel contained NO Python files — only
  dist-info metadata and the console script. Cause: the Hatchling
  `packages = ["src/dual_general_relativity"]` config did not include the
  package in the wheel, so `pip install` succeeded but
  `import dual_general_relativity` raised ModuleNotFoundError. Switched the
  build backend to setuptools with `package-dir = {"" = "src"}`.
- FIX: `import dual_general_relativity` no longer pulls in Flask eagerly
  (lazy `create_app` / `main`); `server.py` uses `from . import compute`.
- FIX: `compute_all` crashed with `NameError: Gg` (`Gamma_g`).
- No physics / app changes.

## 1.0.1

- Superseded by 1.0.2 (wheel shipped without code — see above).

## 1.0.0

- First PyPI release (superseded).
