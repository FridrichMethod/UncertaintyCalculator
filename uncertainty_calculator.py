# -*- coding:utf-8 -*-
# Copyright @FridrichMethod

from sympy import *

# Input

# Define equation
equation = [
    x.strip() for x in
    r"\zeta = (K*pi*eta*u*l)/(4*pi*phi*e_0*e_r)"
    .split("=")
]

# Define variable
variable = [
    ("K = 4 +- 0", r"K"),
    ("eta = 0.9358e-3 +- 0.0001/sqrt(3)", r"\eta"),
    ("u = 3.68e-5 +- 0.11e-5", r"u"),
    ("l = 0.2256 +- 0.0019", r"l"),
    ("phi = 100 +- 1/sqrt(3)", r"\varphi"),
    ("e_0 = 8.8541878128e-12 +- 0", r"\varepsilon_0"),
    ("e_r = 78.7 +- 0.1/sqrt(3)", r"\varepsilon_\text{r}"),
]

# Set digits of results
result_digit = {
    "mu": 3,
    "sigma": 3,
}

# Set units of results
result_unit = r"\si{V}"

# Print separately or integrally
separate = 0

# Insert numbers or not
insert = 0

# Include equation number or not
include_equation_number = 1

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


for x in variable:
    input_symbol = x[0].split("=")
    input_value = input_symbol[1].split("+-")
    input_sym.append(input_symbol[0].strip())
    input_unc.append(f"sigma_{input_symbol[0].strip()}")
    input_fullsym.append(x[1].strip())
    input_fullunc.append(f"\\sigma_{{{x[1].strip()}}}")
    input_mu.append(input_value[0].strip())
    input_sigma.append(input_value[1].strip())
    input_fullmu.append(
        f"\\left({latex_number(sympify(input_value[0].strip()))}\\right)"
    )
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
        print(
            """\\begin{equation}
\\begin{aligned}"""
            if include_equation_number
            else """\\begin{equation*}
\\begin{aligned}"""
        )
        print(equation_left, end="&=")
        print(latex_symbol(equation_right), end="=")
        print(latex_value(equation_right), end="=")
        result_mu = latex_number(
            equation_right.evalf(result_digit["mu"], subs=output_number)
        )
        if result_unit == 1:
            print(result_mu + "\\\\\n\\\\")
        else:
            print(f"{result_mu}\\ " + result_unit + "\\\\\n\\\\")

        pdv_number = []
        for sym in syms:
            if check_unc[sym]:
                print(
                    f"\\frac{{\\partial {equation_left} }}{{\\partial {output_symbol[sym]} }}",
                    end="&=",
                )
                pdv = simplify(diff(equation_right, sym))
                print(latex_symbol(pdv), end="=")
                print(latex_value(pdv), end="=")
                num = pdv.subs(output_number)
                pdv_number.append(num)
                print(latex_number(num.evalf(2)), end="\\\\\n")
            else:
                pdv_number.append(sympify(0))
        print("\\\\")

        print(
            f"\\sigma_{{{equation_left}}}&=\\sqrt{{"
            + "+".join(
                f"\\left(\\frac{{\\partial {equation_left} }}{{\\partial {output_symbol[sym]} }} {fullunc}\\right)^2"
                for sym, fullunc in zip(syms, input_fullunc)
                if check_unc[sym]
            )
            + "}\\\\"
        )
        print(
            "&=\\sqrt{"
            + "+".join(
                f"\\left({latex_number(num.evalf(2))} \\times {output_value[unc]}\\right)^2"
                for num, unc in zip(pdv_number, uncs)
                if sympify(output_number[unc])
            )
            + "}\\\\"
        )
        print(
            "&=\\sqrt{"
            + "+".join(
                f"\\left({latex_number((num*sympify(output_number[unc])).evalf(2))}\\right)^2"
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
            ).evalf(result_digit["sigma"])
        )
        print("&=", end="")
        if result_unit == 1:
            print(result_sigma + "\\\\\n\\\\")
        else:
            print(f"{result_sigma}\\ " + result_unit + "\\\\\n\\\\")

        # Result

        if result_unit == 1:
            print(f"{equation_left}&={result_mu} \\pm {result_sigma}")
        else:
            print(
                f"{equation_left}&=\\left ({result_mu} \\pm {result_sigma} \\right )\\ "
                + result_unit
            )
        print(
            """\\end{aligned}
\\end{equation}"""
            if include_equation_number
            else """\\end{aligned}
\\end{equation*}"""
        )

    else:
        print("\\begin{equation}" if include_equation_number else "\\begin{equation*}")
        print(equation_left, end="=")
        print(latex_symbol(equation_right), end="=")
        print(latex_value(equation_right), end="=")
        result_mu = latex_number(
            equation_right.evalf(result_digit["mu"], subs=output_number)
        )
        if result_unit == 1:
            print(result_mu)
        else:
            print(f"{result_mu}\\ " + result_unit)
        print("\\end{equation}" if include_equation_number else "\\end{equation*}")

        pdv_number = []
        print(
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
                print(
                    f"\\frac{{\\partial {equation_left} }}{{\\partial {output_symbol[sym]} }}",
                    end="&=",
                )
                pdv = simplify(diff(equation_right, sym))
                print(latex_symbol(pdv), end="=")
                print(latex_value(pdv), end="=")
                num = pdv.subs(output_number)
                pdv_number.append(num)
                print(latex_number(num.evalf(2)), end="\\\\\n")
            else:
                pdv_number.append(sympify(0))
        print(
            """\\end{aligned}
\\end{equation}
"""
            if include_equation_number
            else """\\end{aligned}
\\end{equation*}
"""
        )

        print(
            """\\begin{equation}
\\begin{aligned}"""
            if include_equation_number
            else """\\begin{equation*}
\\begin{aligned}"""
        )
        print(
            f"\\sigma_{{{equation_left}}}&=\\sqrt{{"
            + "+".join(
                f"\\left(\\frac{{\\partial {equation_left} }}{{\\partial {output_symbol[sym]} }} {fullunc}\\right)^2"
                for sym, fullunc in zip(syms, input_fullunc)
                if check_unc[sym]
            )
            + "}\\\\"
        )
        print(
            "&=\\sqrt{"
            + "+".join(
                f"\\left({latex_number(num.evalf(2))} \\times {output_value[unc]}\\right)^2"
                for num, unc in zip(pdv_number, uncs)
                if sympify(output_number[unc])
            )
            + "}\\\\"
        )
        print(
            "&=\\sqrt{"
            + "+".join(
                f"\\left({latex_number((num*sympify(output_number[unc])).evalf(2))}\\right)^2"
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
            ).evalf(result_digit["sigma"])
        )
        print("&=", end="")
        if result_unit == 1:
            print(result_sigma)
        else:
            print(f"{result_sigma}\\ " + result_unit)
        print(
            """\\end{aligned}
\\end{equation}
"""
            if include_equation_number
            else """\\end{aligned}
\\end{equation*}
"""
        )

        # Result

        print("\\begin{equation}" if include_equation_number else "\\begin{equation*}")
        if result_unit == 1:
            print(f"{equation_left}={result_mu} \\pm {result_sigma}")
        else:
            print(
                f"{equation_left}=\\left ({result_mu} \\pm {result_sigma} \\right )\\ "
                + result_unit
            )
        print("\\end{equation}" if include_equation_number else "\\end{equation}*")

else:
    if not separate:
        print(
            """\\begin{equation}
\\begin{aligned}"""
            if include_equation_number
            else """\\begin{equation*}
\\begin{aligned}"""
        )
        print(equation_left, end="&=")
        print(latex_symbol(equation_right), end="=")
        result_mu = latex_number(
            equation_right.evalf(result_digit["mu"], subs=output_number)
        )
        if result_unit == 1:
            print(result_mu + "\\\\\n\\\\")
        else:
            print(f"{result_mu}\\ " + result_unit + "\\\\\n\\\\")

        pdv_number = []
        for sym in syms:
            if check_unc[sym]:
                print(
                    f"\\frac{{\\partial {equation_left} }}{{\\partial {output_symbol[sym]} }}",
                    end="&=",
                )
                pdv = simplify(diff(equation_right, sym))
                print(latex_symbol(pdv), end="=")
                num = pdv.subs(output_number)
                pdv_number.append(num)
                print(latex_number(num.evalf(2)), end="\\\\\n")
            else:
                pdv_number.append(sympify(0))
        print("\\\\")

        print(
            f"\\sigma_{{{equation_left}}}&=\\sqrt{{"
            + "+".join(
                f"\\left(\\frac{{\\partial {equation_left} }}{{\\partial {output_symbol[sym]} }} {fullunc}\\right)^2"
                for sym, fullunc in zip(syms, input_fullunc)
                if check_unc[sym]
            )
            + "}\\\\"
        )
        print(
            "&=\\sqrt{"
            + "+".join(
                f"\\left({latex_number((num*sympify(output_number[unc])).evalf(2))}\\right)^2"
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
            ).evalf(result_digit["sigma"])
        )
        print("&=", end="")
        if result_unit == 1:
            print(result_sigma + "\\\\\n\\\\")
        else:
            print(f"{result_sigma}\\ " + result_unit + "\\\\\n\\\\")

        # Result

        if result_unit == 1:
            print(f"{equation_left}&={result_mu} \\pm {result_sigma}")
        else:
            print(
                f"{equation_left}&=\\left ({result_mu} \\pm {result_sigma} \\right )\\ "
                + result_unit
            )
        print(
            """\\end{aligned}
\\end{equation}"""
            if include_equation_number
            else """\\end{aligned}
\\end{equation*}"""
        )

    else:
        print("\\begin{equation}" if include_equation_number else "\\begin{equation*}")
        print(equation_left, end="=")
        print(latex_symbol(equation_right), end="=")
        result_mu = latex_number(
            equation_right.evalf(result_digit["mu"], subs=output_number)
        )
        if result_unit == 1:
            print(result_mu)
        else:
            print(f"{result_mu}\\ " + result_unit)
        print("\\end{equation}" if include_equation_number else "\\end{equation*}")

        pdv_number = []
        print(
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
                print(
                    f"\\frac{{\\partial {equation_left} }}{{\\partial {output_symbol[sym]} }}",
                    end="&=",
                )
                pdv = simplify(diff(equation_right, sym))
                print(latex_symbol(pdv), end="=")
                num = pdv.subs(output_number)
                pdv_number.append(num)
                print(latex_number(num.evalf(2)), end="\\\\\n")
            else:
                pdv_number.append(sympify(0))
        print(
            """\\end{aligned}
\\end{equation}
"""
            if include_equation_number
            else """\\end{aligned}
\\end{equation*}
"""
        )

        print(
            """\\begin{equation}
\\begin{aligned}"""
            if include_equation_number
            else """\\begin{equation*}
\\begin{aligned}"""
        )
        print(
            f"\\sigma_{{{equation_left}}}&=\\sqrt{{"
            + "+".join(
                f"\\left(\\frac{{\\partial {equation_left} }}{{\\partial {output_symbol[sym]} }} {fullunc}\\right)^2"
                for sym, fullunc in zip(syms, input_fullunc)
                if check_unc[sym]
            )
            + "}\\\\"
        )
        print(
            "&=\\sqrt{"
            + "+".join(
                f"\\left({latex_number((num*sympify(output_number[unc])).evalf(2))}\\right)^2"
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
            ).evalf(result_digit["sigma"])
        )
        print("&=", end="")
        if result_unit == 1:
            print(result_sigma)
        else:
            print(f"{result_sigma}\\ " + result_unit)
        print(
            """\\end{aligned}
\\end{equation}
"""
            if include_equation_number
            else """\\end{aligned}
\\end{equation*}
"""
        )

        # Result

        print("\\begin{equation}" if include_equation_number else "\\begin{equation*}")
        if result_unit == 1:
            print(f"{equation_left}={result_mu} \\pm {result_sigma}")
        else:
            print(
                f"{equation_left}=\\left ({result_mu} \\pm {result_sigma} \\right )\\ "
                + result_unit
            )
        print("\\end{equation}" if include_equation_number else "\\end{equation*}")
