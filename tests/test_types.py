"""Tests for type dataclasses."""

from __future__ import annotations

import pytest

from uncertainty_calculator import Digits, Variable


def test_digits_dataclass_behaves_like_config():
    """Digits should store configured precision values."""
    digits = Digits(mu=4, sigma=5)
    assert digits.mu == 4
    assert digits.sigma == 5


def test_digits_requires_positive_integers():
    """Digits must enforce positive integer validation."""
    with pytest.raises(ValueError, match="mu must be a positive integer"):
        Digits(mu=0, sigma=2)
    with pytest.raises(ValueError, match="sigma must be a positive integer"):
        Digits(mu=2, sigma=-1)


def test_variable_normalizes_numeric_inputs_to_float():
    """Variable numeric fields should be stored as floats."""
    variable = Variable(name="x", value=1, uncertainty=0, latex_name="x")
    assert variable.value == 1.0
    assert variable.uncertainty == 0.0


def test_variable_rejects_string_numeric_fields():
    """Variable should reject string inputs that need expression evaluation."""
    with pytest.raises(TypeError, match="value must be a real number"):
        Variable(name="x", value="1", uncertainty=0.1, latex_name="x")
    with pytest.raises(TypeError, match="uncertainty must be a real number"):
        Variable(name="x", value=1.0, uncertainty="0.1", latex_name="x")
