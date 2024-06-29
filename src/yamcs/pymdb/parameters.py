from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Literal

from yamcs.pymdb.alarms import EnumerationAlarm, ThresholdAlarm
from yamcs.pymdb.datatypes import (
    AbsoluteTimeDataType,
    AggregateDataType,
    ArrayDataType,
    BinaryDataType,
    BooleanDataType,
    Choices,
    DataType,
    DynamicInteger,
    EnumeratedDataType,
    Epoch,
    FloatDataType,
    IntegerDataType,
    Member,
    StringDataType,
)
from yamcs.pymdb.encodings import Encoding, TimeEncoding

if TYPE_CHECKING:
    from yamcs.pymdb.alarms import EnumerationContextAlarm, ThresholdContextAlarm
    from yamcs.pymdb.calibrators import Calibrator
    from yamcs.pymdb.systems import System


class DataSource(Enum):
    """
    The nature of the source entity for which a parameter receives a value
    """

    TELEMETERED = auto()
    """A telemetered parameter is one that will have values in telemetry"""

    DERIVED = auto()
    """
    A derived parameter is one that is calculated, usually by an
    :class:`Algorithm`
    """

    CONSTANT = auto()
    """
    A constant parameter is one that is used as a constant in the system
    (e.g. a vehicle id)
    """

    LOCAL = auto()
    """
    A local parameter is one that is used purely by the software locally
    (e.g. a ground command counter)
    """

    GROUND = auto()
    """
    A ground parameter is one that is generated by an asset which is not the
    spacecraft
    """


