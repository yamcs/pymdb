from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Literal, TypeAlias

from yamcs.pymdb.encodings import Encoding, TimeEncoding

if TYPE_CHECKING:
    from yamcs.pymdb.calibrators import Calibrator
    from yamcs.pymdb.parameters import AbsoluteTimeParameter, IntegerParameter


class Epoch(Enum):
    GPS = auto()
    J2000 = auto()
    TAI = auto()
    UNIX = auto()


Choices: TypeAlias = list[tuple[int, str] | tuple[int, str, str]] | type[Enum]


@dataclass
class DynamicInteger:
    parameter: IntegerParameter | str
    """
    Retrieve the value of this parameter.

    The parameter may be specified as ``str``, which is intended for referencing
    a parameter that is not managed with PyMDB.
    """


class DataType:
    def __init__(
        self,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        units: str | None = None,
        encoding: Encoding | None = None,
    ) -> None:
        self.short_description: str | None = short_description
        """Oneline description"""

        self.long_description: str | None = long_description
        """Multiline description"""

        self.extra: dict[str, str] = dict(extra or {})
        """Arbitrary information, keyed by name"""

        self.units: str | None = units
        """Engineering units"""

        self.encoding: Encoding | None = encoding
        """
        How this data is sent or received from some non-native, off-platform
        device. (e.g. a spacecraft)
        """


class AbsoluteTimeDataType(DataType):
    def __init__(
        self,
        reference: Epoch | datetime | AbsoluteTimeParameter,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        units: str | None = None,
        encoding: TimeEncoding | None = None,
    ) -> None:
        DataType.__init__(
            self,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )
        self.reference: Epoch | datetime | AbsoluteTimeParameter = reference


class AggregateDataType(DataType):
    def __init__(
        self,
        members: Sequence[Member],
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        units: str | None = None,
        encoding: Encoding | None = None,
    ) -> None:
        DataType.__init__(
            self,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )
        self.members: list[Member] = list(members)

    def find_member(self, name: str) -> Member:
        for member in self.members:
            if member.name == name:
                return member
        raise KeyError


class ArrayDataType(DataType):
    def __init__(
        self,
        data_type: DataType,
        length: int | DynamicInteger,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        encoding: Encoding | None = None,
    ) -> None:
        DataType.__init__(
            self,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            encoding=encoding,
        )
        self.data_type: DataType = data_type
        self.length: int | DynamicInteger = length


class BinaryDataType(DataType):
    def __init__(
        self,
        min_length: int | None = None,
        max_length: int | None = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        units: str | None = None,
        encoding: Encoding | None = None,
    ) -> None:
        DataType.__init__(
            self,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )

        self.min_length: int | None = min_length
        """Minimum length in bytes"""

        self.max_length: int | None = max_length
        """Maximum length in bytes"""


class BooleanDataType(DataType):
    def __init__(
        self,
        zero_string_value: str = "False",
        one_string_value: str = "True",
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        units: str | None = None,
        encoding: Encoding | None = None,
    ) -> None:
        DataType.__init__(
            self,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )

        self.zero_string_value: str = zero_string_value
        self.one_string_value: str = one_string_value


class EnumeratedDataType(DataType):
    def __init__(
        self,
        choices: Choices,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        units: str | None = None,
        encoding: Encoding | None = None,
    ) -> None:
        DataType.__init__(
            self,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )

        self.choices: Choices = choices

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


class FloatDataType(DataType):
    def __init__(
        self,
        bits: Literal[32, 64] = 32,
        minimum: float | None = None,
        minimum_inclusive: bool = True,
        maximum: float | None = None,
        maximum_inclusive: bool = True,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        units: str | None = None,
        encoding: Encoding | None = None,
        calibrator: Calibrator | None = None,
    ) -> None:
        DataType.__init__(
            self,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )

        self.bits: Literal[32, 64] = bits

        self.minimum: float | None = minimum
        """Minimum valid engineering value"""

        self.minimum_inclusive: bool = minimum_inclusive
        """Whether the minimum value itself is valid"""

        self.maximum: float | None = maximum
        """Maximum valid engineering value (inclusive)"""

        self.maximum_inclusive: bool = maximum_inclusive
        """Whether the maximum value itself is valid"""

        self.calibrator: Calibrator | None = calibrator
        """Describes how a raw value is transformed to an engineering value"""


class IntegerDataType(DataType):
    def __init__(
        self,
        signed: bool = True,
        bits: int = 32,
        minimum: int | None = None,
        maximum: int | None = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        units: str | None = None,
        encoding: Encoding | None = None,
        calibrator: Calibrator | None = None,
    ) -> None:
        DataType.__init__(
            self,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )

        self.signed: bool = signed

        self.bits: int = bits

        self.minimum: int | None = minimum
        """Minimum valid engineering value (inclusive)"""

        self.maximum: int | None = maximum
        """Maximum valid engineering value (inclusive)"""

        self.calibrator: Calibrator | None = calibrator
        """Describes how a raw value is transformed to an engineering value"""


