from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from yamcs.pymdb.commands import Argument, Command, CommandEntry
from yamcs.pymdb.containers import Container
from yamcs.pymdb.parameters import (
    AbsoluteTimeParameter,
    AggregateParameter,
    ArrayParameter,
    BinaryParameter,
    BooleanParameter,
    EnumeratedParameter,
    EnumerationAlarm,
    FloatParameter,
    IntegerParameter,
    Parameter,
    StringParameter,
)

if TYPE_CHECKING:
    from yamcs.pymdb.datatypes import Choices, DataType, Epoch, Member
    from yamcs.pymdb.encodings import BinaryDataEncoding, DataEncoding, TimeEncoding
    from yamcs.pymdb.expressions import Expression


class System:
    """
    The top-level system is the root element for the set of metadata
    necessary to monitor and command a space device, such as a satellite.

    A system defines a namespace.

    Metadata areas include: telemetry, calibration, alarm, algorithms and
    commands.

    A system may have child :class:`Subsystem`s, forming a system tree.
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
        """Short name of this system"""

        self.aliases: dict[str, str] = aliases or {}
        """Alternative names, keyed by namespace"""

        self.short_description: str | None = short_description
        """Oneline description"""

        self.long_description: str | None = long_description
        """Multiline description"""

        self.extra: dict[str, str] = extra or {}
        """Arbitrary information, keyed by name"""

        self._commands_by_name: dict[str, Command] = {}
        self._containers_by_name: dict[str, Container] = {}
        self._parameters_by_name: dict[str, Parameter] = {}
        self._subsystems_by_name: dict[str, Subsystem] = {}

    @property
    def root(self) -> System:
        """
        The top-most system
        """
        return self

    @property
    def qualified_name(self) -> str:
        return "/" + self.name

    @property
    def containers(self) -> list[Container]:
        """
        Containers directly belonging to this system
        """
        return list(self._containers_by_name.values())

    @property
    def commands(self) -> list[Command]:
        """
        Commands directly belonging to this system
        """
        return list(self._commands_by_name.values())

    @property
    def parameters(self) -> list[Parameter]:
        """
        Parameters directly belonging to this system
        """
        return list(self._parameters_by_name.values())

    @property
    def subsystems(self) -> list[Subsystem]:
        """
        Subsystems directly belonging to this system
        """
        return list(self._subsystems_by_name.values())

    def add_parameter(self, parameter: Parameter):
        if parameter.name in self._parameters_by_name:
            raise Exception(f"System already contains a parameter {parameter.name}")

        self._parameters_by_name[parameter.name] = parameter
        return parameter

    def add_absolute_time_parameter(
        self,
        name: str,
        reference: Epoch | AbsoluteTimeParameter,
        aliases: dict[str, str] | None = None,
        initial_value: Any = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: dict[str, str] | None = None,
        units: str | None = None,
        encoding: TimeEncoding | None = None,
    ):
        if name in self._parameters_by_name:
            raise Exception(f"System already contains a parameter {name}")

        parameter = AbsoluteTimeParameter(
            name=name,
            system=self,
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
        members: list[Member],
        aliases: dict[str, str] | None = None,
        initial_value: dict[str, Any] | None = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: dict[str, str] | None = None,
        units: str | None = None,
        encoding: DataEncoding | None = None,
    ):
        if name in self._parameters_by_name:
            raise Exception(f"System already contains a parameter {name}")

        parameter = AggregateParameter(
            name=name,
            system=self,
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
        data_type: DataType,
        aliases: dict[str, str] | None = None,
        initial_value: list[Any] | None = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: dict[str, str] | None = None,
    ):
        if name in self._parameters_by_name:
            raise Exception(f"System already contains a parameter {name}")

        parameter = ArrayParameter(
            name=name,
            system=self,
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
            raise Exception(f"System already contains a parameter {name}")

        parameter = BinaryParameter(
            name=name,
            system=self,
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
            raise Exception(f"System already contains a parameter {name}")

        parameter = BooleanParameter(
            name=name,
            system=self,
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
            raise Exception(f"System already contains a parameter {name}")

        parameter = EnumeratedParameter(
            name=name,
            system=self,
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
            raise Exception(f"System already contains a parameter {name}")

        parameter = FloatParameter(
            name=name,
            system=self,
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
            raise Exception(f"System already contains a parameter {name}")

        parameter = IntegerParameter(
            name=name,
            system=self,
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
            raise Exception(f"System already contains a parameter {name}")

        parameter = StringParameter(
            name=name,
            system=self,
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

    def add_command(
        self,
        name: str,
        aliases: dict[str, str] | None = None,
        short_description: str | None = None,
        long_description: str | None = None,
        parent: Command | None = None,
        assignments: dict[str, Any] | None = None,
        arguments: list[Argument] | None = None,
        entries: list[CommandEntry] | None = None,
        abstract: bool = False,
        restriction_criteria: Expression | None = None,
    ):
        if name in self._commands_by_name:
            raise Exception(f"System already contains a command {name}")

        command = Command(
            name=name,
            system=self,
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

    def find_parameter(self, name: str) -> Parameter:
        """
        Find a parameter belonging directly to this system.

        Raises an exception if no parameter is found
        """
        return self._parameters_by_name[name]

    def find_container(self, name: str) -> Container:
        """
        Find a container belonging directly to this system.

        Raises an exception if no container is found
        """
        return self._containers_by_name[name]

    def find_subsystem(self, name: str) -> Subsystem:
        """
        Find a subsystem belonging directly to this system.

        Raises an exception if no subsystem is found
        """
        return self._subsystems_by_name[name]


class Subsystem(System):
    """
    A subsystem is identical to a :class:`System`, but in addition keeps a reference
    to its parent system.
    """

    def __init__(
        self,
        system: System,
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

        self.system: System = system
        """Parent system"""

        if name in system._subsystems_by_name:
            raise Exception(
                "System {} already contains a subsystem {}".format(
                    system.qualified_name, name
                )
            )

        system._subsystems_by_name[name] = self

    @property
    def root(self) -> System:
        """
        The top-most system
        """
        parent = self.system
        while parent:
            if isinstance(parent, Subsystem):
                parent = parent.system
            else:
                parent = None

        return parent or self

    @property
    def qualified_name(self) -> str:
        """
        Fully qualified name of this system (absolute path)
        """
        path = "/" + self.name

        parent = self.system
        while parent:
            path = "/" + parent.name + path

            if isinstance(parent, Subsystem):
                parent = parent.system
            else:
                parent = None

        return path
