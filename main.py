# Copyright https://github.com/FridrichMethod.

"""Uncertainty Calculator Entry Point."""

from uncertainty_calculator import UncertaintyCalculator

# Input

# Define equation
equation = [x.strip() for x in [r"\zeta ", r" (K*pi*eta*u*l)/(4*pi*phi*e_0*e_r)"]]

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


def main() -> None:
    """Main function to run the calculator."""
    calculator = UncertaintyCalculator(
        equation=equation,
        variable=variable,
        result_digit=result_digit,
        result_unit=result_unit,
        separate=separate,
        insert=insert,
        include_equation_number=include_equation_number,
    )
    print(calculator.run(), end="")


if __name__ == "__main__":
    main()
