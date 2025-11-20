# Uncertainty Calculator

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/badge/Python-3.12+-blue.svg?logo=python&logoColor=white)](https://python.org/downloads)

A Python tool for automated error propagation in physical experiments. This calculator uses symbolic differentiation to compute partial derivatives and propagate uncertainties, generating detailed LaTeX output for your reports.

## Features

- **Symbolic Differentiation**: Automatically calculates partial derivatives using `sympy`.
- **Automated Error Propagation**: Computes the final uncertainty based on the standard error propagation formula.
- **LaTeX Output**: Generates ready-to-use LaTeX code for equations, derivatives, and substitution steps.
- **Customizable**: Configurable decimal precision, units, and output formatting.

## Installation

### Requirements

- Python 3.12+
- `sympy`

### Install via pip

```shell
conda create -n uncertainty-calculator python=3.12 -y
conda activate uncertainty-calculator

pip install uv
uv pip install -e .
```

## Usage

The calculator is designed to be used as a Python module. Below is a complete example of how to configure and run calculation.

### 1. Define the Equation

The equation is defined as a list of strings containing the left-hand side (variable name) and the right-hand side (expression).

```python
# Example: W = (-Q_V * m - Q_N - Q_M) / Dt - rho * V * C
equation = [
    x.strip() for x in
    r'W = (-Q_V*m-Q_N-Q_M)/Dt-rho*V*C'.split('=')
]
```

### 2. Define Variables

Variables are defined as a list of tuples. Each tuple contains:

1. A string defining the variable's value and uncertainty (`symbol = value +- uncertainty`).
2. The LaTeX representation of the variable symbol.

```python
variables = [
    ('Q_V = -26.414 +- 0', r'Q_V'),
    ('m = 0.9547 +- 0.0004/sqrt(3)', r'm'),
    ('Q_N = -0.323 +- 3.243*0.0004/sqrt(3)', r'Q_\ce{Ni}'),
    ('Q_M = -0.01 +- 0.0002*16.736/sqrt(3)', r'Q_\text{cotton}'),
    ('rho = 0.99865 +- 0', r'\rho_\ce{H2O}'),
    ('V = 3000 +- 0.01', r'V'),
    ('C = 4.1824e-3 +- 0', r'C_\ce{H2O}'),
    ('Dt = 1.770 +- 0.009', r'\Delta T'),
]

```

### 3. Configuration

Configure the output format, precision, and units.

```python
# Precision for result (mu) and uncertainty (sigma)
digits = {
    'mu': 4,
    'sigma': 2,
}

# Final unit string in LaTeX (use 1 for dimensionless)
last_unit = r'\text{kJ}/{}^\circ\text{C}'

# Formatting flags
separate = 1                # 1: Separate blocks, 0: Combined block
insert = 1                  # 1: Show intermediate substitution steps
include_equation_number = 1 # 1: Use numbered equations, 0: Use unnumbered (equation*)
```

### 4. Run the Calculator

Import the `UncertaintyCalculator` and execute the calculation.

```python
from uncertainty_calculator import UncertaintyCalculator

def main():
    calculator = UncertaintyCalculator(
        equation=equation,
        variables=variables,
        digits=digits,
        last_unit=last_unit,
        separate=separate,
        insert=insert,
        include_equation_number=include_equation_number
    )
    
    # Print the generated LaTeX code
    print(calculator.run(), end="")

if __name__ == "__main__":
    main()
```

## Output Example

The tool generates LaTeX code that renders to standard physical chemistry calculation steps:

```latex
\begin{equation}
W=- C_\ce{H2O} V \rho_\ce{H2O} + \frac{- Q_\text{cotton} - Q_\ce{Ni} - Q_V m}{\Delta T}=- \left(0.0041824\right) \times \left(3000\right) \times \left(0.99865\right) + \frac{- \left(-0.01\right) - \left(-0.323\right) - \left(-26.414\right) \times \left(0.9547\right)}{\left(1.77\right)}=1.905\ \text{kJ}/{}^\circ\text{C}
\end{equation}

\begin{equation}
\begin{aligned}
\frac{\partial W }{\partial m }&=- \frac{Q_V}{\Delta T}=- \frac{\left(-26.414\right)}{\left(1.77\right)}=15.0\\
\frac{\partial W }{\partial Q_\ce{Ni} }&=- \frac{1}{\Delta T}=- \frac{1}{\left(1.77\right)}=-0.57\\
\dots
\end{aligned}
\end{equation}

\begin{equation}
\begin{aligned}
\sigma_{W}&=\sqrt{\left(\frac{\partial W }{\partial m } \sigma_{m}\right)^2+\dots}\\
&=0.073\ \text{kJ}/{}^\circ\text{C}
\end{aligned}
\end{equation}

\begin{equation}
W=\left (1.905 \pm 0.073 \right )\ \text{kJ}/{}^\circ\text{C}
\end{equation}
```

## Acknowledgements

- **SymPy**: [https://github.com/sympy/sympy](https://github.com/sympy/sympy)
- **LaTeX Live**: [https://latexlive.com](https://latexlive.com)

## License

This project is licensed under the MIT License.
