from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Literal, Optional, Type, TypeAlias


class AlarmLevel(Enum):
    NORMAL = auto()
    WATCH = auto()
    WARNING = auto()
    DISTRESS = auto()
    CRITICAL = auto()
    SEVERE = auto()


class DataSource(Enum):
    TELEMETERED = auto()
    """A telemetered parameter is one that will have values in telemetry"""

    DERIVED = auto()
    """A derived parameter is one that is calculated, usually by an Algorithm"""

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


class CommandLevel(Enum):
    """
    The importance of a telecommand in terms of the nature and
    significance of its on-board effect.

    These levels are adopted from ISO 14950:2004
    """

    NORMAL = auto()
    """
    Level D
    """

    VITAL = auto()
    """
    Level C: Telecommands that are not critical, but essential to the success
    of the mission and, if sent at the wrong time, could cause momentary loss
    of the mission.
    """

    CRITICAL = auto()
    """
    Level B: Telecommands that, if executed at the wrong time or in the wrong
    configuration, could cause irreversible loss or damage for the mission
    (i.e. endanger the achievement of the primary mission objectives)
    """

    FORBIDDEN = auto()
    """
    Level A: Telecommands that are not expected to be used for nominal or
    foreseeable contingency operations, that are included for unforeseen
    contingency operations, and that could cause irreversible damage if
    executed at the wrong time or inthe wrong configuration.
    """


class ByteOrder(Enum):
    BIG_ENDIAN = auto()
    LITTLE_ENDIAN = auto()


class Charset(Enum):
    US_ASCII = auto()
    ISO_8859_1 = auto()
    WINDOWS_1252 = auto()
    UTF_8 = auto()
    UTF_16 = auto()
    UTF_16LE = auto()
    UTF_16BE = auto()
    UTF_32 = auto()
    UTF_32LE = auto()
    UTF_32BE = auto()


class Epoch(Enum):
    UNIX = auto()


class FloatDataEncodingScheme(Enum):
    IEEE754_1985 = auto()
    MILSTD_1750A = auto()


class IntegerDataEncodingScheme(Enum):
    UNSIGNED = auto()
    SIGN_MAGNITUDE = auto()
    TWOS_COMPLEMENT = auto()
    ONES_COMPLEMENT = auto()


class ReferenceLocation(Enum):
    CONTAINER_START = auto()
    PREVIOUS_ENTRY = auto()


class TerminationAction(Enum):
    SUCCESS = auto()
    FAIL = auto()


Choices: TypeAlias = list[tuple[int, str] | tuple[int, str, str]] | Type[Enum]


@dataclass
class JavaAlgorithm:
    java: str


@dataclass(kw_only=True)
class EnumerationAlarm:
    states: dict[str, AlarmLevel]
    default_level: AlarmLevel = AlarmLevel.NORMAL


@dataclass(kw_only=True)
class DataEncoding:
    bits: int
    byte_order: ByteOrder = ByteOrder.BIG_ENDIAN


@dataclass(kw_only=True)
class BinaryDataEncoding(DataEncoding):
    bits: int | None = None
    length_bits: int | None = None
    deserializer: JavaAlgorithm | None = None


@dataclass(kw_only=True)
class IntegerDataEncoding(DataEncoding):
    scheme: IntegerDataEncodingScheme = IntegerDataEncodingScheme.UNSIGNED


@dataclass(kw_only=True)
class FloatDataEncoding(DataEncoding):
    scheme: FloatDataEncodingScheme = FloatDataEncodingScheme.IEEE754_1985


@dataclass(kw_only=True)
class FloatTimeEncoding(FloatDataEncoding):
    offset: int = 0
    scale: int = 1


@dataclass(kw_only=True)
class IntegerTimeEncoding(IntegerDataEncoding):
    offset: int = 0
    scale: int = 1


TimeEncoding: TypeAlias = FloatTimeEncoding | IntegerTimeEncoding


