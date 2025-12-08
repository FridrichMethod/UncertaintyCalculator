# Copyright https://github.com/FridrichMethod.

"""Legacy calculator implementation for testing purposes."""

import builtins
import io

from sympy import diff, latex, simplify, sqrt, symbols, sympify


def run_legacy_calculator(  # noqa: C901
    equation: list[str],
    variables: list[tuple[str, str]],
    digits: dict[str, int],
    last_unit: str | int,
    separate: bool,
    insert: bool,
    include_equation_number: bool,
):
    """Run the legacy calculator logic."""
    output_buffer = io.StringIO()

    def _print(*args, **kwargs):
        kwargs["file"] = output_buffer
        kwargs["sep"] = kwargs.get("sep", " ")
        kwargs["end"] = kwargs.get("end", "\n")
        builtins.print(*args, **kwargs)

    # Parse

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

    for x in variables:
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
    equation_left = equation[0]
    equation_right = sympify(equation[1])

    # Print

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

    if insert:
        if not separate:
            _print(
                """\\begin{equation}
\\begin{aligned}"""
                if include_equation_number
                else """\\begin{equation*}
\\begin{aligned}"""
            )
            _print(equation_left, end="&=")
            _print(latex_symbol(equation_right), end="=")
            _print(latex_value(equation_right), end="=")
            result_mu = latex_number(equation_right.evalf(digits["mu"], subs=output_number))
            if last_unit == 1:
                _print(result_mu + "\\\\\n\\\\")
            else:
                _print(f"{result_mu}\\ " + last_unit + "\\\\\n\\\\")

            pdv_number = []
            for sym in syms:
                if check_unc[sym]:
                    _print(
                        f"\\frac{{\\partial {equation_left} }}{{\\partial {output_symbol[sym]} }}",
                        end="&=",
                    )
                    pdv = simplify(diff(equation_right, sym))
                    _print(latex_symbol(pdv), end="=")
                    _print(latex_value(pdv), end="=")
                    num = pdv.subs(output_number)
                    pdv_number.append(num)
                    _print(latex_number(num.evalf(2)), end="\\\\\n")
                else:
                    pdv_number.append(sympify(0))
            _print("\\\\")

            _print(
                f"\\sigma_{{{equation_left}}}&=\\sqrt{{"
                + "+".join(
                    f"\\left(\\frac{{\\partial {equation_left} }}{{\\partial {output_symbol[sym]} }} {fullunc}\\right)^2"
                    for sym, fullunc in zip(syms, input_fullunc)
                    if check_unc[sym]
                )
                + "}\\\\"
            )
            _print(
                "&=\\sqrt{"
                + "+".join(
                    f"\\left({latex_number(num.evalf(2))} \\times {output_value[unc]}\\right)^2"
                    for num, unc in zip(pdv_number, uncs)
                    if sympify(output_number[unc])
                )
                + "}\\\\"
            )
            _print(
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
                ).evalf(digits["sigma"])
            )
            _print("&=", end="")
            if last_unit == 1:
                _print(result_sigma + "\\\\\n\\\\")
            else:
                _print(f"{result_sigma}\\ " + last_unit + "\\\\\n\\\\")

            # Result

            if last_unit == 1:
                _print(f"{equation_left}&={result_mu} \\pm {result_sigma}")
            else:
                _print(
                    f"{equation_left}&=\\left ({result_mu} \\pm {result_sigma} \\right )\\ "
                    + last_unit
                )
            _print(
                """\\end{aligned}
\\end{equation}"""
                if include_equation_number
                else """\\end{aligned}
\\end{equation*}"""
            )

        else:
            _print("\\begin{equation}" if include_equation_number else "\\begin{equation*}")
            _print(equation_left, end="=")
            _print(latex_symbol(equation_right), end="=")
            _print(latex_value(equation_right), end="=")
            result_mu = latex_number(equation_right.evalf(digits["mu"], subs=output_number))
            if last_unit == 1:
                _print(result_mu)
            else:
                _print(f"{result_mu}\\ " + last_unit)
            _print("\\end{equation}" if include_equation_number else "\\end{equation*}")

            pdv_number = []
            _print(
                """
\\begin{equation}
\\begin{aligned}"""
                if include_equation_number
                else """
\\begin{equation*}
\\begin{aligned}"""
            )
            for sym in syms:
                if check_unc[sym]:
                    _print(
                        f"\\frac{{\\partial {equation_left} }}{{\\partial {output_symbol[sym]} }}",
                        end="&=",
                    )
                    pdv = simplify(diff(equation_right, sym))
                    _print(latex_symbol(pdv), end="=")
                    _print(latex_value(pdv), end="=")
                    num = pdv.subs(output_number)
                    pdv_number.append(num)
                    _print(latex_number(num.evalf(2)), end="\\\\\n")
                else:
                    pdv_number.append(sympify(0))
            _print(
                """\\end{aligned}
\\end{equation}
"""
                if include_equation_number
                else """\\end{aligned}
\\end{equation*}
"""
            )

            _print(
                """\\begin{equation}
\\begin{aligned}"""
                if include_equation_number
                else """\\begin{equation*}
\\begin{aligned}"""
            )
            _print(
                f"\\sigma_{{{equation_left}}}&=\\sqrt{{"
                + "+".join(
                    f"\\left(\\frac{{\\partial {equation_left} }}{{\\partial {output_symbol[sym]} }} {fullunc}\\right)^2"
                    for sym, fullunc in zip(syms, input_fullunc)
                    if check_unc[sym]
                )
                + "}\\\\"
            )
            _print(
                "&=\\sqrt{"
                + "+".join(
                    f"\\left({latex_number(num.evalf(2))} \\times {output_value[unc]}\\right)^2"
                    for num, unc in zip(pdv_number, uncs)
                    if sympify(output_number[unc])
                )
                + "}\\\\"
            )
            _print(
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
                ).evalf(digits["sigma"])
            )
            _print("&=", end="")
            if last_unit == 1:
                _print(result_sigma)
            else:
                _print(f"{result_sigma}\\ " + last_unit)
            _print(
                """\\end{aligned}
\\end{equation}
"""
                if include_equation_number
                else """\\end{aligned}
\\end{equation*}
"""
            )

            # Result

            _print("\\begin{equation}" if include_equation_number else "\\begin{equation*}")
            if last_unit == 1:
                _print(f"{equation_left}={result_mu} \\pm {result_sigma}")
            else:
                _print(
                    f"{equation_left}=\\left ({result_mu} \\pm {result_sigma} \\right )\\ "
                    + last_unit
                )
            _print("\\end{equation}" if include_equation_number else "\\end{equation*}")

    elif not separate:
        _print(
            """\\begin{equation}
\\begin{aligned}"""
            if include_equation_number
            else """\\begin{equation*}
\\begin{aligned}"""
        )
        _print(equation_left, end="&=")
        _print(latex_symbol(equation_right), end="=")
        result_mu = latex_number(equation_right.evalf(digits["mu"], subs=output_number))
        if last_unit == 1:
            _print(result_mu + "\\\\\n\\\\")
        else:
            _print(f"{result_mu}\\ " + last_unit + "\\\\\n\\\\")

        pdv_number = []
        for sym in syms:
            if check_unc[sym]:
                _print(
                    f"\\frac{{\\partial {equation_left} }}{{\\partial {output_symbol[sym]} }}",
                    end="&=",
                )
                pdv = simplify(diff(equation_right, sym))
                _print(latex_symbol(pdv), end="=")
                num = pdv.subs(output_number)
                pdv_number.append(num)
                _print(latex_number(num.evalf(2)), end="\\\\\n")
            else:
                pdv_number.append(sympify(0))
        _print("\\\\")

        _print(
            f"\\sigma_{{{equation_left}}}&=\\sqrt{{"
            + "+".join(
                f"\\left(\\frac{{\\partial {equation_left} }}{{\\partial {output_symbol[sym]} }} {fullunc}\\right)^2"
                for sym, fullunc in zip(syms, input_fullunc)
                if check_unc[sym]
            )
            + "}\\\\"
        )
        _print(
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
            ).evalf(digits["sigma"])
        )
        _print("&=", end="")
        if last_unit == 1:
            _print(result_sigma + "\\\\\n\\\\")
        else:
            _print(f"{result_sigma}\\ " + last_unit + "\\\\\n\\\\")

        # Result

        if last_unit == 1:
            _print(f"{equation_left}&={result_mu} \\pm {result_sigma}")
        else:
            _print(
                f"{equation_left}&=\\left ({result_mu} \\pm {result_sigma} \\right )\\ " + last_unit
            )
        _print(
            """\\end{aligned}
\\end{equation}"""
            if include_equation_number
            else """\\end{aligned}
\\end{equation*}"""
        )

    else:
        _print("\\begin{equation}" if include_equation_number else "\\begin{equation*}")
        _print(equation_left, end="=")
        _print(latex_symbol(equation_right), end="=")
        result_mu = latex_number(equation_right.evalf(digits["mu"], subs=output_number))
        if last_unit == 1:
            _print(result_mu)
        else:
            _print(f"{result_mu}\\ " + last_unit)
        _print("\\end{equation}" if include_equation_number else "\\end{equation*}")

        pdv_number = []
        _print(
            """
\\begin{equation}
\\begin{aligned}"""
            if include_equation_number
            else """
\\begin{equation*}
\\begin{aligned}"""
        )
        for sym in syms:
            if check_unc[sym]:
                _print(
                    f"\\frac{{\\partial {equation_left} }}{{\\partial {output_symbol[sym]} }}",
                    end="&=",
                )
                pdv = simplify(diff(equation_right, sym))
                _print(latex_symbol(pdv), end="=")
                num = pdv.subs(output_number)
                pdv_number.append(num)
                _print(latex_number(num.evalf(2)), end="\\\\\n")
            else:
                pdv_number.append(sympify(0))
        _print(
            """\\end{aligned}
\\end{equation}
"""
            if include_equation_number
            else """\\end{aligned}
\\end{equation*}
"""
        )

        _print(
            """\\begin{equation}
\\begin{aligned}"""
            if include_equation_number
            else """\\begin{equation*}
\\begin{aligned}"""
        )
        _print(
            f"\\sigma_{{{equation_left}}}&=\\sqrt{{"
            + "+".join(
                f"\\left(\\frac{{\\partial {equation_left} }}{{\\partial {output_symbol[sym]} }} {fullunc}\\right)^2"
                for sym, fullunc in zip(syms, input_fullunc)
                if check_unc[sym]
            )
            + "}\\\\"
        )
        _print(
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
            ).evalf(digits["sigma"])
        )
        _print("&=", end="")
        if last_unit == 1:
            _print(result_sigma)
        else:
            _print(f"{result_sigma}\\ " + last_unit)
        _print(
            """\\end{aligned}
\\end{equation}
"""
            if include_equation_number
            else """\\end{aligned}
\\end{equation*}
"""
        )

        # Result

        _print("\\begin{equation}" if include_equation_number else "\\begin{equation*}")
        if last_unit == 1:
            _print(f"{equation_left}={result_mu} \\pm {result_sigma}")
        else:
            _print(
                f"{equation_left}=\\left ({result_mu} \\pm {result_sigma} \\right )\\ " + last_unit
            )
        _print("\\end{equation}" if include_equation_number else "\\end{equation*}")

    return output_buffer.getvalue()
