"""Safe, bounded arithmetic expression evaluator for the desktop calculator."""

import ast
import math
import operator

_BINARY = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}
_UNARY = {ast.USub: operator.neg, ast.UAdd: operator.pos}
_MAX_NODES = 32
_MAX_EXPONENT = 100
_MAX_INTEGER_BITS = 4096
_MAX_ABS_FLOAT = 1e100


def evaluate_expression(expression: str):
    """Evaluate basic arithmetic without eval(), with complexity limits."""
    if not isinstance(expression, str) or not expression.strip():
        raise ValueError("Enter an arithmetic expression")
    tree = ast.parse(expression, mode="eval")
    nodes = list(ast.walk(tree))
    if len(nodes) > _MAX_NODES:
        raise ValueError("Expression is too complex")

    def checked(value):
        if type(value) is int and value.bit_length() > _MAX_INTEGER_BITS:
            raise ValueError("Integer result is too large")
        if type(value) is float and (not math.isfinite(value) or abs(value) > _MAX_ABS_FLOAT):
            raise ValueError("Numeric result is outside the supported range")
        return value

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return checked(node.value)
        if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > _MAX_EXPONENT:
                raise ValueError(f"Exponent magnitude must not exceed {_MAX_EXPONENT}")
            return checked(_BINARY[type(node.op)](left, right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
            return checked(_UNARY[type(node.op)](visit(node.operand)))
        raise ValueError("Only basic numeric arithmetic is supported")

    return visit(tree)
