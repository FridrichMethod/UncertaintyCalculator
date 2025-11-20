import io

from sympy import diff, latex, simplify, sqrt, symbols, sympify


class UncertaintyCalculator:
    def __init__(
        self,
        equation,
        variable,
        result_digit,
        result_unit,
        separate,
        insert,
        include_equation_number,
    ):
        self.equation = equation
        self.variable = variable
        self.result_digit = result_digit
        self.result_unit = result_unit
        self.separate = separate
        self.insert = insert
        self.include_equation_number = include_equation_number

    def run(self):
        # Capture output to string
        output_buffer = io.StringIO()

        def custom_print(*args, **kwargs):
            end = kwargs.get("end", "\n")
            sep = kwargs.get("sep", " ")
            print(*args, file=output_buffer, end=end, sep=sep)

        # Parsing logic
        input_sym = []
        input_unc = []
        input_fullsym = []
        input_fullunc = []
        input_mu = []
        input_sigma = []
        input_fullmu = []
        input_fullsigma = []

        def latex_number(expr):
            return latex(
                expr,
                inv_trig_style="full",
                ln_notation=True,
                fold_func_brackets=True,
                mul_symbol="times",
            )

        for x in self.variable:
            input_symbol = x[0].split("=")
            input_value = input_symbol[1].split("+-")
            input_sym.append(input_symbol[0].strip())
            input_unc.append(f"sigma_{input_symbol[0].strip()}")
            input_fullsym.append(x[1].strip())
            input_fullunc.append(f"\\sigma_{{{x[1].strip()}}}")
            input_mu.append(input_value[0].strip())
            input_sigma.append(input_value[1].strip())
            input_fullmu.append(f"\\left({latex_number(sympify(input_value[0].strip()))}\\right)")
            input_fullsigma.append(latex_number(sympify(input_value[1].strip()).evalf(2)))

        syms = symbols(input_sym)
        uncs = symbols(input_unc)
        output_symbol = dict(zip(syms + uncs, input_fullsym + input_fullunc))
        output_number = dict(zip(syms + uncs, input_mu + input_sigma))
        output_value = dict(zip(syms + uncs, input_fullmu + input_fullsigma))
        check_unc = dict(zip(syms, sympify(input_sigma)))
        equation_left = self.equation[0]
        equation_right = sympify(self.equation[1])

        def latex_symbol(expr):
            return latex(
                expr,
                inv_trig_style="full",
                ln_notation=True,
                fold_func_brackets=True,
                symbol_names=output_symbol,
            )

        def latex_value(expr):
            return latex(
                expr,
                inv_trig_style="full",
                ln_notation=True,
                fold_func_brackets=True,
                mul_symbol="times",
                symbol_names=output_value,
            )

        # Main Logic with if/else branches
        if self.insert:
            if not self.separate:
                custom_print(
                    """\\begin{equation}
\\begin{aligned}"""
                    if self.include_equation_number
                    else """\\begin{equation*}
\\begin{aligned}"""
                )
                custom_print(equation_left, end="&=")
                custom_print(latex_symbol(equation_right), end="=")
                custom_print(latex_value(equation_right), end="=")
                result_mu = latex_number(
                    equation_right.evalf(self.result_digit["mu"], subs=output_number)
                )
                if self.result_unit == 1:
                    custom_print(result_mu + "\\\\\n\\\\")
                else:
                    custom_print(f"{result_mu}\\ " + self.result_unit + "\\\\\n\\\\")

                pdv_number = []
                for sym in syms:
                    if check_unc[sym]:
                        custom_print(
                            f"\\frac{{\\partial {equation_left} }}{{\\partial {output_symbol[sym]} }}",
                            end="&=",
                        )
                        pdv = simplify(diff(equation_right, sym))
                        custom_print(latex_symbol(pdv), end="=")
                        custom_print(latex_value(pdv), end="=")
                        num = pdv.subs(output_number)
                        pdv_number.append(num)
                        custom_print(latex_number(num.evalf(2)), end="\\\\\n")
                    else:
                        pdv_number.append(sympify(0))
                custom_print("\\\\")

                custom_print(
                    f"\\sigma_{{{equation_left}}}&=\\sqrt{{"
                    + "+".join(
                        f"\\left(\\frac{{\\partial {equation_left} }}{{\\partial {output_symbol[sym]} }} {fullunc}\\right)^2"
                        for sym, fullunc in zip(syms, input_fullunc)
                        if check_unc[sym]
                    )
                    + "}\\\\"
                )
                custom_print(
                    "&=\\sqrt{"
                    + "+".join(
                        f"\\left({latex_number(num.evalf(2))} \\times {output_value[unc]}\\right)^2"
                        for num, unc in zip(pdv_number, uncs)
                        if sympify(output_number[unc])
                    )
                    + "}\\\\"
                )
                custom_print(
                    "&=\\sqrt{"
                    + "+".join(
                        f"\\left({latex_number((num * sympify(output_number[unc])).evalf(2))}\\right)^2"
                        for num, unc in zip(pdv_number, uncs)
                        if sympify(output_number[unc])
                    )
                    + "}\\\\"
                )
                result_sigma = latex_number(
                    sqrt(
                        sum(
                            (num * sympify(sigma)) ** 2
                            for num, sigma in zip(pdv_number, input_sigma)
                        )
                    ).evalf(self.result_digit["sigma"])
                )
                custom_print("&=", end="")
                if self.result_unit == 1:
                    custom_print(result_sigma + "\\\\\n\\\\")
                else:
                    custom_print(f"{result_sigma}\\ " + self.result_unit + "\\\\\n\\\\")

                # Result
                if self.result_unit == 1:
                    custom_print(f"{equation_left}&={result_mu} \\pm {result_sigma}")
                else:
                    custom_print(
                        f"{equation_left}&=\\left ({result_mu} \\pm {result_sigma} \\right )\\ "
                        + self.result_unit
                    )
                custom_print(
                    """\\end{aligned}
\\end{equation}"""
                    if self.include_equation_number
                    else """\\end{aligned}
\\end{equation*}"""
                )

            else:
                custom_print(
                    "\\begin{equation}" if self.include_equation_number else "\\begin{equation*}"
                )
                custom_print(equation_left, end="=")
                custom_print(latex_symbol(equation_right), end="=")
                custom_print(latex_value(equation_right), end="=")
                result_mu = latex_number(
                    equation_right.evalf(self.result_digit["mu"], subs=output_number)
                )
                if self.result_unit == 1:
                    custom_print(result_mu)
                else:
                    custom_print(f"{result_mu}\\ " + self.result_unit)
                custom_print(
                    "\\end{equation}" if self.include_equation_number else "\\end{equation*}"
                )

                pdv_number = []
                custom_print(
                    """
\\begin{equation}
\\begin{aligned}"""
                    if self.include_equation_number
                    else """
\\begin{equation*}
\\begin{aligned}"""
                )
                for sym in syms:
                    if check_unc[sym]:
                        custom_print(
                            f"\\frac{{\\partial {equation_left} }}{{\\partial {output_symbol[sym]} }}",
                            end="&=",
                        )
                        pdv = simplify(diff(equation_right, sym))
                        custom_print(latex_symbol(pdv), end="=")
                        custom_print(latex_value(pdv), end="=")
                        num = pdv.subs(output_number)
                        pdv_number.append(num)
                        custom_print(latex_number(num.evalf(2)), end="\\\\\n")
                    else:
                        pdv_number.append(sympify(0))
                custom_print(
                    """\\end{aligned}
\\end{equation}
"""
                    if self.include_equation_number
                    else """\\end{aligned}
\\end{equation*}
"""
                )

                custom_print(
                    """\\begin{equation}
\\begin{aligned}"""
                    if self.include_equation_number
                    else """\\begin{equation*}
\\begin{aligned}"""
                )
                custom_print(
                    f"\\sigma_{{{equation_left}}}&=\\sqrt{{"
                    + "+".join(
                        f"\\left(\\frac{{\\partial {equation_left} }}{{\\partial {output_symbol[sym]} }} {fullunc}\\right)^2"
                        for sym, fullunc in zip(syms, input_fullunc)
                        if check_unc[sym]
                    )
                    + "}\\\\"
                )
                custom_print(
                    "&=\\sqrt{"
                    + "+".join(
                        f"\\left({latex_number(num.evalf(2))} \\times {output_value[unc]}\\right)^2"
                        for num, unc in zip(pdv_number, uncs)
                        if sympify(output_number[unc])
                    )
                    + "}\\\\"
                )
                custom_print(
                    "&=\\sqrt{"
                    + "+".join(
                        f"\\left({latex_number((num * sympify(output_number[unc])).evalf(2))}\\right)^2"
                        for num, unc in zip(pdv_number, uncs)
                        if sympify(output_number[unc])
                    )
                    + "}\\\\"
                )
                result_sigma = latex_number(
                    sqrt(
                        sum(
                            (num * sympify(sigma)) ** 2
                            for num, sigma in zip(pdv_number, input_sigma)
                        )
                    ).evalf(self.result_digit["sigma"])
                )
                custom_print("&=", end="")
                if self.result_unit == 1:
                    custom_print(result_sigma)
                else:
                    custom_print(f"{result_sigma}\\ " + self.result_unit)
                custom_print(
                    """\\end{aligned}
\\end{equation}
"""
                    if self.include_equation_number
                    else """\\end{aligned}
\\end{equation*}
"""
                )

                # Result
                custom_print(
                    "\\begin{equation}" if self.include_equation_number else "\\begin{equation*}"
                )
                if self.result_unit == 1:
                    custom_print(f"{equation_left}={result_mu} \\pm {result_sigma}")
                else:
                    custom_print(
                        f"{equation_left}=\\left ({result_mu} \\pm {result_sigma} \\right )\\ "
                        + self.result_unit
                    )
                custom_print(
                    "\\end{equation}" if self.include_equation_number else "\\end{equation}*"
                )

        elif not self.separate:
            custom_print(
                """\\begin{equation}
\\begin{aligned}"""
                if self.include_equation_number
                else """\\begin{equation*}
\\begin{aligned}"""
            )
            custom_print(equation_left, end="&=")
            custom_print(latex_symbol(equation_right), end="=")
            result_mu = latex_number(
                equation_right.evalf(self.result_digit["mu"], subs=output_number)
            )
            if self.result_unit == 1:
                custom_print(result_mu + "\\\\\n\\\\")
            else:
                custom_print(f"{result_mu}\\ " + self.result_unit + "\\\\\n\\\\")

            pdv_number = []
            for sym in syms:
                if check_unc[sym]:
                    custom_print(
                        f"\\frac{{\\partial {equation_left} }}{{\\partial {output_symbol[sym]} }}",
                        end="&=",
                    )
                    pdv = simplify(diff(equation_right, sym))
                    custom_print(latex_symbol(pdv), end="=")
                    num = pdv.subs(output_number)
                    pdv_number.append(num)
                    custom_print(latex_number(num.evalf(2)), end="\\\\\n")
                else:
                    pdv_number.append(sympify(0))
            custom_print("\\\\")

            custom_print(
                f"\\sigma_{{{equation_left}}}&=\\sqrt{{"
                + "+".join(
                    f"\\left(\\frac{{\\partial {equation_left} }}{{\\partial {output_symbol[sym]} }} {fullunc}\\right)^2"
                    for sym, fullunc in zip(syms, input_fullunc)
                    if check_unc[sym]
                )
                + "}\\\\"
            )
            custom_print(
                "&=\\sqrt{"
                + "+".join(
                    f"\\left({latex_number((num * sympify(output_number[unc])).evalf(2))}\\right)^2"
                    for num, unc in zip(pdv_number, uncs)
                    if sympify(output_number[unc])
                )
                + "}\\\\"
            )
            result_sigma = latex_number(
                sqrt(
                    sum((num * sympify(sigma)) ** 2 for num, sigma in zip(pdv_number, input_sigma))
                ).evalf(self.result_digit["sigma"])
            )
            custom_print("&=", end="")
            if self.result_unit == 1:
                custom_print(result_sigma + "\\\\\n\\\\")
            else:
                custom_print(f"{result_sigma}\\ " + self.result_unit + "\\\\\n\\\\")

            # Result
            if self.result_unit == 1:
                custom_print(f"{equation_left}&={result_mu} \\pm {result_sigma}")
            else:
                custom_print(
                    f"{equation_left}&=\\left ({result_mu} \\pm {result_sigma} \\right )\\ "
                    + self.result_unit
                )
            custom_print(
                """\\end{aligned}
\\end{equation}"""
                if self.include_equation_number
                else """\\end{aligned}
\\end{equation*}"""
            )

        else:
            custom_print(
                "\\begin{equation}" if self.include_equation_number else "\\begin{equation*}"
            )
            custom_print(equation_left, end="=")
            custom_print(latex_symbol(equation_right), end="=")
            result_mu = latex_number(
                equation_right.evalf(self.result_digit["mu"], subs=output_number)
            )
            if self.result_unit == 1:
                custom_print(result_mu)
            else:
                custom_print(f"{result_mu}\\ " + self.result_unit)
            custom_print("\\end{equation}" if self.include_equation_number else "\\end{equation*}")

            pdv_number = []
            custom_print(
                """
\\begin{equation}
\\begin{aligned}"""
                if self.include_equation_number
                else """
\\begin{equation*}
\\begin{aligned}"""
            )
            for sym in syms:
                if check_unc[sym]:
                    custom_print(
                        f"\\frac{{\\partial {equation_left} }}{{\\partial {output_symbol[sym]} }}",
                        end="&=",
                    )
                    pdv = simplify(diff(equation_right, sym))
                    custom_print(latex_symbol(pdv), end="=")
                    num = pdv.subs(output_number)
                    pdv_number.append(num)
                    custom_print(latex_number(num.evalf(2)), end="\\\\\n")
                else:
                    pdv_number.append(sympify(0))
            custom_print(
                """\\end{aligned}
\\end{equation}
"""
                if self.include_equation_number
                else """\\end{aligned}
\\end{equation*}
"""
            )

            custom_print(
                """\\begin{equation}
\\begin{aligned}"""
                if self.include_equation_number
                else """\\begin{equation*}
\\begin{aligned}"""
            )
            custom_print(
                f"\\sigma_{{{equation_left}}}&=\\sqrt{{"
                + "+".join(
                    f"\\left(\\frac{{\\partial {equation_left} }}{{\\partial {output_symbol[sym]} }} {fullunc}\\right)^2"
                    for sym, fullunc in zip(syms, input_fullunc)
                    if check_unc[sym]
                )
                + "}\\\\"
            )
            custom_print(
                "&=\\sqrt{"
                + "+".join(
                    f"\\left({latex_number((num * sympify(output_number[unc])).evalf(2))}\\right)^2"
                    for num, unc in zip(pdv_number, uncs)
                    if sympify(output_number[unc])
                )
                + "}\\\\"
            )
            result_sigma = latex_number(
                sqrt(
                    sum((num * sympify(sigma)) ** 2 for num, sigma in zip(pdv_number, input_sigma))
                ).evalf(self.result_digit["sigma"])
            )
            custom_print("&=", end="")
            if self.result_unit == 1:
                custom_print(result_sigma)
            else:
                custom_print(f"{result_sigma}\\ " + self.result_unit)
            custom_print(
                """\\end{aligned}
\\end{equation}
"""
                if self.include_equation_number
                else """\\end{aligned}
\\end{equation*}
"""
            )

            # Result
            custom_print(
                "\\begin{equation}" if self.include_equation_number else "\\begin{equation*}"
            )
            if self.result_unit == 1:
                custom_print(f"{equation_left}={result_mu} \\pm {result_sigma}")
            else:
                custom_print(
                    f"{equation_left}=\\left ({result_mu} \\pm {result_sigma} \\right )\\ "
                    + self.result_unit
                )
            custom_print("\\end{equation}" if self.include_equation_number else "\\end{equation*}")

        return output_buffer.getvalue()