@dataclass(kw_only=True)
class StringDataEncoding(DataEncoding):
    bits: int | None = None
    length_bits: int | None = None

    max_bits: int | None = 8388608
    """
    Maximum number of bits, in case of a dynamically sized string.

    This value hints Yamcs about the buffer size that is allocated to
    read the string, although Yamcs can choose to use a smaller buffer
    when it can.

    Default is 1 MB
    """

    charset: Charset = Charset.US_ASCII
    termination: bytes = b"\0"


class SpaceSystem:
    """
    The top-level SpaceSystem is the root element for the set of metadata
    necessary to monitor and command a space device, such as a satellite.

    A SpaceSystem defines a namespace.

    Metadata areas include: telemetry, calibration, alarm, algorithms and
    commands.

    A SpaceSystem may have child :class:`Subsystems`, forming a system tree.
    """

    def __init__(
        self,
        name: str,
        aliases: dict[str, str] | None = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: dict[str, str] | None = None,
    ):
        self.name: str = name
        """Short name of this space system"""

        self.aliases: dict[str, str] = aliases or {}
        """Alternative names, keyed by namespace"""

        self.short_description: str | None = short_description
        """Oneline description"""

        self.long_description: str | None = long_description
        """Multiline description"""

        self.extra: dict[str, str] = extra or {}
        """Arbitrary information, keyed by name"""

        self._commands_by_name: dict[str, "Command"] = {}
        self._containers_by_name: dict[str, "Container"] = {}
        self._parameters_by_name: dict[str, "Parameter"] = {}
        self._subsystems_by_name: dict[str, "Subsystem"] = {}

    @property
    def root(self) -> "SpaceSystem":
        """
        The top-most space system
        """
        return self

    @property
    def qualified_name(self) -> str:
        return "/" + self.name

    @property
    def containers(self) -> list["Container"]:
        """
        Containers directly belonging to this space system
        """
        return list(self._containers_by_name.values())

    @property
    def commands(self) -> list["Command"]:
        """
        Commands directly belonging to this space system
        """
        return list(self._commands_by_name.values())

    @property
    def parameters(self) -> list["Parameter"]:
        """
        Parameters directly belonging to this space system
        """
        return list(self._parameters_by_name.values())

    @property
    def subsystems(self) -> list["Subsystem"]:
        """
        Subsystems directly belonging to this space system
        """
        return list(self._subsystems_by_name.values())

    def add_parameter(self, parameter: "Parameter"):
        if parameter.name in self._parameters_by_name:
            raise Exception(
                f"Space system already contains a parameter {parameter.name}"
            )

        self._parameters_by_name[parameter.name] = parameter
        return parameter

    def add_absolute_time_parameter(
        self,
        name: str,
        reference: "Epoch | AbsoluteTimeParameter",
        aliases: dict[str, str] | None = None,
        initial_value: Any = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: dict[str, str] | None = None,
        units: str | None = None,
        encoding: TimeEncoding | None = None,
    ):
        if name in self._parameters_by_name:
            raise Exception(f"Space system already contains a parameter {name}")

        parameter = AbsoluteTimeParameter(
            name=name,
            space_system=self,
            aliases=aliases or {},
            initial_value=initial_value,
            short_description=short_description,
            long_description=long_description,
            extra=extra or {},
            units=units,
            encoding=encoding,
            reference=reference,
        )
        self._parameters_by_name[parameter.name] = parameter
        return parameter

    def add_aggregate_parameter(
        self,
        name: str,
        members: list["Member"],
        aliases: dict[str, str] | None = None,
        initial_value: dict[str, Any] | None = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: dict[str, str] | None = None,
        units: str | None = None,
        encoding: DataEncoding | None = None,
    ):
        if name in self._parameters_by_name:
            raise Exception(f"Space system already contains a parameter {name}")

        parameter = AggregateParameter(
            name=name,
            space_system=self,
            aliases=aliases or {},
            initial_value=initial_value,
            short_description=short_description,
            long_description=long_description,
            extra=extra or {},
            units=units,
            encoding=encoding,
            members=members,
        )
        self._parameters_by_name[parameter.name] = parameter
        return parameter

    def add_array_parameter(
        self,
        name: str,
        length: int,
        data_type: "DataType",
        aliases: dict[str, str] | None = None,
        initial_value: list[Any] | None = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: dict[str, str] | None = None,
    ):
        if name in self._parameters_by_name:
            raise Exception(f"Space system already contains a parameter {name}")

        parameter = ArrayParameter(
            name=name,
            space_system=self,
            length=length,
            data_type=data_type,
            aliases=aliases or {},
            initial_value=initial_value,
            short_description=short_description,
            long_description=long_description,
            extra=extra or {},
        )
        self._parameters_by_name[parameter.name] = parameter
        return parameter

    def add_binary_parameter(
        self,
        name: str,
        aliases: dict[str, str] | None = None,
        initial_value: Any = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: dict[str, str] | None = None,
        units: str | None = None,
        encoding: BinaryDataEncoding | None = None,
    ):
        if name in self._parameters_by_name:
            raise Exception(f"Space system already contains a parameter {name}")

        parameter = BinaryParameter(
            name=name,
            space_system=self,
            aliases=aliases or {},
            initial_value=initial_value,
            short_description=short_description,
            long_description=long_description,
            extra=extra or {},
            units=units,
            encoding=encoding,
        )
        self._parameters_by_name[parameter.name] = parameter
        return parameter

    def add_boolean_parameter(
        self,
        name: str,
        aliases: dict[str, str] | None = None,
        initial_value: bool | None = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: dict[str, str] | None = None,
        units: str | None = None,
        encoding: DataEncoding | None = None,
        zero_string_value: str = "False",
        one_string_value: str = "True",
    ):
        if name in self._parameters_by_name:
            raise Exception(f"Space system already contains a parameter {name}")

        parameter = BooleanParameter(
            name=name,
            space_system=self,
            aliases=aliases or {},
            initial_value=initial_value,
            short_description=short_description,
            long_description=long_description,
            extra=extra or {},
            units=units,
            encoding=encoding,
            zero_string_value=zero_string_value,
            one_string_value=one_string_value,
        )
        self._parameters_by_name[parameter.name] = parameter
        return parameter

    def add_enumerated_parameter(
        self,
        name: str,
        choices: Choices,
        aliases: dict[str, str] | None = None,
        initial_value: str | None = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: dict[str, str] | None = None,
        units: str | None = None,
        encoding: DataEncoding | None = None,
        alarm: EnumerationAlarm | None = None,
    ):
        if name in self._parameters_by_name:
            raise Exception(f"Space system already contains a parameter {name}")

        parameter = EnumeratedParameter(
            name=name,
            space_system=self,
            initial_value=initial_value,
            aliases=aliases or {},
            short_description=short_description,
            long_description=long_description,
            extra=extra or {},
            units=units,
            encoding=encoding,
            choices=choices,
            alarm=alarm,
        )
        self._parameters_by_name[parameter.name] = parameter
        return parameter

    def add_float_parameter(
        self,
        name: str,
        aliases: dict[str, str] | None = None,
        initial_value: int | None = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: dict[str, str] | None = None,
        units: str | None = None,
        encoding: DataEncoding | None = None,
        bits: Literal[32] | Literal[64] = 32,
        minimum: float | None = None,
        minimum_inclusive: bool = True,
        maximum: float | None = None,
        maximum_inclusive: bool = True,
    ):
        if name in self._parameters_by_name:
            raise Exception(f"Space system already contains a parameter {name}")

        parameter = FloatParameter(
            name=name,
            space_system=self,
            aliases=aliases or {},
            initial_value=initial_value,
            short_description=short_description,
            long_description=long_description,
            extra=extra or {},
            units=units,
            encoding=encoding,
            bits=bits,
            minimum=minimum,
            minimum_inclusive=minimum_inclusive,
            maximum=maximum,
            maximum_inclusive=maximum_inclusive,
        )
        self._parameters_by_name[parameter.name] = parameter
        return parameter

    def add_integer_parameter(
        self,
        name: str,
        aliases: dict[str, str] | None = None,
        initial_value: int | None = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: dict[str, str] | None = None,
        units: str | None = None,
        encoding: DataEncoding | None = None,
        signed: bool = True,
    ):
        if name in self._parameters_by_name:
            raise Exception(f"Space system already contains a parameter {name}")

        parameter = IntegerParameter(
            name=name,
            space_system=self,
            aliases=aliases or {},
            initial_value=initial_value,
            short_description=short_description,
            long_description=long_description,
            extra=extra or {},
            units=units,
            encoding=encoding,
            signed=signed,
        )
        self._parameters_by_name[parameter.name] = parameter
        return parameter

    def add_string_parameter(
        self,
        name: str,
        aliases: dict[str, str] | None = None,
        initial_value: str | None = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: dict[str, str] | None = None,
        units: str | None = None,
        encoding: DataEncoding | None = None,
    ):
        if name in self._parameters_by_name:
            raise Exception(f"Space system already contains a parameter {name}")

        parameter = StringParameter(
            name=name,
            space_system=self,
            aliases=aliases or {},
            initial_value=initial_value,
            short_description=short_description,
            long_description=long_description,
            extra=extra or {},
            units=units,
            encoding=encoding,
        )
        self._parameters_by_name[parameter.name] = parameter
        return parameter

    def add_container(
        self,
        name: str,
        aliases: dict[str, str] | None = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: dict[str, str] | None = None,
        entries: list["ParameterEntry | ContainerEntry"] | None = None,
        parent: "Container | None" = None,
        abstract: bool = False,
        restriction_criteria: "Expression | None" = None,
    ):
        if name in self._containers_by_name:
            raise Exception(f"Space system already contains a container {name}")

        container = Container(
            name=name,
            space_system=self,
            aliases=aliases or {},
            short_description=short_description,
            long_description=long_description,
            extra=extra or {},
            entries=entries or [],
            parent=parent,
            abstract=abstract,
            restriction_criteria=restriction_criteria,
        )
        self._containers_by_name[container.name] = container
        return container

    def add_command(
        self,
        name: str,
        aliases: dict[str, str] | None = None,
        short_description: str | None = None,
        long_description: str | None = None,
        parent: Optional["Command"] = None,
        assignments: dict[str, Any] | None = None,
        arguments: list["Argument"] | None = None,
        entries: list["CommandEntry"] | None = None,
        abstract: bool = False,
        restriction_criteria: Optional["Expression"] = None,
    ):
        if name in self._commands_by_name:
            raise Exception(f"Space system already contains a command {name}")

        command = Command(
            name=name,
            space_system=self,
            aliases=aliases,
            short_description=short_description,
            long_description=long_description,
            parent=parent,
            assignments=assignments,
            arguments=arguments,
            entries=entries,
            abstract=abstract,
            restriction_criteria=restriction_criteria,
        )
        self._commands_by_name[command.name] = command
        return command

    def find_parameter(self, name: str) -> "Parameter":
        """
        Find a parameter belonging directly to this space system.

        Raises an exception if no parameter is found
        """
        return self._parameters_by_name[name]

    def find_container(self, name: str) -> "Container":
        """
        Find a container belonging directly to this space system.

        Raises an exception if no container is found
        """
        return self._containers_by_name[name]

    def find_subsystem(self, name: str) -> "Subsystem":
        """
        Find a subsystem belonging directly to this space system.

        Raises an exception if no subsystem is found
        """
        return self._subsystems_by_name[name]


