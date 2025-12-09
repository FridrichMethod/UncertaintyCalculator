"""Computation helpers for uncertainty calculator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from sympy import S, diff, simplify, sqrt

from uncertainty_calculator.formatting import latex_number
from uncertainty_calculator.parsing import ParseState
from uncertainty_calculator.types import Digits


@dataclass
class ComputeState:
    """Computed derivatives and final results."""

    pdv_results: list[tuple[Any, Any, Any]]
    result_mu: str
    result_sigma: str


def compute(parse_state: ParseState, digits: Digits) -> ComputeState:
    """Compute partial derivatives and formatted mu/sigma results."""
    pdv_results: list[tuple[Any, Any, Any]] = []
    for symbol in parse_state.symbols:
        if parse_state.uncertainty_values[symbol]:
            pdv = simplify(diff(parse_state.equation_right, symbol))
            num = pdv.subs(parse_state.output_number)  # type: ignore
            pdv_results.append((symbol, pdv, num))
        else:
            pdv_results.append((symbol, S.Zero, S.Zero))

    result_mu = latex_number(
        parse_state.equation_right.evalf(digits.mu, subs=parse_state.output_number)  # type: ignore
    )

    pdv_nums = [res[2] for res in pdv_results]
    sum_squares = sum(
        (num * sigma_value) ** 2 for num, sigma_value in zip(pdv_nums, parse_state.input_sigma)
    )
    result_sigma = latex_number(sqrt(sum_squares).evalf(digits.sigma))  # type: ignore

    return ComputeState(pdv_results=pdv_results, result_mu=result_mu, result_sigma=result_sigma)
