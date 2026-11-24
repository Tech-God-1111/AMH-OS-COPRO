import pytest

from core.calculator import evaluate_expression


@pytest.mark.parametrize(("expression", "expected"), [
    ("(12 + 4) * 3", 48),
    ("-5 + 2", -3),
    ("2 ** 8", 256),
    ("7 / 2", 3.5),
])
def test_supported_arithmetic(expression, expected):
    assert evaluate_expression(expression) == expected


@pytest.mark.parametrize("expression", [
    "__import__('os').system('whoami')",
    "2 ** 101",
    "2 ** (2 ** 101)",
    "1 / 0",
    "True + 1",
    "9" * 2000,
])
def test_rejects_unsafe_or_invalid_expressions(expression):
    with pytest.raises((ValueError, SyntaxError, ZeroDivisionError, OverflowError)):
        evaluate_expression(expression)
