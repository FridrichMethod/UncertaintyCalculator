"""Rendering helpers for the uncertainty calculator."""

from __future__ import annotations

import io
from collections.abc import Callable
from dataclasses import dataclass

from uncertainty_calculator.compute import ComputeState
from uncertainty_calculator.formatting import latex_number, latex_symbol, latex_value
from uncertainty_calculator.parsing import ParseState
from uncertainty_calculator.types import LastUnit


@dataclass
class RenderOptions:
    """Rendering configuration for the output."""

    last_unit: LastUnit
    separate: bool
    insert: bool
    include_equation_number: bool


def render_output(
    parse_state: ParseState, compute_state: ComputeState, options: RenderOptions
) -> str:
    """Render the LaTeX output based on parsed inputs and computed results."""
    buffer = io.StringIO()

    def printer(*args: object, end: str = "\n", sep: str = " ") -> None:
        print(*args, file=buffer, end=end, sep=sep)

    if not options.separate:
        _render_combined(printer, parse_state, compute_state, options)
    else:
        _render_separate(printer, parse_state, compute_state, options)

    return buffer.getvalue()


def _env_start(printer: Callable[..., None], include_number: bool, aligned: bool) -> None:
    suffix = "" if include_number else "*"
    printer(f"\\begin{{equation{suffix}}}")
    if aligned:
        printer("\\begin{aligned}")  # noqa: RUF027


def _env_end(printer: Callable[..., None], include_number: bool, aligned: bool) -> None:
    suffix = "" if include_number else "*"
    if aligned:
        printer("\\end{aligned}")  # noqa: RUF027
    printer(f"\\end{{equation{suffix}}}")


def _render_equation_def(
    printer: Callable[..., None],
    parse_state: ParseState,
    compute_state: ComputeState,
    options: RenderOptions,
    aligned: bool,
) -> None:
    separator = "&=" if aligned else "="
    printer(parse_state.equation_left, end=separator)
    printer(latex_symbol(parse_state.equation_right, parse_state.output_symbol), end="=")

    if options.insert:
        printer(latex_value(parse_state.equation_right, parse_state.output_value), end="=")

    res_str = (
        compute_state.result_mu
        if options.last_unit is None
        else f"{compute_state.result_mu}\\ {options.last_unit}"
    )

    if aligned:
        printer(f"{res_str}\\\\\n\\\\")
    else:
        printer(res_str)


def _render_pdvs(
    printer: Callable[..., None],
    parse_state: ParseState,
    compute_state: ComputeState,
    options: RenderOptions,
    aligned: bool,
) -> None:
    separator = "&=" if aligned else "="

    for symbol, pdv, num in compute_state.pdv_results:
        if not parse_state.uncertainty_values[symbol]:
            continue

        lhs = (
            f"\\frac{{\\partial {parse_state.equation_left} }}"
            f"{{\\partial {parse_state.output_symbol[symbol]} }}"
        )
        printer(lhs, end=separator)
        printer(latex_symbol(pdv, parse_state.output_symbol), end="=")

        if options.insert:
            printer(latex_value(pdv, parse_state.output_value), end="=")

        printer(latex_number(num.evalf(2)), end="\\\\\n")


def _sigma_symbolic_terms(parse_state: ParseState) -> list[str]:
    terms = []
    for symbol, fullunc in zip(parse_state.symbols, parse_state.input_fullunc):
        if parse_state.uncertainty_values[symbol]:
            terms.append(
                f"\\left(\\frac{{\\partial {parse_state.equation_left} }}"
                f"{{\\partial {parse_state.output_symbol[symbol]} }} {fullunc}\\right)^2"
            )
    return terms


def _sigma_intermediate_terms(parse_state: ParseState, compute_state: ComputeState) -> list[str]:
    terms = []
    for i, (symbol, _, num) in enumerate(compute_state.pdv_results):
        if parse_state.uncertainty_values[symbol]:
            unc = parse_state.unc_symbols[i]
            val_latex = latex_number(num.evalf(2))
            unc_latex = parse_state.output_value[unc]
            terms.append(f"\\left({val_latex} \\times {unc_latex}\\right)^2")
    return terms


