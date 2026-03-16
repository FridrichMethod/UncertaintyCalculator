# Uncertainty Calculator

<p align="left">
  <a href="https://www.python.org/downloads/release/python-3120/"><img alt="Python 3.12+" src="https://img.shields.io/badge/Python-3.12+-blue.svg?logo=python&logoColor=white"></a>
  <a href="https://github.com/fridrichmethod/UncertaintyCalculator/actions"><img alt="CI Status" src="https://github.com/fridrichmethod/UncertaintyCalculator/workflows/CI/badge.svg"></a>
  <a href="https://github.com/astral-sh/ruff"><img alt="Code style: ruff" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json"></a>
  <a href="https://mypy-lang.org/"><img alt="Checked with mypy" src="https://www.mypy-lang.org/static/mypy_badge.svg"></a>
  <a href="https://github.com/pre-commit/pre-commit"><img alt="pre-commit" src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit"></a>
  <a href="https://opensource.org/licenses/MIT"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
  <a href="https://colab.research.google.com/github/FridrichMethod/UncertaintyCalculator/blob/main/examples/uncertainty_calculator.ipynb"><img alt="Open in Colab" src="https://colab.research.google.com/assets/colab-badge.svg"></a>
</p>

> *"Help you get rid of the **Physical Chemistry Experiment** course in CCME at PKU!"*

A Python tool for automated error propagation in physical experiments. This calculator uses symbolic differentiation to compute partial derivatives and propagate uncertainties, generating detailed LaTeX output for your reports.

---

## 📑 Table of Contents

- [✨ Features](#-features)
- [🚀 Installation](#-installation)
- [📖 Usage](#-usage)
  - [Code layout](#code-layout)
  - [1. Define the Equation](#1-define-the-equation)
  - [2. Define Variables](#2-define-variables)
  - [3. Configuration](#3-configuration)
  - [4. Run the Calculator](#4-run-the-calculator)
  - [5. Render the LaTeX String](#5-render-the-latex-string)
- [📊 Output Example](#-output-example)
- [🙌 Acknowledgements](#-acknowledgements)
- [📄 License](#-license)

## ✨ Features

- **Symbolic Differentiation**: Automatically calculates partial derivatives using `sympy`.
- **Automated Error Propagation**: Computes the final uncertainty based on the standard error propagation formula.
- **LaTeX Output**: Generates ready-to-use LaTeX code for equations, derivatives, and substitution steps.
- **Customizable**: Configurable decimal precision, units, and output formatting.

## 🚀 Installation

### Requirements

- **Python**: `3.12+`
- **Dependencies**: `sympy`

### Install via `uv`

We recommend using [`uv`](https://github.com/astral-sh/uv) for fast environment management:

```shell
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e .[dev]
```

## 📖 Usage

The calculator is designed to be used as a Python module. Below is a complete example of how to configure and run calculation.

### Code layout

The core logic is organized by responsibility:

- `calculator.py`: orchestrates the pipeline
- `parsers.py`: builds symbols/mappings from inputs
- `compute.py`: performs derivatives and numeric propagation
- `render.py`: produces LaTeX output
- `_types.py`: input dataclasses and type aliases
- `format.py` / `validation.py`: shared helpers

### 1. Define the Equation

The equation can be defined using the `Equation` class. `latex_name` is the rendered result symbol, while `expression` is the internal symbolic formula written with variable `name`s.

```python
from uncertainty_calculator import Equation

# Define equation
equation = Equation(
    latex_name=r"\zeta",
    expression=r"(K*pi*eta*u*l)/(4*pi*phi*e_0*e_r)",
)
```

### 2. Define Variables

Variables can be defined using the `Variable` class for structured input.

```python
from uncertainty_calculator import Variable

# Define variables
variables = [
    Variable(name="K", value=4.0, uncertainty=0.0, latex_name="K"),
    Variable(name="eta", value=0.9358e-3, uncertainty=5.773502691896258e-05, latex_name=r"\eta"),
    Variable(name="u", value=3.68e-5, uncertainty=0.11e-5, latex_name="u"),
    Variable(name="l", value=0.2256, uncertainty=0.0019, latex_name="l"),
    Variable(name="phi", value=100.0, uncertainty=0.5773502691896257, latex_name=r"\varphi"),
    Variable(name="e_0", value=8.8541878128e-12, uncertainty=0.0, latex_name=r"\varepsilon_0"),
    Variable(
        name="e_r", value=78.7, uncertainty=0.057735026918962574, latex_name=r"\varepsilon_\text{r}"
    ),
]
```

### 3. Configuration

Configure the output format, precision, and units.

```python
from uncertainty_calculator import Digits

# Set digits of results
digits = Digits(mu=3, sigma=3)

# Set units of results
last_unit = r"\text{V}"  # Use None if dimensionless
# last_unit = None

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
    digits=digits,
    last_unit=last_unit,
    separate=separate,
    insert=insert,
    include_equation_number=include_equation_number,
)

latex_string = calculator.run(equation=equation, variables=variables)

print(latex_string)
```

### 5. Render the LaTeX String

```python
from IPython.display import Latex

Latex(latex_string)
```

## 📊 Output Example

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

**Rendered results:**

<p align="center">
  <img src="./assets/latex_rendered.png" alt="Rendered results" width="80%">
</p>

## 🙌 Acknowledgements

- **SymPy**: [https://github.com/sympy/sympy](https://github.com/sympy/sympy)
- **LaTeX Live**: [https://latexlive.com](https://latexlive.com)

## 📄 License

This project is licensed under the [MIT License](LICENSE).
