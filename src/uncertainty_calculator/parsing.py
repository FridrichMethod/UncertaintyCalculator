"""Parsing helpers for uncertainty calculator inputs."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from sympy import Symbol, symbols, sympify

from uncertainty_calculator._types import Equation, Variables
from uncertainty_calculator.formatting import latex_number


@dataclass
class ParseState:
    """Intermediate parsed inputs ready for computation/rendering."""

    symbols: list[Symbol]
    unc_symbols: list[Symbol]
    output_symbol: Mapping[Symbol, str]
    output_number: Mapping[Symbol, Any]
    output_value: Mapping[Symbol, str]
    uncertainty_values: Mapping[Symbol, Any]
    input_fullunc: list[str]
    input_sigma: list[Any]
    equation_latex_name: str
    equation_expression: Any


def parse_inputs(equation: Equation, variables: Variables) -> ParseState:
    """Parse variables and initialize sympy symbols and lookup mappings."""
    symbol_names: list[str] = []
    uncertainty_names: list[str] = []
    latex_symbols: list[str] = []

    input_mu: list[Any] = []
    input_sigma: list[Any] = []
    input_fullmu: list[str] = []
    input_fullsigma: list[str] = []
    input_fullunc: list[str] = []

    seen_names: set[str] = set()

    for var_item in variables:
        if var_item.name in seen_names:
            msg = f"Duplicate variable name detected: {var_item.name!r}"
            raise ValueError(msg)
        seen_names.add(var_item.name)

        sym_str = var_item.name
        latex_repr = var_item.latex_name.strip()

        symbol_names.append(sym_str)
        uncertainty_names.append(f"sigma_{sym_str}")
        latex_symbols.append(latex_repr)
        input_fullunc.append(f"\\sigma_{{{latex_repr}}}")

        numeric_mu = sympify(var_item.value)
        numeric_sigma = sympify(var_item.uncertainty)

        input_mu.append(numeric_mu)
        input_sigma.append(numeric_sigma)

        latex_mu = latex_number(numeric_mu)
        input_fullmu.append(f"\\left({latex_mu}\\right)")

        latex_sigma = latex_number(numeric_sigma.evalf(2))
        input_fullsigma.append(latex_sigma)

    symbols_parsed = symbols(symbol_names)
    unc_symbols = symbols(uncertainty_names)
    symbol_map = dict(zip(symbol_names, symbols_parsed))

    output_symbol = dict(zip(symbols_parsed + unc_symbols, latex_symbols + input_fullunc))
    output_number = dict(zip(symbols_parsed + unc_symbols, input_mu + input_sigma))
    output_value = dict(zip(symbols_parsed + unc_symbols, input_fullmu + input_fullsigma))
    uncertainty_values = dict(zip(symbols_parsed, input_sigma))

    equation_latex_name = equation.latex_name
    equation_expression = sympify(equation.expression, locals=symbol_map)

    return ParseState(
        symbols=symbols_parsed,
        unc_symbols=unc_symbols,
        output_symbol=output_symbol,
        output_number=output_number,
        output_value=output_value,
        uncertainty_values=uncertainty_values,
        input_fullunc=input_fullunc,
        input_sigma=input_sigma,
        equation_latex_name=equation_latex_name,
        equation_expression=equation_expression,
    )