def _sigma_numeric_terms(parse_state: ParseState, compute_state: ComputeState) -> list[str]:
    terms = []
    for i, (symbol, _, num) in enumerate(compute_state.pdv_results):
        if parse_state.uncertainty_values[symbol]:
            unc = parse_state.unc_symbols[i]
            val = (num * parse_state.output_number[unc]).evalf(2)
            terms.append(f"\\left({latex_number(val)}\\right)^2")
    return terms


def _render_sigma(
    printer: Callable[..., None],
    parse_state: ParseState,
    compute_state: ComputeState,
    options: RenderOptions,
) -> None:
    has_uncertainty = any(parse_state.uncertainty_values[symbol] for symbol in parse_state.symbols)

    if not has_uncertainty:
        res_str = (
            compute_state.result_sigma
            if options.last_unit is None
            else f"{compute_state.result_sigma}\\ {options.last_unit}"
        )
        printer(f"\\sigma_{{{parse_state.equation_left}}}&=", end="")
        if not options.separate:
            printer(f"{res_str}\\\\\n\\\\")
        else:
            printer(res_str)
        return

    symbolic_terms = _sigma_symbolic_terms(parse_state)
    printer(f"\\sigma_{{{parse_state.equation_left}}}&=\\sqrt{{{'+'.join(symbolic_terms)}}}\\\\")

    if options.insert:
        intermediate_terms = _sigma_intermediate_terms(parse_state, compute_state)
        printer(f"&=\\sqrt{{{'+'.join(intermediate_terms)}}}\\\\")

    numeric_terms = _sigma_numeric_terms(parse_state, compute_state)
    printer(f"&=\\sqrt{{{'+'.join(numeric_terms)}}}\\\\")

    res_str = (
        compute_state.result_sigma
        if options.last_unit is None
        else f"{compute_state.result_sigma}\\ {options.last_unit}"
    )

    if not options.separate:
        printer(f"&={res_str}\\\\\n\\\\")
    else:
        printer(f"&={res_str}")


def _render_result_line(
    printer: Callable[..., None],
    parse_state: ParseState,
    compute_state: ComputeState,
    options: RenderOptions,
    aligned: bool,
) -> None:
    separator = "&=" if aligned else "="

    if options.last_unit is None:
        line = (
            f"{parse_state.equation_left}{separator}"
            f"{compute_state.result_mu} \\pm {compute_state.result_sigma}"
        )
    else:
        line = (
            f"{parse_state.equation_left}{separator}\\left ({compute_state.result_mu} "
            f"\\pm {compute_state.result_sigma} \\right )\\ {options.last_unit}"
        )

    printer(line)


def _render_combined(
    printer: Callable[..., None],
    parse_state: ParseState,
    compute_state: ComputeState,
    options: RenderOptions,
) -> None:
    _env_start(printer, options.include_equation_number, aligned=True)
    _render_equation_def(printer, parse_state, compute_state, options, aligned=True)
    _render_pdvs(printer, parse_state, compute_state, options, aligned=True)
    printer("\\\\")
    _render_sigma(printer, parse_state, compute_state, options)
    _render_result_line(printer, parse_state, compute_state, options, aligned=True)
    _env_end(printer, options.include_equation_number, aligned=True)


def _render_separate(
    printer: Callable[..., None],
    parse_state: ParseState,
    compute_state: ComputeState,
    options: RenderOptions,
) -> None:
    _env_start(printer, options.include_equation_number, aligned=False)
    _render_equation_def(printer, parse_state, compute_state, options, aligned=False)
    _env_end(printer, options.include_equation_number, aligned=False)

    printer("\n", end="")
    _env_start(printer, options.include_equation_number, aligned=True)
    _render_pdvs(printer, parse_state, compute_state, options, aligned=True)
    _env_end(printer, options.include_equation_number, aligned=True)
    printer("\n", end="")

    _env_start(printer, options.include_equation_number, aligned=True)
    _render_sigma(printer, parse_state, compute_state, options)
    _env_end(printer, options.include_equation_number, aligned=True)
    printer("\n", end="")

    _env_start(printer, options.include_equation_number, aligned=False)
    _render_result_line(printer, parse_state, compute_state, options, aligned=False)

    if options.insert and not options.include_equation_number:
        printer("\\end{equation*}")
    else:
        _env_end(printer, options.include_equation_number, aligned=False)