class Subsystem(SpaceSystem):
    """
    A subsystem is identical to a :class:`SpaceSystem`, but in addition keeps a reference
    to its parent space system.
    """

    def __init__(
        self,
        space_system: SpaceSystem,
        name: str,
        aliases: dict[str, str] | None = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: dict[str, str] | None = None,
    ):
        super().__init__(
            name=name,
            aliases=aliases,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
        )

        self.space_system: SpaceSystem = space_system
        """Parent space system"""

        if name in space_system._subsystems_by_name:
            raise Exception(
                "Space system {} already contains a subsystem {}".format(
                    space_system.qualified_name, name
                )
            )

        space_system._subsystems_by_name[name] = self

    @property
    def root(self) -> "SpaceSystem":
        """
        The top-most space system
        """
        parent = self.space_system
        while parent:
            if isinstance(parent, Subsystem):
                parent = parent.space_system
            else:
                parent = None

        return parent or self

    @property
    def qualified_name(self) -> str:
        """
        Fully qualified name of this space system (absolute path)
        """
        path = "/" + self.name

        parent = self.space_system
        while parent:
            path = "/" + parent.name + path

            if isinstance(parent, Subsystem):
                parent = parent.space_system
            else:
                parent = None

        return path


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
    reference: "Epoch | AbsoluteTimeParameter"
    encoding: TimeEncoding | None = None


