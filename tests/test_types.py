"""Tests for type dataclasses."""

from __future__ import annotations

import pytest

from uncertainty_calculator import Digits


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
