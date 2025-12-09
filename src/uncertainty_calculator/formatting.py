"""Formatting helpers for LaTeX output."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from sympy import latex


def latex_number(expr: Any) -> str:
    """Convert a numeric expression to its LaTeX representation."""
    return latex(
        expr,
        inv_trig_style="full",
        ln_notation=True,
        fold_func_brackets=True,
        mul_symbol="times",
    )


def latex_symbol(expr: Any, symbol_names: Mapping[Any, str]) -> str:
    """Convert a symbolic expression to LaTeX using provided symbol mappings."""
    return latex(
        expr,
        inv_trig_style="full",
        ln_notation=True,
        fold_func_brackets=True,
        symbol_names=symbol_names,
    )


def latex_value(expr: Any, symbol_names: Mapping[Any, str]) -> str:
    """Convert an expression to LaTeX using provided value mappings."""
    return latex(
        expr,
        inv_trig_style="full",
        ln_notation=True,
        fold_func_brackets=True,
        mul_symbol="times",
        symbol_names=symbol_names,
    )
