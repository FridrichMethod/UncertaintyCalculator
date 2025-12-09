"""Tests for calculator orchestration."""

from __future__ import annotations

import pytest

from tests.conftest import RawCase
from tests.legacy_calculator import run_legacy_calculator
from uncertainty_calculator import Digits, Equation, UncertaintyCalculator, Variable


def test_calculator_output_matches_legacy(
    raw_case: RawCase,
    equation,
    variables,
    digits,
    last_unit,
    separate,
    insert,
    include_equation_number,
):
    """Refactored calculator should match the legacy implementation."""

    expected_output = run_legacy_calculator(
        equation=raw_case.equation,
        variables=raw_case.variables,
        digits=digits,
        last_unit=last_unit,
        separate=separate,
        insert=insert,
        include_equation_number=include_equation_number,
    )

    calculator = UncertaintyCalculator(
        equation=equation,
        variables=variables,
        digits=digits,
        last_unit=last_unit,
        separate=separate,
        insert=insert,
        include_equation_number=include_equation_number,
    )
    actual_output = calculator.run()

    assert actual_output == expected_output


def test_run_can_be_called_multiple_times_with_new_inputs():
    """Calculator should not leak state between runs when inputs change."""

    digits = Digits(mu=2, sigma=2)
    calc = UncertaintyCalculator(
        equation=Equation(lhs="y", rhs="x"),
        variables=[Variable(name="x", value=1, uncertainty=0.1, latex_name="x")],
        digits=digits,
        last_unit=None,
        separate=False,
        insert=False,
        include_equation_number=False,
    )

    first_output = calc.run()
    assert "\\sigma_{x}" in first_output

    calc.equation = Equation(lhs="y", rhs="m")
    calc.variables = [Variable(name="m", value=2, uncertainty=0.2, latex_name="m")]
    second_output = calc.run()

    assert "\\sigma_{m}" in second_output
    assert "\\sigma_{x}" not in second_output


def test_variable_dataclass_input():
    """Calculator should accept dataclass inputs and return a string output."""

    equation_obj = Equation(lhs=r"\zeta", rhs=r"K*x")
    variables_obj = [
        Variable(name="K", value="2", uncertainty="0.1", latex_name="K"),
        Variable(name="x", value="3", uncertainty="0.2", latex_name="x"),
    ]
    digits = Digits(mu=2, sigma=2)

    calc_obj = UncertaintyCalculator(
        equation=equation_obj,
        variables=variables_obj,
        digits=digits,
        last_unit=None,
        separate=False,
        insert=False,
        include_equation_number=False,
    )

    assert isinstance(calc_obj.run(), str)


def test_mixed_input_types():
    """Numeric values provided as float/int should be accepted."""

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

    calc.run()

