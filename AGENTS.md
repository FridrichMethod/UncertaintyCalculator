# UncertaintyCalculator agent guide

Instructions for every coding agent (Codex, Cursor, Copilot, Claude Code) working in this repository. Claude Code imports this file through `CLAUDE.md`.

## Project Mission

- Convert an input equation and variable measurements into LaTeX that shows:
  - evaluated central value (`mu`)
  - uncertainty propagation (`sigma`)
  - optional derivative/substitution steps

## Local Validation Workflow

Always activate the project environment before running commands:

```bash
source .venv/bin/activate
pre-commit run --all-files
pytest -n auto --dist=loadscope tests/
```

Use Python 3.12 assumptions from `pyproject.toml`.

## Core Pipeline (Do Not Bypass)

1. `parse_inputs()` in `src/uncertainty_calculator/parsers.py`
2. `validate_inputs()` in `src/uncertainty_calculator/validation.py`
3. `compute()` in `src/uncertainty_calculator/compute.py`
4. `render_output()` in `src/uncertainty_calculator/render.py`

Keep logic in the right layer. Prefer extending an existing stage over mixing concerns across modules.

- Do not place rendering logic in compute/parsing.
- Do not place symbolic math logic in rendering.

## Public API Stability

- Preserve behavior and signatures of:
  - `Equation`, `Variable`, `Digits`
  - `UncertaintyCalculator` and `UncertaintyCalculator.run()`
- Preserve the dataclass API in `src/uncertainty_calculator/_types.py`.
- Preserve orchestration contract in `src/uncertainty_calculator/calculator.py`.
- Keep exports in `src/uncertainty_calculator/__init__.py` consistent.

## Module Ownership

- `parsers.py`: normalize and map inputs into SymPy-friendly structures.
- `validation.py`: reject undefined or invalid symbolic references.
- `compute.py`: derivatives and numeric uncertainty propagation.
- `render.py`: LaTeX structure/format (combined vs separate, insert vs non-insert).
- `format.py`: SymPy-to-LaTeX helper wrappers only.

## Change Rules

- Maintain parity-sensitive output behavior unless explicitly changing product behavior.
- Treat output format as regression-sensitive; tests compare against legacy behavior.
- When changing rendering/computation, add or update focused tests in `tests/`.
- Update/add tests under `tests/` for any behavior change.
- Keep targeted unit tests close to changed module.
- Keep tests deterministic and aligned with legacy parity expectations (`tests/legacy_calculator.py`).
