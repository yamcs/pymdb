from typing import Any

from yamcs.pymdb.model import (
    AndExpression,
    EqExpression,
    Expression,
    GteExpression,
    GtExpression,
    LteExpression,
    LtExpression,
    NeExpression,
    OrExpression,
    Parameter,
)


def eq(parameter: Parameter, value: Any, calibrated=True):
    return EqExpression(parameter, value, calibrated)


def ne(parameter: Parameter, value: Any, calibrated=True):
    return NeExpression(parameter, value, calibrated)


def lt(parameter: Parameter, value: Any, calibrated=True):
    return LtExpression(parameter, value, calibrated)


def lte(parameter: Parameter, value: Any, calibrated=True):
    return LteExpression(parameter, value, calibrated)


def gt(parameter: Parameter, value: Any, calibrated=True):
    return GtExpression(parameter, value, calibrated)


def gte(parameter: Parameter, value: Any, calibrated=True):
    return GteExpression(parameter, value, calibrated)


def all_of(expression1: Expression, expression2: Expression, *args: Expression):
    return AndExpression(expression1, expression2, *args)


def any_of(expression1: Expression, expression2: Expression, *args: Expression):
    return OrExpression(expression1, expression2, *args)
