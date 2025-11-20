import io
from typing import Any

from sympy import Symbol, diff, latex, simplify, sqrt, symbols, sympify

# Type definitions matching Python 3.12 style
type Equation = list[str]
type Variables = list[tuple[str, str]]
type Digits = dict[str, int]
type LastUnit = str | int


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
        separate: int | bool,
        insert: int | bool,
        include_equation_number: int | bool,
    ) -> None:
        """Initialize the UncertaintyCalculator.

        Args:
            equation: A list containing the LHS and RHS of the equation as strings.
            variables: A list of tuples defining variables and their LaTeX representations.
                      Example: [("K = 4 +- 0", "K"), ...]
            digits: A dictionary specifying decimal places for 'mu' and 'sigma'.
            last_unit: The unit string (e.g. r"\\si{V}") or 1 if dimensionless.
            separate: If True (or 1), prints calculation steps in separate equation blocks.
            insert: If True (or 1), includes an intermediate step showing values plugged into the formula.
            include_equation_number: If True (or 1), uses numbered 'equation' environments; otherwise 'equation*'.

        """
        self.equation = equation
        self.variables = variables
        self.digits = digits
        self.last_unit = last_unit
        self.separate = bool(separate)
        self.insert = bool(insert)
        self.include_equation_number = bool(include_equation_number)

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
        self._compute_derivatives_and_results()

        if not self.separate:
            self._render_combined()
        else:
            self._render_separate()

        return self._buffer.getvalue()

    # --- Output Helpers ---

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
        """Convert an expression to LaTeX using the defined value mappings (for substitution steps)."""
        return latex(
            expr,
            inv_trig_style="full",
            ln_notation=True,
            fold_func_brackets=True,
            mul_symbol="times",
            symbol_names=self.output_value,
        )

    # --- Core Logic Steps ---

    def _parse_inputs(self) -> None:
        """Parse variables and initialize sympy symbols."""
        input_sym: list[str] = []
        input_unc: list[str] = []
        input_fullsym: list[str] = []

        input_mu: list[str] = []
        input_fullmu: list[str] = []
        input_fullsigma: list[str] = []

        for var_def, latex_repr in self.variables:
            # Format: "K = 4 +- 0"
            parts = var_def.split("=")
            sym_str = parts[0].strip()
            value_parts = parts[1].split("+-")
            val_mu_str = value_parts[0].strip()
            val_sigma_str = value_parts[1].strip()

            input_sym.append(sym_str)
            input_unc.append(f"sigma_{sym_str}")
            input_fullsym.append(latex_repr.strip())
            self.input_fullunc.append(f"\\sigma_{{{latex_repr.strip()}}}")

            input_mu.append(val_mu_str)
            self.input_sigma.append(val_sigma_str)

            # Pre-calculate latex representations for values
            latex_mu = self._latex_number(sympify(val_mu_str))
            input_fullmu.append(f"\\left({latex_mu}\\right)")

            latex_sigma = self._latex_number(sympify(val_sigma_str).evalf(2))
            input_fullsigma.append(latex_sigma)

        self.syms = symbols(input_sym)
        self.uncs = symbols(input_unc)

        # Create mappings for sympy substitutions and latex rendering
        self.output_symbol = dict(zip(self.syms + self.uncs, input_fullsym + self.input_fullunc))
        self.output_number = dict(zip(self.syms + self.uncs, input_mu + self.input_sigma))
        self.output_value = dict(zip(self.syms + self.uncs, input_fullmu + input_fullsigma))
        self.check_unc = dict(zip(self.syms, sympify(self.input_sigma)))

        self.equation_left = self.equation[0]
        self.equation_right = sympify(self.equation[1])

    def _compute_derivatives_and_results(self) -> None:
        """Compute partial derivatives and final mu/sigma values."""
        self.pdv_results = []
        for sym in self.syms:
            if self.check_unc[sym]:
                pdv = simplify(diff(self.equation_right, sym))
                num = pdv.subs(self.output_number)  # type: ignore
                self.pdv_results.append((sym, pdv, num))
            else:
                self.pdv_results.append((sym, sympify(0), sympify(0)))

        # Calculate Mu (Mean)
        self.result_mu = self._latex_number(
            self.equation_right.evalf(self.digits["mu"], subs=self.output_number)  # type: ignore
        )

        # Calculate Sigma (Uncertainty)
        # Extract numeric values of partial derivatives
        pdv_nums = [res[2] for res in self.pdv_results]

        sum_squares = sum(
            (num * sympify(sigma)) ** 2
            for num, sigma in zip(pdv_nums, self.input_sigma)  # type: ignore
        )
        self.result_sigma = self._latex_number(
            sqrt(sum_squares).evalf(self.digits["sigma"])  # type: ignore
        )

    # --- Rendering Methods ---

    def _print_env_start(self, aligned: bool = False) -> None:
        """Print the start of an equation environment."""
        suffix = "" if self.include_equation_number else "*"
        self._print(f"\\begin{{equation{suffix}}}")
        if aligned:
            self._print("\\begin{aligned}")

    def _print_env_end(self, aligned: bool = False) -> None:
        """Print the end of an equation environment."""
        suffix = "" if self.include_equation_number else "*"
        if aligned:
            self._print("\\end{aligned}")
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
            self._print("\\end{equation}*")
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
        if self.last_unit == 1:
            res_str = self.result_mu
        else:
            res_str = f"{self.result_mu}\\ {self.last_unit}"

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

    def _render_sigma(self, aligned: bool) -> None:
        """Render the sigma (uncertainty) calculation lines."""
        # 1. Symbolic representation
        terms = []
        for sym, fullunc in zip(self.syms, self.input_fullunc):
            if self.check_unc[sym]:
                term = (
                    f"\\left(\\frac{{\\partial {self.equation_left} }}"
                    f"{{\\partial {self.output_symbol[sym]} }} {fullunc}\\right)^2"
                )
                terms.append(term)

        line1 = f"\\sigma_{{{self.equation_left}}}&=\\sqrt{{{'+'.join(terms)}}}\\\\"
        self._print(line1)

        # 2. Intermediate representation with values (if insert)
        if self.insert:
            terms_inter = []
            for i, (sym, _, num) in enumerate(self.pdv_results):
                if self.check_unc[sym]:
                    unc = self.uncs[i]
                    # self.output_value[unc] contains the latex string for uncertainty
                    val_latex = self._latex_number(num.evalf(2))
                    unc_latex = self.output_value[unc]
                    term = f"\\left({val_latex} \\times {unc_latex}\\right)^2"
                    terms_inter.append(term)

            self._print(f"&=\\sqrt{{{'+'.join(terms_inter)}}}\\\\")

        # 3. Combined numeric representation
        terms_combined = []
        for i, (sym, _, num) in enumerate(self.pdv_results):
            if self.check_unc[sym]:
                unc = self.uncs[i]
                # self.output_number[unc] contains the raw numeric string for uncertainty
                # Multiply pdv value (num) by uncertainty value
                val = (num * sympify(self.output_number[unc])).evalf(2)
                term = f"\\left({self._latex_number(val)}\\right)^2"
                terms_combined.append(term)

        self._print(f"&=\\sqrt{{{'+'.join(terms_combined)}}}\\\\")

        # 4. Final Sigma Result
        self._print("&=", end="")

        if self.last_unit == 1:
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

        if self.last_unit == 1:
            self._print(f"{self.equation_left}{separator}{self.result_mu} \\pm {self.result_sigma}")
        else:
            self._print(
                f"{self.equation_left}{separator}\\left ({self.result_mu} \\pm {self.result_sigma} \\right )\\ {self.last_unit}"
            )
