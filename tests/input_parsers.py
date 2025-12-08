"""Utility helpers for converting legacy test inputs."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from uncertainty_calculator import Equation, Variable


def parse_equation(raw_equation: Sequence[str]) -> Equation:
    """Convert a (lhs, rhs) sequence into an Equation dataclass."""
    if len(raw_equation) != 2:
        msg = "Equation must contain exactly two entries (lhs, rhs)."
        raise ValueError(msg)
    lhs, rhs = raw_equation
    return Equation(lhs=lhs.strip(), rhs=rhs.strip())


def parse_variables(raw_variables: Iterable[tuple[str, str]]) -> list[Variable]:
    """Convert legacy variable tuples into Variable dataclasses."""
    parsed: list[Variable] = []
    for definition, latex_name in raw_variables:
        parts = definition.split("=")
        if len(parts) != 2:
            msg = f"Invalid variable definition: '{definition}'"
            raise ValueError(msg)
        name = parts[0].strip()
        value_parts = parts[1].split("+-")
        if len(value_parts) != 2:
            msg = f"Invalid value/uncertainty format: '{definition}'"
            raise ValueError(msg)
        value = value_parts[0].strip()
        uncertainty = value_parts[1].strip()
        parsed.append(
            Variable(
                name=name,
                value=value,
                uncertainty=uncertainty,
                latex_name=latex_name,
            )
        )
    return parsed
