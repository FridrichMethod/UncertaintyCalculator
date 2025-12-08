"""Test suite for Uncertainty Calculator."""

import pytest

from tests.input_parsers import parse_equation, parse_variables
from tests.legacy_calculator import run_legacy_calculator
from uncertainty_calculator import Digits, UncertaintyCalculator

# Default test case data
default_equation = [x.strip() for x in [r"\zeta ", r" (K*pi*eta*u*l)/(4*pi*phi*e_0*e_r)"]]
default_variables = [
    ("K = 4 +- 0", r"K"),
    ("eta = 0.9358e-3 +- 0.0001/sqrt(3)", r"\eta"),
    ("u = 3.68e-5 +- 0.11e-5", r"u"),
    ("l = 0.2256 +- 0.0019", r"l"),
    ("phi = 100 +- 1/sqrt(3)", r"\varphi"),
    ("e_0 = 8.8541878128e-12 +- 0", r"\varepsilon_0"),
    ("e_r = 78.7 +- 0.1/sqrt(3)", r"\varepsilon_\text{r}"),
]

# Extended Test Case 1: From README
readme_equation = [x.strip() for x in [r"W ", r" (-Q_V*m-Q_N-Q_M)/Dt-rho*V*C"]]
readme_variables = [
    ("Q_V = -26.414 +- 0", r"Q_V"),
    ("m = 0.9547 +- 0.0004/sqrt(3)", r"m"),
    ("Q_N = -0.323 +- 3.243*0.0004/sqrt(3)", r"Q_\ce{Ni}"),
    ("Q_M = -0.01 +- 0.0002*16.736/sqrt(3)", r"Q_\text{cotton}"),
    ("rho = 0.99865 +- 0", r"\rho_\ce{H2O}"),
    ("V = 3000 +- 0.01", r"V"),
    ("C = 4.1824e-3 +- 0", r"C_\ce{H2O}"),
    ("Dt = 1.770 +- 0.009", r"\Delta T"),
]

# Extended Test Case 2: Simple Linear
linear_equation = ["y", "m*x + b"]
linear_variables = [
    ("m = 2.5 +- 0.1", "m"),
    ("x = 4.0 +- 0.2", "x"),
    ("b = 1.0 +- 0.5", "b"),
]

# Extended Test Case 3: Power Law
power_equation = ["E", "0.5 * m * v**2"]
power_variables = [
    ("m = 10.0 +- 0.5", "m"),
    ("v = 5.0 +- 0.1", "v"),
]

# Test Data Collection
test_cases = [
    ("default", default_equation, default_variables),
    ("readme", readme_equation, readme_variables),
    ("linear", linear_equation, linear_variables),
    ("power", power_equation, power_variables),
]


@pytest.mark.parametrize("case_name, equation, variables", test_cases)
@pytest.mark.parametrize("digits", [Digits(mu=3, sigma=2), Digits(mu=4, sigma=3)])
@pytest.mark.parametrize("last_unit", [r"\text{V}", "", None])
@pytest.mark.parametrize("separate", [True, False])
@pytest.mark.parametrize("insert", [True, False])
@pytest.mark.parametrize("include_equation_number", [True, False])
def test_calculator_output_matches_legacy(
    case_name,
    equation,
    variables,
    digits,
    last_unit,
    separate,
    insert,
    include_equation_number,
):
    """Test that the refactored calculator matches the legacy implementation."""
    print(f"Running test case: {case_name}")

    # Run Legacy (Oracle) with injected equation/variables
    # Keep legacy format for legacy calculator
    expected_output = run_legacy_calculator(
        equation=equation,
        variables=variables,
        digits=digits,
        last_unit=last_unit,
        separate=separate,
        insert=insert,
        include_equation_number=include_equation_number,
    )

    # Convert inputs to new format for new calculator
    new_equation = parse_equation(equation)
    new_variables = parse_variables(variables)

    # Run Refactored
    calculator = UncertaintyCalculator(
        equation=new_equation,
        variables=new_variables,
        digits=digits,
        last_unit=last_unit,
        separate=separate,
        insert=insert,
        include_equation_number=include_equation_number,
    )
    actual_output = calculator.run()

    assert actual_output == expected_output
