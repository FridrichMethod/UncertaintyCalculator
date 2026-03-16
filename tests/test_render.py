# pyright: reportMissingImports=false
"""Tests for render helpers."""

from __future__ import annotations

from uncertainty_calculator import Digits, Equation, UncertaintyCalculator, Variable
from uncertainty_calculator.compute import compute
from uncertainty_calculator.parsers import parse_inputs
from uncertainty_calculator.render import RenderOptions, render_output


def _simple_parse_state(value: float, uncertainty: float = 0.1):
    equation = Equation(latex_name="y", expression="x")
    variables = [Variable(name="x", value=value, uncertainty=uncertainty, latex_name="x")]
    return parse_inputs(equation, variables)


def test_render_output_combined_contains_sigma_line():
    """Combined render should include sigma line and equation alignment."""
    parse_state = _simple_parse_state(value=2.0, uncertainty=0.5)
    compute_state = compute(parse_state, digits=Digits(mu=2, sigma=2))
    options = RenderOptions(
        last_unit=None, separate=False, insert=False, include_equation_number=False
    )

    output = render_output(parse_state, compute_state, options)
    assert "\\begin{aligned}" in output
    assert "\\sigma_{y}" in output
    assert "y&=" in output


def test_zero_uncertainty_renders_sigma_without_empty_sqrt():
    """Sigma render should short-circuit when uncertainties are zero."""
    digits = Digits(mu=2, sigma=2)
    calc = UncertaintyCalculator(
        digits=digits,
        last_unit=None,
        separate=False,
        insert=False,
        include_equation_number=False,
    )

    output = calc.run(
        equation=Equation(latex_name="y", expression="x"),
        variables=[Variable(name="x", value=1, uncertainty=0, latex_name="x")],
    )
    assert "\\sigma_{y}&=0" in output
    assert "sqrt{" not in output
