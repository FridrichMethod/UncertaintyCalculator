"""Tests for validation helpers."""

from __future__ import annotations

import pytest

from uncertainty_calculator import Digits, Equation, UncertaintyCalculator, Variable


def test_missing_variable_validation():
    """Validation should fail when equation references undefined symbols."""

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

