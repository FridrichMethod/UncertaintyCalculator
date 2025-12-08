"""Tests for input dataclasses and parsing helpers."""

import pytest

from tests.input_parsers import parse_equation, parse_variables
from uncertainty_calculator.core import Digits, Equation, UncertaintyCalculator, Variable


def test_variable_dataclass_input():
    """Test that Variable dataclass input is handled correctly."""
    # Using Equation object
    equation_obj = Equation(lhs=r"\zeta", rhs=r"K*x")

    # New dataclass input
    variables_obj = [
        Variable(name="K", value="2", uncertainty="0.1", latex_name="K"),
        Variable(name="x", value="3", uncertainty="0.2", latex_name="x"),
    ]

    digits = Digits(mu=2, sigma=2)

    # Should instantiate and run without error
    calc_obj = UncertaintyCalculator(
        equation=equation_obj,
        variables=variables_obj,
        digits=digits,
        last_unit=None,
        separate=False,
        insert=False,
        include_equation_number=False,
    )

    # Just checking it runs, result correctness checked in other tests
    assert isinstance(calc_obj.run(), str)


def test_missing_variable_validation():
    """Test that validation raises ValueError for missing variables."""
    equation = Equation(lhs="y", rhs="m*x + b")  # 'b' is missing
    variables = [
        Variable(name="m", value=1, uncertainty=0.1, latex_name="m"),
        Variable(name="x", value=2, uncertainty=0.1, latex_name="x"),
    ]
    digits = Digits(mu=2, sigma=2)

    calc = UncertaintyCalculator(
        equation=equation,
        variables=variables,
        digits=digits,
        last_unit="",
        separate=False,
        insert=False,
        include_equation_number=False,
    )

    with pytest.raises(ValueError, match="Symbol 'b' used in equation but not defined"):
        calc.run()


def test_mixed_input_types():
    """Test that numbers can be passed as float/int in Variable."""
    equation = Equation(lhs="y", rhs="x")
    variables = [Variable(name="x", value=10.5, uncertainty=0.5, latex_name="x")]
    digits = Digits(mu=2, sigma=2)

    calc = UncertaintyCalculator(
        equation=equation,
        variables=variables,
        digits=digits,
        last_unit="",
        separate=False,
        insert=False,
        include_equation_number=False,
    )

    # Should run without error
    calc.run()


def test_digits_dataclass_behaves_like_config():
    """Ensure Digits dataclass stores both fields."""
    digits = Digits(mu=4, sigma=5)
    assert digits.mu == 4
    assert digits.sigma == 5


def test_parse_equation_trims_and_builds_dataclass():
    """Parsing helper should strip whitespace and create Equation."""
    raw = ["  A  ", "  B + C  "]
    equation = parse_equation(raw)
    assert equation.lhs == "A"
    assert equation.rhs == "B + C"


def test_parse_equation_invalid_length_raises():
    """Parser should flag malformed equations."""
    with pytest.raises(ValueError):
        parse_equation(["only-one-side"])


def test_parse_variables_parses_value_and_uncertainty():
    """Parsing helper should convert legacy tuples into Variable objects."""
    raw = [
        ("X = 1 +- 0.1", "X"),
        ("Y = 2 +- 0.2", "Y"),
    ]
    variables = parse_variables(raw)
    assert [var.name for var in variables] == ["X", "Y"]
    assert variables[0].value == "1"
    assert variables[0].uncertainty == "0.1"
    assert variables[1].latex_name == "Y"


def test_parse_variables_invalid_definition():
    """Parser should reject invalid variable definitions."""
    with pytest.raises(ValueError):
        parse_variables([("invalid", "x")])
