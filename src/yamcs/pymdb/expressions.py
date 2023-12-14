from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from yamcs.pymdb.parameters import Parameter


class Expression:
    pass


class AndExpression(Expression):
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


class OrExpression(Expression):
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


class EqExpression(Expression):
    def __init__(
        self,
        parameter: Parameter,
        value: Any,
        calibrated: bool = True,
    ):
        self.parameter: Parameter = parameter
        self.value: Any = value
        self.calibrated: bool = calibrated


class NeExpression(Expression):
    def __init__(
        self,
        parameter: Parameter,
        value: Any,
        calibrated: bool = True,
    ):
        self.parameter: Parameter = parameter
        self.value: Any = value
        self.calibrated: bool = calibrated


class LtExpression(Expression):
    def __init__(
        self,
        parameter: Parameter,
        value: Any,
        calibrated: bool = True,
    ):
        self.parameter: Parameter = parameter
        self.value: Any = value
        self.calibrated: bool = calibrated


class LteExpression(Expression):
    def __init__(
        self,
        parameter: Parameter,
        value: Any,
        calibrated: bool = True,
    ):
        self.parameter: Parameter = parameter
        self.value: Any = value
        self.calibrated: bool = calibrated


class GtExpression(Expression):
    def __init__(
        self,
        parameter: Parameter,
        value: Any,
        calibrated: bool = True,
    ):
        self.parameter: Parameter = parameter
        self.value: Any = value
        self.calibrated: bool = calibrated


class GteExpression(Expression):
    def __init__(
        self,
        parameter: Parameter,
        value: Any,
        calibrated: bool = True,
    ):
        self.parameter: Parameter = parameter
        self.value: Any = value
        self.calibrated: bool = calibrated


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