@dataclass(kw_only=True)
class AggregateDataType(DataType):
    members: list["Member"] = field(default_factory=list)


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
class Parameter(DataType):
    name: str
    """Short name of this parameter"""

    space_system: SpaceSystem
    """Space system this parameter belongs to"""

    aliases: dict[str, str] = field(default_factory=dict)
    """Alternative names, keyed by namespace"""

    data_source: DataSource = DataSource.TELEMETERED
    """
    The nature of the source entity for which this parameter receives a value
    """

    @property
    def qualified_name(self):
        path = "/" + self.name

        parent = self.space_system
        while parent:
            path = "/" + parent.name + path
            if isinstance(parent, Subsystem):
                parent = parent.space_system
            else:
                parent = None

        return path


@dataclass(kw_only=True)
class AbsoluteTimeParameter(Parameter, AbsoluteTimeDataType):
    pass


@dataclass(kw_only=True)
class AggregateParameter(Parameter, AggregateDataType):
    members: list["Member"] = field(default_factory=list)


@dataclass(kw_only=True)
class ArrayParameter(Parameter, ArrayDataType):
    pass


@dataclass(kw_only=True)
class BinaryParameter(Parameter, BinaryDataType):
    pass


@dataclass(kw_only=True)
class BooleanParameter(Parameter, BooleanDataType):
    pass


