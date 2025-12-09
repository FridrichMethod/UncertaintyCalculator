"""Shared pytest fixtures for calculator test cases."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from tests.input_parsers import parse_equation, parse_variables
from uncertainty_calculator import Digits


@dataclass(frozen=True)
class RawCase:
    """Frozen test case data to exercise calculator pipeline."""

    name: str
    equation: list[str]
    variables: list[tuple[str, str]]


CASES: list[RawCase] = [
    RawCase(
        name="default",
        equation=[x.strip() for x in [r"\zeta ", r" (K*pi*eta*u*l)/(4*pi*phi*e_0*e_r)"]],
        variables=[
            ("K = 4 +- 0", r"K"),
            ("eta = 0.9358e-3 +- 0.0001/sqrt(3)", r"\eta"),
            ("u = 3.68e-5 +- 0.11e-5", r"u"),
            ("l = 0.2256 +- 0.0019", r"l"),
            ("phi = 100 +- 1/sqrt(3)", r"\varphi"),
            ("e_0 = 8.8541878128e-12 +- 0", r"\varepsilon_0"),
            ("e_r = 78.7 +- 0.1/sqrt(3)", r"\varepsilon_\text{r}"),
        ],
    ),
    RawCase(
        name="readme",
        equation=[x.strip() for x in [r"W ", r" (-Q_V*m-Q_N-Q_M)/Dt-rho*V*C"]],
        variables=[
            ("Q_V = -26.414 +- 0", r"Q_V"),
            ("m = 0.9547 +- 0.0004/sqrt(3)", r"m"),
            ("Q_N = -0.323 +- 3.243*0.0004/sqrt(3)", r"Q_\ce{Ni}"),
            ("Q_M = -0.01 +- 0.0002*16.736/sqrt(3)", r"Q_\text{cotton}"),
            ("rho = 0.99865 +- 0", r"\rho_\ce{H2O}"),
            ("V = 3000 +- 0.01", r"V"),
            ("C = 4.1824e-3 +- 0", r"C_\ce{H2O}"),
            ("Dt = 1.770 +- 0.009", r"\Delta T"),
        ],
    ),
    RawCase(
        name="linear",
        equation=["y", "m*x + b"],
        variables=[
            ("m = 2.5 +- 0.1", "m"),
            ("x = 4.0 +- 0.2", "x"),
            ("b = 1.0 +- 0.5", "b"),
        ],
    ),
    RawCase(
        name="power",
        equation=["E", "0.5 * m * v**2"],
        variables=[
            ("m = 10.0 +- 0.5", "m"),
            ("v = 5.0 +- 0.1", "v"),
        ],
    ),
    RawCase(
        name="trig_exp",
        equation=["I", "I0 * exp(-t/tau) * sin(omega*t + phi)"],
        variables=[
            ("I0 = 2.0 +- 0.05", r"I_0"),
            ("t = 0.25 +- 0.01", "t"),
            ("tau = 1.2 +- 0.02", r"\tau"),
            ("omega = 3.14 +- 0.01", r"\omega"),
            ("phi = 0.1 +- 0.02", r"\phi"),
        ],
    ),
    RawCase(
        name="rational_mixed",
        equation=["Z", "(a*b + c)/(d - e*f)"],
        variables=[
            ("a = 1.5 +- 0.01", "a"),
            ("b = 2.5 +- 0.02", "b"),
            ("c = 0.75 +- 0.005", "c"),
            ("d = 10 +- 0.1", "d"),
            ("e = 0.5 +- 0.01", "e"),
            ("f = 4 +- 0.2", "f"),
        ],
    ),
]


@pytest.fixture(scope="session", params=CASES, ids=lambda case: case.name)
def raw_case(request: pytest.FixtureRequest) -> RawCase:
    """Provide each raw test case definition."""
    return request.param


@pytest.fixture(scope="session")
def equation(raw_case: RawCase):
    """Equation parsed from a raw case."""
    return parse_equation(raw_case.equation)


@pytest.fixture(scope="session")
def variables(raw_case: RawCase):
    """Variables parsed from a raw case."""
    return parse_variables(raw_case.variables)


@pytest.fixture(scope="session", params=[Digits(mu=3, sigma=2), Digits(mu=4, sigma=3)])
def digits(request: pytest.FixtureRequest) -> Digits:
    """Digits configuration combinations."""
    return request.param


@pytest.fixture(scope="session", params=[r"\text{V}", "", None], ids=["V", "empty", "none"])
def last_unit(request: pytest.FixtureRequest):
    """Units to append to rendered results."""
    return request.param


@pytest.fixture(scope="session", params=[True, False], ids=["separate", "combined"])
def separate(request: pytest.FixtureRequest) -> bool:
    """Toggle separate rendering."""
    return request.param


@pytest.fixture(scope="session", params=[True, False], ids=["insert", "no-insert"])
def insert(request: pytest.FixtureRequest) -> bool:
    """Toggle numerical insertion into LaTeX."""
    return request.param


@pytest.fixture(scope="session", params=[True, False], ids=["numbered", "unnumbered"])
def include_equation_number(request: pytest.FixtureRequest) -> bool:
    """Toggle equation numbering."""
    return request.param
