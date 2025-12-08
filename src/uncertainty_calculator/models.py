"""Dataclasses and type definitions for the uncertainty calculator."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass


@dataclass
class Equation:
    """An equation definition for the uncertainty calculator.

    Attributes:
        lhs: The left-hand side of the equation (variable name).
        rhs: The right-hand side of the equation (expression).

    """

    lhs: str
    rhs: str


@dataclass
class Variable:
    r"""A variable definition for the uncertainty calculator.

    Attributes:
        name: The variable symbol used in the equation (e.g., "K").
        value: The value of the variable. Can be a number or a string expression (e.g., "4", "1/sqrt(3)").
        uncertainty: The uncertainty of the variable. Can be a number or string expression.
        latex_name: The LaTeX representation of the variable (e.g., r"\eta").

    """

    name: str
    value: str | float
    uncertainty: str | float
    latex_name: str


@dataclass
class Digits:
    """Digits configuration for result rounding."""

    mu: int
    sigma: int

    def __post_init__(self) -> None:
        """Validate that digit counts are positive integers."""
        for field_name, value in (("mu", self.mu), ("sigma", self.sigma)):
            if not isinstance(value, int) or value <= 0:
                msg = f"{field_name} must be a positive integer (got {value!r})"
                raise ValueError(msg)


# Type definitions matching Python 3.12 style
type Variables = Iterable[Variable]
type LastUnit = str | None
