# UncertaintyCalculator Claude Instructions

## What This Repository Does

Given:

- an equation (`lhs`, `rhs`)
- a list of variables (`name`, `value`, `uncertainty`, `latex_name`)

produce LaTeX that includes evaluated value and propagated uncertainty, plus optional intermediate steps.

## Implementation Boundaries

- Keep the pipeline order:
  - `parse_inputs` -> `validate_inputs` -> `compute` -> `render_output`
- Do not place rendering logic in compute/parsing.
- Do not place symbolic math logic in rendering.

## Key Compatibility Constraints

- Preserve the dataclass API in `src/uncertainty_calculator/_types.py`.
- Preserve orchestration contract in `src/uncertainty_calculator/calculator.py`.
- Treat output format as regression-sensitive; tests compare against legacy behavior.

## Where to Edit

- Parsing or symbol mapping changes: `parsers.py`
- Validation rules: `validation.py`
- Derivative or uncertainty math: `compute.py`
- LaTeX layout/output switches: `render.py`
- LaTeX helper options: `format.py`

## Test Discipline

- Update/add tests under `tests/` for any behavior change.
- Keep targeted unit tests close to changed module.
- Preserve legacy parity unless intentionally changing expected output.

## Commands

Activate `.venv` before running any project command:

```bash
source .venv/bin/activate
pre-commit run --all-files
pytest -n auto --dist=loadscope tests/
```
