"""Core module for Uncertainty Calculator."""

import io
from dataclasses import dataclass
from typing import Any

from sympy import Symbol, diff, latex, simplify, sqrt, symbols, sympify

from uncertainty_calculator.models import Digits, Equation, LastUnit, Variables


@dataclass
class _VariableInputs:
    symbols: list[str]
    uncertainties: list[str]
    latex_symbols: list[str]
    latex_uncertainties: list[str]
    mu_values: list[str]
    sigma_values: list[str]
    latex_mu_values: list[str]
    latex_sigma_values: list[str]


class UncertaintyCalculator:
    """A calculator for error propagation in physical experiments using symbolic differentiation.

    This calculator takes an equation and variables with uncertainties, computes the partial
    derivatives, and propagates the uncertainties to find the final result and its error.
    It outputs the full calculation steps in LaTeX format.
    """

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
        """Initialize the UncertaintyCalculator.

        Args:
            equation: An Equation object.
            variables: A list of Variable objects.
            digits: A Digits config specifying decimal places for 'mu' and 'sigma'.
            last_unit: The unit string or None if dimensionless.
            separate: If True, prints calculation steps in separate equation blocks.
            insert: If True, includes an intermediate step showing values plugged into the formula.
            include_equation_number: If True, uses numbered 'equation' environments;
                otherwise 'equation*'.

        """
        self.equation = equation
        self.variables = variables
        self.digits = digits
        self.last_unit = last_unit
        self.separate = separate
        self.insert = insert
        self.include_equation_number = include_equation_number

        # Parsing state
        self._buffer: io.StringIO | None = None
        self.syms: list[Symbol] = []
        self.uncs: list[Symbol] = []
        self.output_symbol: dict[Symbol, str] = {}
        self.output_number: dict[Symbol, str] = {}
        self.output_value: dict[Symbol, str] = {}
        self.check_unc: dict[Symbol, Any] = {}
        self.input_fullunc: list[str] = []
        self.input_sigma: list[str] = []

        self.equation_left: str = ""
        self.equation_right: Any = None

        # Computation results
        # List of (symbol, partial_derivative_expression, partial_derivative_value)
        self.pdv_results: list[tuple[Symbol, Any, Any]] = []
        self.result_mu: str = ""
        self.result_sigma: str = ""

    def run(self) -> str:
        """Execute the calculation and return the formatted LaTeX string."""
        self._buffer = io.StringIO()
        self._parse_inputs()
        self._validate_inputs()
        self._compute_derivatives()
        self._compute_results()

        if not self.separate:
            self._render_combined()
        else:
            self._render_separate()

        return self._buffer.getvalue()

    def _print(self, *args: Any, **kwargs: Any) -> None:
        """Print to the internal buffer."""
        end = kwargs.get("end", "\n")
        sep = kwargs.get("sep", " ")
        print(*args, file=self._buffer, end=end, sep=sep)

    def _latex_number(self, expr: Any) -> str:
        """Convert a numeric expression to its LaTeX representation."""
        return latex(
            expr,
            inv_trig_style="full",
            ln_notation=True,
            fold_func_brackets=True,
            mul_symbol="times",
        )

    def _latex_symbol(self, expr: Any) -> str:
        """Convert a symbolic expression to LaTeX using the defined symbol mappings."""
        return latex(
            expr,
            inv_trig_style="full",
            ln_notation=True,
            fold_func_brackets=True,
            symbol_names=self.output_symbol,
        )

    def _latex_value(self, expr: Any) -> str:
        """Convert an expression to LaTeX using value mappings (for substitution steps)."""
        return latex(
            expr,
            inv_trig_style="full",
            ln_notation=True,
            fold_func_brackets=True,
            mul_symbol="times",
            symbol_names=self.output_value,
        )

    def _reset_parse_state(self) -> None:
        """Reset per-run state so multiple run() calls remain valid."""
        self.input_fullunc = []
        self.input_sigma = []
        self.syms = []
        self.uncs = []
        self.output_symbol = {}
        self.output_number = {}
        self.output_value = {}
        self.check_unc = {}

    def _collect_variable_inputs(self) -> _VariableInputs:
        """Collect raw and formatted values from variable inputs."""
        inputs = _VariableInputs(
            symbols=[],
            uncertainties=[],
            latex_symbols=[],
            latex_uncertainties=[],
            mu_values=[],
            sigma_values=[],
            latex_mu_values=[],
            latex_sigma_values=[],
        )

        for var_item in self.variables:
            sym_str = var_item.name
            val_mu_str = str(var_item.value)
            val_sigma_str = str(var_item.uncertainty)
            latex_repr = var_item.latex_name.strip()

            inputs.symbols.append(sym_str)
            inputs.uncertainties.append(f"sigma_{sym_str}")
            inputs.latex_symbols.append(latex_repr)
            inputs.latex_uncertainties.append(f"\\sigma_{{{latex_repr}}}")

            inputs.mu_values.append(val_mu_str)
            inputs.sigma_values.append(val_sigma_str)

            latex_mu = self._latex_number(sympify(val_mu_str))
            inputs.latex_mu_values.append(f"\\left({latex_mu}\\right)")

            latex_sigma = self._latex_number(sympify(val_sigma_str).evalf(2))
            inputs.latex_sigma_values.append(latex_sigma)

        return inputs

    def _initialize_symbols(self, inputs: _VariableInputs) -> None:
        """Initialize sympy symbols for variables and uncertainties."""
        self.syms = symbols(inputs.symbols)
        self.uncs = symbols(inputs.uncertainties)

    def _build_mappings(self, inputs: _VariableInputs) -> None:
        """Build lookup mappings for symbols, numbers, and LaTeX values."""
        self.input_fullunc = inputs.latex_uncertainties
        self.input_sigma = inputs.sigma_values
        self.output_symbol = dict(
            zip(self.syms + self.uncs, inputs.latex_symbols + inputs.latex_uncertainties)
        )
        self.output_number = dict(
            zip(self.syms + self.uncs, inputs.mu_values + inputs.sigma_values)
        )
        self.output_value = dict(
            zip(self.syms + self.uncs, inputs.latex_mu_values + inputs.latex_sigma_values)
        )
        self.check_unc = dict(zip(self.syms, sympify(self.input_sigma)))

    def _parse_inputs(self) -> None:
        """Parse variables and initialize sympy symbols."""
        self._reset_parse_state()
        inputs = self._collect_variable_inputs()
        self._initialize_symbols(inputs)
        self._build_mappings(inputs)
        self.equation_left = self.equation.lhs
        self.equation_right = sympify(self.equation.rhs)

    def _validate_inputs(self) -> None:
        """Validate that all symbols in the equation are defined in variables."""
        # Get all free symbols in the equation right-hand side
        free_symbols = self.equation_right.free_symbols

        # Check if all free symbols are in our defined symbols
        # Note: free_symbols contains SymPy Symbol objects
        # self.syms contains SymPy Symbol objects for our variables

        defined_symbols = set(self.syms)

        for sym in free_symbols:
            # Some constants like pi might be in free_symbols if not handled,
            # but usually sympy handles pi as a number.
            # However, if user uses 'pi' string in equation but it's a symbol?
            # sympy.pi is not a Symbol, it's a Number.
            if sym not in defined_symbols:
                # It might be a reserved symbol or something else.
                # But for our calculator, we expect variables to be defined.
                # Let's double check if it's not something like 'e' or 'pi' that sympy auto-converts
                # but might appear as symbol if not properly handled?
                # If the user writes "pi" without defining it, sympy might treat it as Symbol("pi").
                # Unless we sympify with locals?

                # We can't easily distinguish "valid unknown symbol" from "missing variable".
                # But strict validation is good.
                raise ValueError(f"Symbol '{sym}' used in equation but not defined in variables.")

    def _compute_derivatives(self) -> None:
        """Compute partial derivatives for each variable."""
        self.pdv_results = []
        for sym in self.syms:
            if self.check_unc[sym]:
                pdv = simplify(diff(self.equation_right, sym))
                num = pdv.subs(self.output_number)  # type: ignore
                self.pdv_results.append((sym, pdv, num))
            else:
                self.pdv_results.append((sym, sympify(0), sympify(0)))

    def _compute_results(self) -> None:
        """Compute formatted mu and sigma results."""
        self.result_mu = self._latex_number(
            self.equation_right.evalf(self.digits.mu, subs=self.output_number)  # type: ignore
        )

        pdv_nums = [res[2] for res in self.pdv_results]
        sum_squares = sum(
            (num * sympify(sigma)) ** 2
            for num, sigma in zip(pdv_nums, self.input_sigma)  # type: ignore
        )
        self.result_sigma = self._latex_number(
            sqrt(sum_squares).evalf(self.digits.sigma)  # type: ignore
        )

    def _print_env_start(self, aligned: bool = False) -> None:
        """Print the start of an equation environment."""
        suffix = "" if self.include_equation_number else "*"
        self._print(f"\\begin{{equation{suffix}}}")
        if aligned:
            self._print("\\begin{aligned}")  # noqa: RUF027

    def _print_env_end(self, aligned: bool = False) -> None:
        """Print the end of an equation environment."""
        suffix = "" if self.include_equation_number else "*"
        if aligned:
            self._print("\\end{aligned}")  # noqa: RUF027
        self._print(f"\\end{{equation{suffix}}}")

    def _render_combined(self) -> None:
        """Render output when 'separate' is False (all steps in one aligned block)."""
        self._print_env_start(aligned=True)
        self._render_equation_def(aligned=True)
        self._render_pdvs(aligned=True)
        self._print("\\\\")
        self._render_sigma(aligned=True)
        self._render_result_line(aligned=True)
        self._print_env_end(aligned=True)

    def _render_separate(self) -> None:
        """Render output when 'separate' is True (steps in separate equation blocks)."""
        # 1. Equation Definition
        self._print_env_start(aligned=False)
        self._render_equation_def(aligned=False)
        self._print_env_end(aligned=False)

        # 2. Partial Derivatives
        self._print("\n", end="")
        self._print_env_start(aligned=True)
        self._render_pdvs(aligned=True)
        self._print_env_end(aligned=True)
        self._print("\n", end="")

        # 3. Sigma Calculation
        self._print_env_start(aligned=True)
        self._render_sigma(aligned=True)
        self._print_env_end(aligned=True)
        self._print("\n", end="")

        # 4. Final Result
        self._print_env_start(aligned=False)
        self._render_result_line(aligned=False)

        # Handle specific legacy output behavior:
        # When separate=True, insert=True, and include_equation_number=False,
        # the legacy code outputted "\end{equation}*" instead of "\end{equation*}"
        if self.insert and not self.include_equation_number:
            self._print("\\end{equation*}")
        else:
            self._print_env_end(aligned=False)

    def _render_equation_def(self, aligned: bool) -> None:
        """Render the equation definition line (e.g. z = x/y = ...)."""
        separator = "&=" if aligned else "="
        self._print(self.equation_left, end=separator)
        self._print(self._latex_symbol(self.equation_right), end="=")

        if self.insert:
            self._print(self._latex_value(self.equation_right), end="=")

        # Format result string with unit
        res_str = (
            self.result_mu if self.last_unit is None else f"{self.result_mu}\\ {self.last_unit}"
        )

        if aligned:
            # In combined mode, include extra newlines for spacing
            self._print(f"{res_str}\\\\\n\\\\")
        else:
            self._print(res_str)

    def _render_pdvs(self, aligned: bool) -> None:
        """Render partial derivatives lines."""
        # Note: aligned is typically True for PDs
        separator = "&=" if aligned else "="

        for sym, pdv, num in self.pdv_results:
            if not self.check_unc[sym]:
                continue

            lhs = (
                f"\\frac{{\\partial {self.equation_left} }}{{\\partial {self.output_symbol[sym]} }}"
            )
            self._print(lhs, end=separator)
            self._print(self._latex_symbol(pdv), end="=")

            if self.insert:
                self._print(self._latex_value(pdv), end="=")

            self._print(self._latex_number(num.evalf(2)), end="\\\\\n")

    def _sigma_symbolic_terms(self) -> list[str]:
        """Build symbolic sigma terms."""
        terms = []
        for sym, fullunc in zip(self.syms, self.input_fullunc):
            if self.check_unc[sym]:
                terms.append(
                    f"\\left(\\frac{{\\partial {self.equation_left} }}"
                    f"{{\\partial {self.output_symbol[sym]} }} {fullunc}\\right)^2"
                )
        return terms

    def _sigma_intermediate_terms(self) -> list[str]:
        """Build intermediate sigma terms with substituted derivative values."""
        terms = []
        for i, (sym, _, num) in enumerate(self.pdv_results):
            if self.check_unc[sym]:
                unc = self.uncs[i]
                val_latex = self._latex_number(num.evalf(2))
                unc_latex = self.output_value[unc]
                terms.append(f"\\left({val_latex} \\times {unc_latex}\\right)^2")
        return terms

    def _sigma_numeric_terms(self) -> list[str]:
        """Build numeric sigma terms with substituted derivative and uncertainty values."""
        terms = []
        for i, (sym, _, num) in enumerate(self.pdv_results):
            if self.check_unc[sym]:
                unc = self.uncs[i]
                val = (num * sympify(self.output_number[unc])).evalf(2)
                terms.append(f"\\left({self._latex_number(val)}\\right)^2")
        return terms

    def _render_sigma(self, aligned: bool) -> None:
        """Render the sigma (uncertainty) calculation lines."""
        has_uncertainty = any(self.check_unc[sym] for sym in self.syms)

        if not has_uncertainty:
            # Short-circuit when all uncertainties are zero to avoid empty sqrt blocks
            res_str = (
                self.result_sigma
                if self.last_unit is None
                else f"{self.result_sigma}\\ {self.last_unit}"
            )
            self._print(f"\\sigma_{{{self.equation_left}}}&=", end="")
            if not self.separate:
                self._print(f"{res_str}\\\\\n\\\\")
            else:
                self._print(res_str)
            return

        # 1. Symbolic representation
        symbolic_terms = self._sigma_symbolic_terms()
        line1 = f"\\sigma_{{{self.equation_left}}}&=\\sqrt{{{'+'.join(symbolic_terms)}}}\\\\"
        self._print(line1)

        # 2. Intermediate representation with values (if insert)
        if self.insert:
            intermediate_terms = self._sigma_intermediate_terms()
            self._print(f"&=\\sqrt{{{'+'.join(intermediate_terms)}}}\\\\")

        # 3. Combined numeric representation
        numeric_terms = self._sigma_numeric_terms()
        self._print(f"&=\\sqrt{{{'+'.join(numeric_terms)}}}\\\\")

        # 4. Final Sigma Result
        self._print("&=", end="")

        if self.last_unit is None:
            res_str = self.result_sigma
        else:
            res_str = f"{self.result_sigma}\\ {self.last_unit}"

        if not self.separate:
            # Combined block needs extra newlines
            self._print(f"{res_str}\\\\\n\\\\")
        else:
            # Separate block does NOT need extra newlines
            self._print(res_str)

    def _render_result_line(self, aligned: bool) -> None:
        """Render the final result line with +/- uncertainty."""
        separator = "&=" if aligned else "="

        if self.last_unit is None:
            line = f"{self.equation_left}{separator}{self.result_mu} \\pm {self.result_sigma}"
        else:
            line = (
                f"{self.equation_left}{separator}\\left ({self.result_mu} "
                f"\\pm {self.result_sigma} \\right )\\ {self.last_unit}"
            )

        self._print(line)
