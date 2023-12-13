from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Literal, Type, TypeAlias

from yamcs.pymdb.encodings import DataEncoding, TimeEncoding

if TYPE_CHECKING:
    from yamcs.pymdb.parameters import AbsoluteTimeParameter


class Epoch(Enum):
    UNIX = auto()


Choices: TypeAlias = list[tuple[int, str] | tuple[int, str, str]] | Type[Enum]


@dataclass(kw_only=True)
class DataType:
    initial_value: Any = None

    short_description: str | None = None
    """Oneline description"""

    long_description: str | None = None
    """Multiline description"""

    extra: dict[str, str] = field(default_factory=dict)
    """Arbitrary information, keyed by name"""

    units: str | None = None
    encoding: DataEncoding | None = None


@dataclass(kw_only=True)
class AbsoluteTimeDataType(DataType):
    reference: Epoch | AbsoluteTimeParameter
    encoding: TimeEncoding | None = None


@dataclass(kw_only=True)
class AggregateDataType(DataType):
    members: list[Member] = field(default_factory=list)


@dataclass(kw_only=True)
class ArrayDataType(DataType):
    data_type: DataType
    length: int


@dataclass(kw_only=True)
class BinaryDataType(DataType):
    min_length: int | None = None
    """Minimum length in bytes"""

    max_length: int | None = None
    """Maximum length in bytes"""


@dataclass(kw_only=True)
class BooleanDataType(DataType):
    zero_string_value: str = "False"
    one_string_value: str = "True"


@dataclass(kw_only=True)
class EnumeratedDataType(DataType):
    choices: Choices

    def label_for(self, value: int):
        if isinstance(self.choices, list):
            for choice in self.choices:
                if choice[0] == value:
                    return choice[1]
        else:
            for choice in self.choices:
                if choice.value == value:
                    return choice.name

        raise KeyError(f"No enumeration label for value {value}")


@dataclass(kw_only=True)
class FloatDataType(DataType):
    bits: Literal[32] | Literal[64] = 32

    minimum: float | None = None
    """Minimum valid engineering value"""

    minimum_inclusive: bool = True
    """Whether the minimum value itself is valid"""

    maximum: float | None = None
    """Maximum valid engineering value (inclusive)"""

    maximum_inclusive: bool = True
    """Whether the maximum value itself is valid"""


@dataclass(kw_only=True)
class IntegerDataType(DataType):
    signed: bool = True

    minimum: int | None = None
    """Minimum valid engineering value (inclusive)"""

    maximum: int | None = None
    """Maximum valid engineering value (inclusive)"""


@dataclass(kw_only=True)
class StringDataType(DataType):
    min_length: int | None = None
    """Minimum length in characters"""

    max_length: int | None = None
    """Maximum length in characters"""


@dataclass
class Member(DataType):
    name: str


@dataclass(kw_only=True)
class AbsoluteTimeMember(Member, AbsoluteTimeDataType):
    pass


@dataclass(kw_only=True)
class AggregateMember(Member, AggregateDataType):
    pass


@dataclass(kw_only=True)
class ArrayMember(Member, ArrayDataType):
    pass


@dataclass(kw_only=True)
class BinaryMember(Member, BinaryDataType):
    pass


@dataclass(kw_only=True)
class BooleanMember(Member, BooleanDataType):
    pass


@dataclass(kw_only=True)
class EnumeratedMember(Member, EnumeratedDataType):
    pass


@dataclass(kw_only=True)
class FloatMember(Member, FloatDataType):
    pass


@dataclass(kw_only=True)
class IntegerMember(Member, IntegerDataType):
    pass


@dataclass(kw_only=True)
class StringMember(Member, StringDataType):
    pass
