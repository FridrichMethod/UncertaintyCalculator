import sys
from pathlib import Path

import pytest

# Ensure we import the package, not the script in root
# We renamed the script to main.py, so the conflict is gone, but we still want to ensure src/ is in path if not installed.

root_path = Path(__file__).parent.parent.resolve()
src_path = str(root_path / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from tests.legacy_calculator import run_legacy_calculator
from uncertainty_calculator import UncertaintyCalculator

# Define equation
equation = [x.strip() for x in [r"\zeta ", r" (K*pi*eta*u*l)/(4*pi*phi*e_0*e_r)"]]

# Define variable
variable = [
    ("K = 4 +- 0", r"K"),
    ("eta = 0.9358e-3 +- 0.0001/sqrt(3)", r"\eta"),
    ("u = 3.68e-5 +- 0.11e-5", r"u"),
    ("l = 0.2256 +- 0.0019", r"l"),
    ("phi = 100 +- 1/sqrt(3)", r"\varphi"),
    ("e_0 = 8.8541878128e-12 +- 0", r"\varepsilon_0"),
    ("e_r = 78.7 +- 0.1/sqrt(3)", r"\varepsilon_\text{r}"),
]


@pytest.mark.parametrize("result_digit_mu", [2, 3])
@pytest.mark.parametrize("result_digit_sigma", [2, 3])
@pytest.mark.parametrize("result_unit", [r"\si{V}", 1])
@pytest.mark.parametrize("separate", [0, 1])
@pytest.mark.parametrize("insert", [0, 1])
@pytest.mark.parametrize("include_equation_number", [0, 1])
def test_calculator_output_matches_legacy(
    result_digit_mu, result_digit_sigma, result_unit, separate, insert, include_equation_number
):
    # Prepare inputs
    result_digit = {
        "mu": result_digit_mu,
        "sigma": result_digit_sigma,
    }

    # Run Legacy (Oracle)
    expected_output = run_legacy_calculator(
        result_digit=result_digit,
        result_unit=result_unit,
        separate=separate,
        insert=insert,
        include_equation_number=include_equation_number,
    )

    # Run Refactored
    calculator = UncertaintyCalculator(
        equation=equation,
        variable=variable,
        result_digit=result_digit,
        result_unit=result_unit,
        separate=separate,
        insert=insert,
        include_equation_number=include_equation_number,
    )
    actual_output = calculator.run()

    assert actual_output == expected_output