@dataclass(kw_only=True)
class EnumeratedParameter(Parameter, EnumeratedDataType):
    alarm: EnumerationAlarm | None = None
    """Specification for alarm monitoring"""


@dataclass(kw_only=True)
class FloatParameter(Parameter, FloatDataType):
    pass


@dataclass(kw_only=True)
class IntegerParameter(Parameter, IntegerDataType):
    pass


@dataclass(kw_only=True)
class StringParameter(Parameter, StringDataType):
    pass


@dataclass
class Member(DataType):
    name: str


@dataclass(kw_only=True)
class AbsoluteTimeMember(Parameter, AbsoluteTimeDataType):
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


@dataclass
class Argument(DataType):
    name: str
    """Short name of this argument"""


@dataclass(kw_only=True)
class AbsoluteTimeArgument(Argument, AbsoluteTimeDataType):
    reference: Epoch


@dataclass(kw_only=True)
class AggregateArgument(Argument, AggregateDataType):
    members: list[Member] = field(default_factory=list)


@dataclass(kw_only=True)
class ArrayArgument(Argument, ArrayDataType):
    pass


@dataclass(kw_only=True)
class BinaryArgument(Argument, BinaryDataType):
    pass


@dataclass(kw_only=True)
class BooleanArgument(Argument, BooleanDataType):
    pass


@dataclass(kw_only=True)
class EnumeratedArgument(Argument, EnumeratedDataType):
    pass


@dataclass(kw_only=True)
class FloatArgument(Argument, FloatDataType):
    pass


@dataclass(kw_only=True)
class IntegerArgument(Argument, IntegerDataType):
    pass


@dataclass(kw_only=True)
class StringArgument(Argument, StringDataType):
    pass


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


@dataclass
class ParameterEntry:
    parameter: Parameter

    short_description: str | None = None
    """Oneline description"""

    reference_location: ReferenceLocation = ReferenceLocation.PREVIOUS_ENTRY
    location_in_bits: int = 0
    include_condition: Expression | None = None


@dataclass
class ContainerEntry:
    container: "Container"

    short_description: str | None = None
    """Oneline description"""

    reference_location: ReferenceLocation = ReferenceLocation.PREVIOUS_ENTRY
    location_in_bits: int = 0
    include_condition: Expression | None = None


