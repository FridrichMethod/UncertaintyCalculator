"""Validation helpers for parsed inputs."""

from __future__ import annotations

from uncertainty_calculator.parsing import ParseState


def validate_inputs(parse_state: ParseState) -> None:
    """Ensure all symbols referenced in the equation are defined by variables."""
    defined_symbols = set(parse_state.symbols)
    free_symbols = parse_state.equation_right.free_symbols

    for sym in free_symbols:
        if sym not in defined_symbols:
            msg = f"Symbol '{sym}' used in equation but not defined in variables."
            raise ValueError(msg)
