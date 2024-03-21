from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from yamcs.pymdb.parameters import AggregateParameter, Member, Parameter


class ParameterMember:
    def __init__(
        self,
        parameter: AggregateParameter,
        path: Member | list[Member],
    ):
        self.parameter = parameter

        if isinstance(path, Sequence):
            self.path: list[Member] = path
        else:
            self.path: list[Member] = [path]


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
        ref: Parameter | ParameterMember | str,
        value: Any,
        calibrated: bool = True,
    ):
        self.ref: Parameter | ParameterMember | str = ref
        self.value: Any = value
        self.calibrated: bool = calibrated


class NeExpression(Expression):
    def __init__(
        self,
        ref: Parameter | ParameterMember | str,
        value: Any,
        calibrated: bool = True,
    ):
        self.ref: Parameter | ParameterMember | str = ref
        self.value: Any = value
        self.calibrated: bool = calibrated


class LtExpression(Expression):
    def __init__(
        self,
        ref: Parameter | ParameterMember | str,
        value: Any,
        calibrated: bool = True,
    ):
        self.ref: Parameter | ParameterMember | str = ref
        self.value: Any = value
        self.calibrated: bool = calibrated


class LteExpression(Expression):
    def __init__(
        self,
        ref: Parameter | ParameterMember | str,
        value: Any,
        calibrated: bool = True,
    ):
        self.ref: Parameter | ParameterMember | str = ref
        self.value: Any = value
        self.calibrated: bool = calibrated


class GtExpression(Expression):
    def __init__(
        self,
        ref: Parameter | ParameterMember | str,
        value: Any,
        calibrated: bool = True,
    ):
        self.ref: Parameter | ParameterMember | str = ref
        self.value: Any = value
        self.calibrated: bool = calibrated


class GteExpression(Expression):
    def __init__(
        self,
        ref: Parameter | ParameterMember | str,
        value: Any,
        calibrated: bool = True,
    ):
        self.ref: Parameter | ParameterMember | str = ref
        self.value: Any = value
        self.calibrated: bool = calibrated


def eq(ref: Parameter | ParameterMember | str, value: Any, calibrated=True):
    return EqExpression(ref, value, calibrated)


def ne(ref: Parameter | ParameterMember | str, value: Any, calibrated=True):
    return NeExpression(ref, value, calibrated)


def lt(ref: Parameter | ParameterMember | str, value: Any, calibrated=True):
    return LtExpression(ref, value, calibrated)


def lte(ref: Parameter | ParameterMember | str, value: Any, calibrated=True):
    return LteExpression(ref, value, calibrated)


def gt(ref: Parameter | ParameterMember | str, value: Any, calibrated=True):
    return GtExpression(ref, value, calibrated)


def gte(ref: Parameter | ParameterMember | str, value: Any, calibrated=True):
    return GteExpression(ref, value, calibrated)


def all_of(expression1: Expression, expression2: Expression, *args: Expression):
    return AndExpression(expression1, expression2, *args)


def any_of(expression1: Expression, expression2: Expression, *args: Expression):
    return OrExpression(expression1, expression2, *args)