@dataclass
class Container:
    """
    A collection of entries where each entry may be another container
    or a parameter.
    """

    name: str
    """Short name of this parameter"""

    space_system: SpaceSystem
    """Space system this container belongs to"""

    aliases: dict[str, str] = field(default_factory=dict)
    """Alternative names, keyed by namespace"""

    short_description: str | None = None
    """Oneline description"""

    long_description: str | None = None
    """Multiline description"""

    extra: dict[str, str] = field(default_factory=dict)
    """Arbitrary information, keyed by name"""

    entries: list[ParameterEntry | ContainerEntry] = field(default_factory=list)
    parent: Optional["Container"] = None
    abstract: bool = False
    restriction_criteria: Expression | None = None

    @property
    def qualified_name(self):
        path = "/" + self.name

        parent = self.space_system
        while parent:
            path = "/" + parent.name + path
            if isinstance(parent, Subsystem):
                parent = parent.space_system
            else:
                parent = None

        return path


@dataclass
class ArgumentEntry:
    argument: Argument

    short_description: str | None = None
    """Oneline description"""

    reference_location: ReferenceLocation = ReferenceLocation.PREVIOUS_ENTRY
    location_in_bits: int = 0
    include_condition: Expression | None = None


@dataclass
class FixedValueEntry:
    binary: bytes

    name: str | None = None

    short_description: str | None = None
    """Onleine description"""

    reference_location: ReferenceLocation = ReferenceLocation.PREVIOUS_ENTRY
    location_in_bits: int = 0
    include_condition: Expression | None = None
    bits: int | None = None


CommandEntry = ArgumentEntry | ParameterEntry | FixedValueEntry


class Command:
    def __init__(
        self,
        name: str,
        space_system: SpaceSystem,
        aliases: dict[str, str] | None = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: dict[str, str] | None = None,
        abstract: bool = False,
        parent: "Command | None" = None,
        restriction_criteria: Expression | None = None,
        assignments: dict[str, Any] | None = None,
        arguments: list[Argument] | None = None,
        entries: list[CommandEntry] | None = None,
        level: CommandLevel = CommandLevel.NORMAL,
        warning_message: str | None = None,
    ):
        self.name = name
        """Short name of this command"""

        self.space_system = space_system
        """Space system this command belongs to"""

        self.aliases = aliases or {}
        """Alternative names, keyed by namespace"""

        self.short_description = short_description
        """Oneline description"""

        self.long_description = long_description
        """Multiline description"""

        self.extra = extra or {}
        """Arbitrary information, keyed by name"""

        self.abstract = abstract
        self.parent = parent
        self.restriction_criteria = restriction_criteria
        self.assignments = assignments or {}
        self.arguments = arguments or []
        self._entries = entries

        self.transferred_to_range_verifier: "TransferredToRangeVerifier" | None = None
        self.sent_from_range_verifier: "SentFromRangeVerifier" | None = None
        self.received_verifier: "ReceivedVerifier" | None = None
        self.accepted_verifier: "AcceptedVerifier" | None = None
        self.queued_verifier: "QueuedVerifier" | None = None
        self.execution_verifiers: list["ExecutionVerifier"] = []
        self.complete_verifiers: list["CompleteVerifier"] = []
        self.failed_verifier: "FailedVerifier" | None = None

        self.level = level
        """
        The importance of this telecommand in terms of the nature and
        significance of its on-board effect.
        """

        self.warning_message = warning_message
        """Message explaining the importance of this telecommand"""

    @property
    def verifiers(self) -> list["Verifier"]:
        res = []
        if self.transferred_to_range_verifier:
            res.append(self.transferred_to_range_verifier)
        if self.sent_from_range_verifier:
            res.append(self.sent_from_range_verifier)
        if self.received_verifier:
            res.append(self.received_verifier)
        if self.accepted_verifier:
            res.append(self.accepted_verifier)
        if self.queued_verifier:
            res.append(self.queued_verifier)
        res.extend(self.execution_verifiers)
        res.extend(self.complete_verifiers)
        if self.failed_verifier:
            res.append(self.failed_verifier)
        return res

    @property
    def qualified_name(self):
        path = "/" + self.name

        parent = self.space_system
        while parent:
            path = "/" + parent.name + path
            if isinstance(parent, Subsystem):
                parent = parent.space_system
            else:
                parent = None

        return path

    def get_argument(self, name: str, visit_parents=True):
        """
        Return the argument for the given name

        :param visit_parents:
            Search upwards in parent commands
        """
        for argument in self.arguments:
            if argument.name == name:
                return argument

        if visit_parents and self.parent:
            return self.parent.get_argument(name)
        else:
            return None

    @property
    def entries(self) -> list[CommandEntry]:
        """
        The order and placement of entries in the encoded command.

        If unset, the default behaviour is to have a consecutive
        entry for each argument that has an encoding defined, in the
        same order as the arguments.
        """
        if self._entries is None:
            res = []
            for argument in self.arguments:
                if argument.encoding:
                    res.append(ArgumentEntry(argument))
            return res
        else:
            return self._entries

    @entries.setter
    def entries(self, entries: list[CommandEntry]):
        self._entries = entries


