from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from yamcs.pymdb.parameters import Parameter


class Expression:
    pass


class _AndExpression(Expression):
    def __init__(
        self,
        expression1: Expression,
        expression2: Expression,
        *args: Expression,
    ) -> None:
        self.expressions: list[Expression] = [
            expression1,
            expression2,
            *args,
        ]


class _OrExpression(Expression):
    def __init__(
        self,
        expression1: Expression,
        expression2: Expression,
        *args: Expression,
    ) -> None:
        self.expressions: list[Expression] = [
            expression1,
            expression2,
            *args,
        ]


@dataclass
class EqExpression(Expression):
    parameter: Parameter
    value: Any
    calibrated: bool = True


@dataclass
class NeExpression(Expression):
    parameter: Parameter
    value: Any
    calibrated: bool = True


@dataclass
class LtExpression(Expression):
    parameter: Parameter
    value: Any
    calibrated: bool = True


@dataclass
class LteExpression(Expression):
    parameter: Parameter
    value: Any
    calibrated: bool = True


@dataclass
class GtExpression(Expression):
    parameter: Parameter
    value: Any
    calibrated: bool = True


@dataclass
class GteExpression(Expression):
    parameter: Parameter
    value: Any
    calibrated: bool = True


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
    return _AndExpression(expression1, expression2, *args)


def any_of(expression1: Expression, expression2: Expression, *args: Expression):
    return _OrExpression(expression1, expression2, *args)