class Parameter(DataType):
    """
    Base class for a telemetry parameter.

    If parameters are to be used as entries of telemetry or command
    containers, an encoding should also be specified, describing the raw
    encoding.

    Implementations are: :class:`AbsoluteTimeParameter`,
    :class:`BinaryParameter`, :class:`BooleanParameter`,
    :class:`EnumeratedParameter`, :class:`FloatParameter`,
    :class:`IntegerParameter` and :class:`StringParameter`.

    And complex parameters :class:`AggregateParameter` and
    :class:`ArrayParameter`. These do not directly specify an
    encoding, but group together other parameters.

    Each of these implementations matches a native engineering type in Yamcs.
    """

    def __init__(
        self,
        system: System,
        name: str,
        *,
        aliases: Mapping[str, str] | None = None,
        data_source: DataSource = DataSource.TELEMETERED,
        initial_value: Any = None,
        persistent: bool = True,
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
        """Short name of this parameter"""

        self.system: System = system
        """System this parameter belongs to"""

        self.aliases: dict[str, str] = dict(aliases or {})
        """Alternative names, keyed by namespace"""

        self.data_source: DataSource = data_source
        """
        The nature of the source entity for which this parameter receives a
        value
        """

        self.initial_value: Any = initial_value
        """Initial value"""

        self.persistent: bool = persistent
        """
        If true, the parameter's last value is restored in case of a
        restart of the Yamcs system.

        If :attr:`initial_value` is set too, attr:`initial_value` is only
        used once (when there is no other value to persist).
        """

        if name in system._parameters_by_name:
            raise Exception(f"System already contains a parameter {name}")
        system._parameters_by_name[name] = self

    @property
    def qualified_name(self) -> str:
        """
        Absolute path of this item covering the full system tree. For example,
        an item ``C`` in a subystem ``B`` of a top-level system ``A`` is
        represented as ``/A/B/C``
        """
        path = "/" + self.name

        parent = self.system
        while parent:
            path = "/" + parent.name + path
            parent = getattr(parent, "system", None)

        return path

    def __lt__(self, other: Parameter) -> bool:
        return self.qualified_name < other.qualified_name

    def __str__(self) -> str:
        return self.qualified_name


class AbsoluteTimeParameter(Parameter, AbsoluteTimeDataType):
    """
    A parameter where engineering values represent an instant in time
    """

    def __init__(
        self,
        system: System,
        name: str,
        reference: Epoch | datetime | AbsoluteTimeParameter,
        aliases: Mapping[str, str] | None = None,
        data_source: DataSource = DataSource.TELEMETERED,
        initial_value: Any = None,
        persistent: bool = True,
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
        Parameter.__init__(
            self,
            name=name,
            system=system,
            aliases=aliases,
            data_source=data_source,
            initial_value=initial_value,
            persistent=persistent,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )


class AggregateParameter(Parameter, AggregateDataType):
    """
    A parameter where engineering values represent a structure of other
    data types, referred to as `members`
    """

    def __init__(
        self,
        system: System,
        name: str,
        members: Sequence[Member],
        aliases: Mapping[str, str] | None = None,
        data_source: DataSource = DataSource.TELEMETERED,
        initial_value: Any = None,
        persistent: bool = True,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        encoding: Encoding | None = None,
    ) -> None:
        AggregateDataType.__init__(
            self,
            members=members,
        )
        Parameter.__init__(
            self,
            name=name,
            system=system,
            aliases=aliases,
            data_source=data_source,
            initial_value=initial_value,
            persistent=persistent,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            encoding=encoding,
        )


class ArrayParameter(Parameter, ArrayDataType):
    """
    A parameter where engineering values represent an array where each element
    is of another data type
    """

    def __init__(
        self,
        system: System,
        name: str,
        data_type: DataType,
        length: int | DynamicInteger,
        aliases: Mapping[str, str] | None = None,
        data_source: DataSource = DataSource.TELEMETERED,
        initial_value: Any = None,
        persistent: bool = True,
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
        Parameter.__init__(
            self,
            name=name,
            system=system,
            aliases=aliases,
            data_source=data_source,
            initial_value=initial_value,
            persistent=persistent,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            encoding=encoding,
        )


class BinaryParameter(Parameter, BinaryDataType):
    """
    A parameter where engineering values represent binary
    """

    def __init__(
        self,
        system: System,
        name: str,
        min_length: int | None = None,
        max_length: int | None = None,
        aliases: Mapping[str, str] | None = None,
        data_source: DataSource = DataSource.TELEMETERED,
        initial_value: Any = None,
        persistent: bool = True,
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
        Parameter.__init__(
            self,
            name=name,
            system=system,
            aliases=aliases,
            data_source=data_source,
            initial_value=initial_value,
            persistent=persistent,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )


class BooleanParameter(Parameter, BooleanDataType):
    """
    A parameter where engineering values represent a boolean enumeration
    """

    def __init__(
        self,
        system: System,
        name: str,
        zero_string_value: str = "False",
        one_string_value: str = "True",
        aliases: Mapping[str, str] | None = None,
        data_source: DataSource = DataSource.TELEMETERED,
        initial_value: Any = None,
        persistent: bool = True,
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
        Parameter.__init__(
            self,
            name=name,
            system=system,
            aliases=aliases,
            data_source=data_source,
            initial_value=initial_value,
            persistent=persistent,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )


class EnumeratedParameter(Parameter, EnumeratedDataType):
    """
    A parameter where engineering values represent states in an enumeration
    """

    def __init__(
        self,
        system: System,
        name: str,
        choices: Choices,
        alarm: EnumerationAlarm | None = None,
        context_alarms: Sequence[EnumerationContextAlarm] | None = None,
        aliases: Mapping[str, str] | None = None,
        data_source: DataSource = DataSource.TELEMETERED,
        initial_value: Any = None,
        persistent: bool = True,
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
        Parameter.__init__(
            self,
            name=name,
            system=system,
            aliases=aliases,
            data_source=data_source,
            initial_value=initial_value,
            persistent=persistent,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )

        self.alarm: EnumerationAlarm | None = alarm
        """Specification for alarm monitoring"""

        self.context_alarms: list[EnumerationContextAlarm] = list(context_alarms or [])
        """Alarm specification when a specific context expression applies"""


class FloatParameter(Parameter, FloatDataType):
    """
    A parameter where engineering values represent a decimal
    """

    def __init__(
        self,
        system: System,
        name: str,
        bits: Literal[32, 64] = 32,
        minimum: float | None = None,
        minimum_inclusive: bool = True,
        maximum: float | None = None,
        maximum_inclusive: bool = True,
        aliases: Mapping[str, str] | None = None,
        data_source: DataSource = DataSource.TELEMETERED,
        initial_value: Any = None,
        persistent: bool = True,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        units: str | None = None,
        encoding: Encoding | None = None,
        calibrator: Calibrator | None = None,
        alarm: ThresholdAlarm | None = None,
        context_alarms: Sequence[ThresholdContextAlarm] | None = None,
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
        Parameter.__init__(
            self,
            name=name,
            system=system,
            aliases=aliases,
            data_source=data_source,
            initial_value=initial_value,
            persistent=persistent,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )

        self.alarm: ThresholdAlarm | None = alarm
        """Specification for alarm monitoring"""

        self.context_alarms: list[ThresholdContextAlarm] = list(context_alarms or [])
        """Alarm specification when a specific context expression applies"""


class IntegerParameter(Parameter, IntegerDataType):
    """
    A parameter where engineering values represent an integer
    """

    def __init__(
        self,
        system: System,
        name: str,
        signed: bool = True,
        bits: int = 32,
        minimum: int | None = None,
        maximum: int | None = None,
        aliases: Mapping[str, str] | None = None,
        data_source: DataSource = DataSource.TELEMETERED,
        initial_value: Any = None,
        persistent: bool = True,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        units: str | None = None,
        encoding: Encoding | None = None,
        calibrator: Calibrator | None = None,
        alarm: ThresholdAlarm | None = None,
        context_alarms: Sequence[ThresholdContextAlarm] | None = None,
    ) -> None:
        IntegerDataType.__init__(
            self,
            signed=signed,
            bits=bits,
            minimum=minimum,
            maximum=maximum,
            calibrator=calibrator,
        )
        Parameter.__init__(
            self,
            name=name,
            system=system,
            aliases=aliases,
            data_source=data_source,
            initial_value=initial_value,
            persistent=persistent,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )

        self.alarm: ThresholdAlarm | None = alarm
        """Specification for alarm monitoring"""

        self.context_alarms: list[ThresholdContextAlarm] = list(context_alarms or [])
        """Alarm specification when a specific context expression applies"""


class StringParameter(Parameter, StringDataType):
    """
    A parameter where engineering values represent a character string
    """

    def __init__(
        self,
        system: System,
        name: str,
        min_length: int | None = None,
        max_length: int | None = None,
        aliases: Mapping[str, str] | None = None,
        data_source: DataSource = DataSource.TELEMETERED,
        initial_value: Any = None,
        persistent: bool = True,
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
        Parameter.__init__(
            self,
            name=name,
            system=system,
            aliases=aliases,
            data_source=data_source,
            initial_value=initial_value,
            persistent=persistent,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )
