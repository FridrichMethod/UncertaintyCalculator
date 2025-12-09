"""Pipeline orchestrator for the uncertainty calculator."""

from __future__ import annotations

from uncertainty_calculator.compute import ComputeState, compute
from uncertainty_calculator.parsing import ParseState, parse_inputs
from uncertainty_calculator.rendering import RenderOptions, render_output
from uncertainty_calculator.types import Digits, Equation, LastUnit, Variables
from uncertainty_calculator.validation import validate_inputs


class UncertaintyCalculator:
    """A calculator for error propagation in physical experiments using symbolic differentiation."""

    def __init__(
        self,
        equation: Equation,
        variables: Variables,
        digits: Digits,
        last_unit: LastUnit,
        separate: bool,
        insert: bool,
        include_equation_number: bool,
    ) -> None:
        """Initialize the calculator with all configuration options."""
        self.equation = equation
        self.variables = variables
        self.digits = digits
        self.last_unit = last_unit
        self.separate = separate
        self.insert = insert
        self.include_equation_number = include_equation_number

    def run(self) -> str:
        """Execute the calculation pipeline and return the LaTeX string."""
        parse_state: ParseState = parse_inputs(self.equation, self.variables)
        validate_inputs(parse_state)
        compute_state: ComputeState = compute(parse_state, self.digits)

        options = RenderOptions(
            last_unit=self.last_unit,
            separate=self.separate,
            insert=self.insert,
            include_equation_number=self.include_equation_number,
        )
        return render_output(parse_state, compute_state, options)
