# pyright: reportMissingImports=false
"""Tests for compute helpers."""

from __future__ import annotations

from sympy import S, Symbol

from uncertainty_calculator import Digits, Equation, Variable
from uncertainty_calculator.compute import compute
from uncertainty_calculator.parsing import parse_inputs


def _simple_parse_state(value: str, uncertainty: str = "0.1"):
    equation = Equation(lhs="y", rhs="x")
    variables = [Variable(name="x", value=value, uncertainty=uncertainty, latex_name="x")]
    return parse_inputs(equation, variables)


def test_compute_zero_uncertainty_sets_zero_derivative_and_sigma():
    """Zero uncertainty should produce zero derivatives and zero sigma."""

    parse_state = _simple_parse_state(value="2", uncertainty="0")
    compute_state = compute(parse_state, digits=Digits(mu=2, sigma=2))

    symbol, pdv_expr, pdv_num = compute_state.pdv_results[0]
    assert isinstance(symbol, Symbol)
    assert pdv_expr == S.Zero
    assert pdv_num == S.Zero
    assert compute_state.result_sigma == "0"

