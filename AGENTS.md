# UncertaintyCalculator Agent Guide

## Project Mission

- Convert an input equation and variable measurements into LaTeX that shows:
  - evaluated central value (`mu`)
  - uncertainty propagation (`sigma`)
  - optional derivative/substitution steps

## Core Pipeline (Do Not Bypass)

1. `parse_inputs()` in `src/uncertainty_calculator/parsers.py`
2. `validate_inputs()` in `src/uncertainty_calculator/validation.py`
3. `compute()` in `src/uncertainty_calculator/compute.py`
4. `render_output()` in `src/uncertainty_calculator/render.py`

Keep logic in the right layer. Prefer extending an existing stage over mixing concerns across modules.

## Public API Stability

- Preserve behavior and signatures of:
  - `Equation`, `Variable`, `Digits`
  - `UncertaintyCalculator` and `UncertaintyCalculator.run()`
- Keep exports in `src/uncertainty_calculator/__init__.py` consistent.

## Module Ownership

- `parsers.py`: normalize and map inputs into SymPy-friendly structures.
- `validation.py`: reject undefined or invalid symbolic references.
- `compute.py`: derivatives and numeric uncertainty propagation.
- `render.py`: LaTeX structure/format (combined vs separate, insert vs non-insert).
- `format.py`: SymPy-to-LaTeX helper wrappers only.

## Change Rules

- Maintain parity-sensitive output behavior unless explicitly changing product behavior.
- When changing rendering/computation, add or update focused tests in `tests/`.
- Keep tests deterministic and aligned with legacy parity expectations (`tests/legacy_calculator.py`).

## Local Validation Workflow

Always activate the project environment before running commands:

```bash
source .venv/bin/activate
pre-commit run --all-files
pytest -n auto --dist=loadscope tests/
```

Use Python 3.12 assumptions from `pyproject.toml`.
