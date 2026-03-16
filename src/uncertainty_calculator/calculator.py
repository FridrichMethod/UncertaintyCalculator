"""Pipeline orchestrator for the uncertainty calculator."""

from __future__ import annotations

from uncertainty_calculator._types import Digits, Equation, Variables
from uncertainty_calculator.compute import ComputeState, compute
from uncertainty_calculator.parsers import ParseState, parse_inputs
from uncertainty_calculator.render import RenderOptions, render_output
from uncertainty_calculator.validation import validate_inputs


class UncertaintyCalculator:
    """A calculator for error propagation in physical experiments using symbolic differentiation."""

    def __init__(
        self,
        digits: Digits,
        last_unit: str | None,
        separate: bool,
        insert: bool,
        include_equation_number: bool,
    ) -> None:
        """Initialize the calculator with rendering and precision configuration."""
        self.digits = digits
        self.last_unit = last_unit
        self.separate = separate
        self.insert = insert
        self.include_equation_number = include_equation_number

    def run(self, equation: Equation, variables: Variables) -> str:
        """Execute the calculation pipeline and return the LaTeX string."""
        parse_state: ParseState = parse_inputs(equation, variables)
        validate_inputs(parse_state)
        compute_state: ComputeState = compute(parse_state, self.digits)

        options = RenderOptions(
            last_unit=self.last_unit,
            separate=self.separate,
            insert=self.insert,
            include_equation_number=self.include_equation_number,
        )
        return render_output(parse_state, compute_state, options)
