"""Dataclasses and type definitions for the uncertainty calculator."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from numbers import Real


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
        value: The numeric value of the variable.
        uncertainty: The numeric uncertainty of the variable.
        latex_name: The LaTeX representation of the variable (e.g., r"\eta").

    """

    name: str
    value: float
    uncertainty: float
    latex_name: str

    def __post_init__(self) -> None:
        """Validate that numeric fields are real numbers and normalize them to floats."""
        for field_name in ("value", "uncertainty"):
            field_value = getattr(self, field_name)
            if isinstance(field_value, bool) or not isinstance(field_value, Real):
                msg = f"{field_name} must be a real number (got {field_value!r})"
                raise TypeError(msg)
            setattr(self, field_name, float(field_value))


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