class ContainerCheck:
    def __init__(self, container: Container):
        self.container = container


class ExpressionCheck:
    def __init__(self, expression: Expression):
        self.expression = expression


Check: TypeAlias = ContainerCheck | ExpressionCheck


@dataclass
class Verifier:
    check: Check
    """Check to perform"""

    timeout: float
    """How long to wait for a check result (in seconds)"""

    delay: float = 0
    """Wait time before starting to check (in seconds)"""

    on_success: TerminationAction | None = None
    """What it means for the whole command, when this single verifier succeeds"""

    on_fail: TerminationAction | None = None
    """What it means for the whole command, when this single verifier fails"""

    on_timeout: TerminationAction | None = None
    """What it means for the whole command, when this single verifier times out"""


@dataclass
class TransferredToRangeVerifier(Verifier):
    """
    A verifier that checks whether the command has been received to the network
    that connects the ground system to the spacecraft.

    The result of this verifier must originate from something other than the
    spacecraft.
    """

    on_fail: TerminationAction | None = TerminationAction.FAIL
    """What it means for the whole command, when this single verifier fails"""


@dataclass
class SentFromRangeVerifier(Verifier):
    """
    A verifier that checks whether the command been transmitted to the
    spacecraft by the network that connects the ground system to the
    spacecraft.

    The result of this verifier must originate from something other than the
    space system.
    """

    on_fail: TerminationAction | None = TerminationAction.FAIL
    """What it means for the whole command, when this single verifier fails"""


@dataclass
class ReceivedVerifier(Verifier):
    """
    A verifier that checks that the space system has received the command
    """

    on_fail: TerminationAction | None = TerminationAction.FAIL
    """What it means for the whole command, when this single verifier fails"""


@dataclass
class AcceptedVerifier(Verifier):
    """
    A verifier that checks that the space system has accepted the command
    """

    on_fail: TerminationAction | None = TerminationAction.FAIL
    """What it means for the whole command, when this single verifier fails"""


@dataclass
class QueuedVerifier(Verifier):
    """
    A verifier that checks that the command is scheduled for execution by
    the space system.
    """

    on_fail: TerminationAction | None = TerminationAction.FAIL
    """What it means for the whole command, when this single verifier fails"""


@dataclass
class ExecutionVerifier(Verifier):
    """
    A verifier that checks that the command is being executed.
    """

    on_fail: TerminationAction | None = TerminationAction.FAIL
    """What it means for the whole command, when this single verifier fails"""


@dataclass
class CompleteVerifier(Verifier):
    """
    A verifier that checks whether the command to be considered completed
    """

    on_success: TerminationAction | None = TerminationAction.SUCCESS
    """What it means for the whole command, when this single verifier succeeds"""

    on_fail: TerminationAction | None = TerminationAction.FAIL
    """What it means for the whole command, when this single verifier fails"""

    return_parameter: Parameter | None = None


@dataclass
class FailedVerifier(Verifier):
    """
    A verifier that checks that the command failed.
    """

    on_success: TerminationAction | None = TerminationAction.FAIL
    """What it means for the whole command, when this single verifier succeeds"""

    return_parameter: Parameter | None = None
