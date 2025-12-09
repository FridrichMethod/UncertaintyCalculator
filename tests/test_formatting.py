# pyright: reportMissingImports=false
"""Tests for formatting helpers."""

from __future__ import annotations

from sympy import sympify

from uncertainty_calculator.formatting import latex_number


def test_latex_number_basic_formatting():
    """latex_number should render rational and integer inputs."""
    assert latex_number(sympify("3/2")) == "\\frac{3}{2}"
    assert latex_number(2) == "2"
