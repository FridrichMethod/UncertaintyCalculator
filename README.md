# Uncertainty Calculator

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg?logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3120/) [![CI Status](https://github.com/fridrichmethod/UncertaintyCalculator/workflows/CI/badge.svg)](https://github.com/fridrichmethod/UncertaintyCalculator/actions) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/FridrichMethod/UncertaintyCalculator/blob/main/calculator.ipynb)

<div align="center" style="margin: 2em 0;">
  <div style="background-color: #f6f8fa; border: 1px solid #d0d7de; border-radius: 6px; padding: 1.5em; max-width: 600px;">
    <p style="margin: 0; font-size: 1.1em; color: #24292f; line-height: 1.6; font-style: italic;">
      "Help you get rid of the <strong>Physical Chemistry Experiment</strong> course in CCME at PKU!"
    </p>
  </div>
</div>

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

### Install via uv

```shell
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e .[dev]
```

## Usage

The calculator is designed to be used as a Python module. Below is a complete example of how to configure and run calculation.

### 1. Define the Equation

The equation is defined as a list of strings containing the left-hand side (variable name) and the right-hand side (expression).

```python
# Define equation
equation = [r"\zeta", r"(K*pi*eta*u*l)/(4*pi*phi*e_0*e_r)"]
```

### 2. Define Variables

Variables are defined as a list of tuples. Each tuple contains:

1. A string defining the variable's value and uncertainty (`symbol = value +- uncertainty`).
2. The LaTeX representation of the variable symbol.

```python
# Define variables
variables = [
    ("K = 4 +- 0", r"K"),
    ("eta = 0.9358e-3 +- 0.0001/sqrt(3)", r"\eta"),
    ("u = 3.68e-5 +- 0.11e-5", r"u"),
    ("l = 0.2256 +- 0.0019", r"l"),
    ("phi = 100 +- 1/sqrt(3)", r"\varphi"),
    ("e_0 = 8.8541878128e-12 +- 0", r"\varepsilon_0"),
    ("e_r = 78.7 +- 0.1/sqrt(3)", r"\varepsilon_\text{r}"),
]
```

### 3. Configuration

Configure the output format, precision, and units.

```python
# Set digits of results
digits = {
    "mu": 3,
    "sigma": 3,
}

# Set units of results
last_unit = r"\text{V}"

# Print separately or integrally
separate = False

# Insert numbers or not
insert = False

# Include equation number or not
include_equation_number = True
```

### 4. Run the Calculator

Import the `UncertaintyCalculator` and execute the calculation.

```python
from uncertainty_calculator import UncertaintyCalculator

calculator = UncertaintyCalculator(
    equation=equation,
    variables=variables,
    digits=digits,
    last_unit=last_unit,
    separate=separate,
    insert=insert,
    include_equation_number=include_equation_number,
)

latex_string = calculator.run()

print(latex_string)
```

### 5. Render the LaTeX String

```python
from IPython.display import Latex

Latex(latex_string)
```

## Output Example

The tool generates LaTeX code that renders to standard physical chemistry calculation steps:

```latex
\begin{equation}
\begin{aligned}
\zeta&=\frac{K \eta l u}{4 \varepsilon_0 \varepsilon_\text{r} \varphi}=0.111\ \text{V}\\
\\
\frac{\partial \zeta }{\partial \eta }&=\frac{K l u}{4 \varepsilon_0 \varepsilon_\text{r} \varphi}=1.2 \times 10^{2}\\
\frac{\partial \zeta }{\partial u }&=\frac{K \eta l}{4 \varepsilon_0 \varepsilon_\text{r} \varphi}=3.0 \times 10^{3}\\
\frac{\partial \zeta }{\partial l }&=\frac{K \eta u}{4 \varepsilon_0 \varepsilon_\text{r} \varphi}=0.49\\
\frac{\partial \zeta }{\partial \varphi }&=- \frac{K \eta l u}{4 \varepsilon_0 \varepsilon_\text{r} \varphi^{2}}=-0.0011\\
\frac{\partial \zeta }{\partial \varepsilon_\text{r} }&=- \frac{K \eta l u}{4 \varepsilon_0 \varepsilon_\text{r}^{2} \varphi}=-0.0014\\
\\
\sigma_{\zeta}&=\sqrt{\left(\frac{\partial \zeta }{\partial \eta } \sigma_{\eta}\right)^2+\left(\frac{\partial \zeta }{\partial u } \sigma_{u}\right)^2+\left(\frac{\partial \zeta }{\partial l } \sigma_{l}\right)^2+\left(\frac{\partial \zeta }{\partial \varphi } \sigma_{\varphi}\right)^2+\left(\frac{\partial \zeta }{\partial \varepsilon_\text{r} } \sigma_{\varepsilon_\text{r}}\right)^2}\\
&=\sqrt{\left(0.0069\right)^2+\left(0.0033\right)^2+\left(0.00094\right)^2+\left(-0.00064\right)^2+\left(-8.2 \times 10^{-5}\right)^2}\\
&=0.00773\ \text{V}\\
\\
\zeta&=\left (0.111 \pm 0.00773 \right )\ \text{V}
\end{aligned}
\end{equation}
```

Rendered results:

![Rendered results](./assets/latex_rendered.png)

## Acknowledgements

- **SymPy**: [https://github.com/sympy/sympy](https://github.com/sympy/sympy)
- **LaTeX Live**: [https://latexlive.com](https://latexlive.com)

## License

This project is licensed under the MIT License.
