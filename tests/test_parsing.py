"""Tests for parsing helpers."""

from __future__ import annotations

import pytest

from tests.input_parsers import parse_equation, parse_variables
from uncertainty_calculator import Equation, Variable
from uncertainty_calculator.parsing import parse_inputs


def test_parse_equation_trims_and_builds_dataclass():
    """Whitespace should be stripped when building Equation."""
    raw = ["  A  ", "  B + C  "]
    equation = parse_equation(raw)
    assert equation.lhs == "A"
    assert equation.rhs == "B + C"


def test_parse_equation_invalid_length_raises():
    """Invalid equation length should raise ValueError."""
    with pytest.raises(ValueError):
        parse_equation(["only-one-side"])


def test_parse_variables_parses_value_and_uncertainty():
    """Legacy tuple definitions should convert to Variable dataclasses."""
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
    """Bad legacy variable definitions should be rejected."""
    with pytest.raises(ValueError):
        parse_variables([("invalid", "x")])


def test_parsing_rejects_duplicate_variable_names():
    """Duplicate variable names should raise a ValueError."""
    equation = Equation(lhs="y", rhs="x + z")
    variables = [
        Variable(name="x", value=1, uncertainty=0.1, latex_name="x"),
        Variable(name="x", value=2, uncertainty=0.2, latex_name="x_dup"),
    ]
    with pytest.raises(ValueError, match="Duplicate variable name detected"):
        parse_inputs(equation, variables)