class StringDataType(DataType):
    def __init__(
        self,
        min_length: int | None = None,
        max_length: int | None = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        units: str | None = None,
        encoding: Encoding | None = None,
    ) -> None:
        DataType.__init__(
            self,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )

        self.min_length: int | None = min_length
        """Minimum length in characters"""

        self.max_length: int | None = max_length
        """Maximum length in characters"""


class Member(DataType):
    def __init__(
        self,
        name: str,
        initial_value: Any = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        units: str | None = None,
        encoding: Encoding | None = None,
    ) -> None:
        DataType.__init__(
            self,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )

        self.name: str = name
        """Member name"""

        self.initial_value: Any = initial_value
        """Initial value"""


class AbsoluteTimeMember(Member, AbsoluteTimeDataType):
    def __init__(
        self,
        name: str,
        reference: Epoch | datetime | AbsoluteTimeParameter,
        initial_value: Any = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        units: str | None = None,
        encoding: TimeEncoding | None = None,
    ) -> None:
        AbsoluteTimeDataType.__init__(
            self,
            reference=reference,
        )
        Member.__init__(
            self,
            name=name,
            initial_value=initial_value,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )


class AggregateMember(Member, AggregateDataType):
    def __init__(
        self,
        name: str,
        members: Sequence[Member],
        initial_value: Any = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        encoding: Encoding | None = None,
    ) -> None:
        AggregateDataType.__init__(
            self,
            members=members,
        )
        Member.__init__(
            self,
            name=name,
            initial_value=initial_value,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            encoding=encoding,
        )


class ArrayMember(Member, ArrayDataType):
    def __init__(
        self,
        name: str,
        data_type: DataType,
        length: int,
        initial_value: Any = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        encoding: Encoding | None = None,
    ) -> None:
        ArrayDataType.__init__(
            self,
            data_type=data_type,
            length=length,
        )
        Member.__init__(
            self,
            name=name,
            initial_value=initial_value,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            encoding=encoding,
        )


class BinaryMember(Member, BinaryDataType):
    def __init__(
        self,
        name: str,
        min_length: int | None = None,
        max_length: int | None = None,
        initial_value: Any = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        units: str | None = None,
        encoding: Encoding | None = None,
    ) -> None:
        BinaryDataType.__init__(
            self,
            min_length=min_length,
            max_length=max_length,
        )
        Member.__init__(
            self,
            name=name,
            initial_value=initial_value,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )


class BooleanMember(Member, BooleanDataType):
    def __init__(
        self,
        name: str,
        zero_string_value: str = "False",
        one_string_value: str = "True",
        initial_value: Any = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        units: str | None = None,
        encoding: Encoding | None = None,
    ) -> None:
        BooleanDataType.__init__(
            self,
            zero_string_value=zero_string_value,
            one_string_value=one_string_value,
        )
        Member.__init__(
            self,
            name=name,
            initial_value=initial_value,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )


class EnumeratedMember(Member, EnumeratedDataType):
    def __init__(
        self,
        name: str,
        choices: Choices,
        initial_value: Any = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        units: str | None = None,
        encoding: Encoding | None = None,
    ) -> None:
        EnumeratedDataType.__init__(
            self,
            choices=choices,
        )
        Member.__init__(
            self,
            name=name,
            initial_value=initial_value,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )


class FloatMember(Member, FloatDataType):
    def __init__(
        self,
        name: str,
        bits: Literal[32, 64] = 32,
        minimum: float | None = None,
        minimum_inclusive: bool = True,
        maximum: float | None = None,
        maximum_inclusive: bool = True,
        initial_value: Any = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        units: str | None = None,
        encoding: Encoding | None = None,
        calibrator: Calibrator | None = None,
    ) -> None:
        FloatDataType.__init__(
            self,
            bits=bits,
            minimum=minimum,
            minimum_inclusive=minimum_inclusive,
            maximum=maximum,
            maximum_inclusive=maximum_inclusive,
            calibrator=calibrator,
        )
        Member.__init__(
            self,
            name=name,
            initial_value=initial_value,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )


class IntegerMember(Member, IntegerDataType):
    def __init__(
        self,
        name: str,
        signed: bool = True,
        bits: int = 32,
        minimum: int | None = None,
        maximum: int | None = None,
        initial_value: Any = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        units: str | None = None,
        encoding: Encoding | None = None,
        calibrator: Calibrator | None = None,
    ) -> None:
        IntegerDataType.__init__(
            self,
            signed=signed,
            bits=bits,
            minimum=minimum,
            maximum=maximum,
            calibrator=calibrator,
        )
        Member.__init__(
            self,
            name=name,
            initial_value=initial_value,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )


class StringMember(Member, StringDataType):
    def __init__(
        self,
        name: str,
        min_length: int | None = None,
        max_length: int | None = None,
        initial_value: Any = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        units: str | None = None,
        encoding: Encoding | None = None,
    ) -> None:
        StringDataType.__init__(
            self,
            min_length=min_length,
            max_length=max_length,
        )
        Member.__init__(
            self,
            name=name,
            initial_value=initial_value,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )
