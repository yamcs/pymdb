from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Literal

from yamcs.pymdb.containers import ParameterEntry
from yamcs.pymdb.datatypes import (
    AbsoluteTimeDataType,
    AggregateDataType,
    ArrayDataType,
    BinaryDataType,
    BooleanDataType,
    Choices,
    DataType,
    EnumeratedDataType,
    Epoch,
    FloatDataType,
    IntegerDataType,
    Member,
    StringDataType,
)
from yamcs.pymdb.encodings import Encoding, TimeEncoding
from yamcs.pymdb.expressions import Expression
from yamcs.pymdb.verifiers import (
    AcceptedVerifier,
    CompleteVerifier,
    ExecutionVerifier,
    FailedVerifier,
    QueuedVerifier,
    ReceivedVerifier,
    SentFromRangeVerifier,
    TransferredToRangeVerifier,
    Verifier,
)

if TYPE_CHECKING:
    from yamcs.pymdb.calibrators import Calibrator
    from yamcs.pymdb.systems import System


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


class Argument(DataType):
    def __init__(
        self,
        name: str,
        *,
        default: Any = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        units: str | None = None,
        encoding: Encoding | None = None,
    ) -> None:
        self.name: str = name
        """Short name of this argument"""

        self.default: Any = default
        """Default value"""

        DataType.__init__(
            self,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )

        def __str__(self) -> str:
            return self.name


class AbsoluteTimeArgument(Argument, AbsoluteTimeDataType):
    def __init__(
        self,
        name: str,
        reference: Epoch,
        *,
        default: Any = None,
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
        Argument.__init__(
            self,
            name=name,
            default=default,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )


class AggregateArgument(Argument, AggregateDataType):
    def __init__(
        self,
        name: str,
        members: Sequence[Member],
        *,
        default: Any = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        encoding: Encoding | None = None,
    ) -> None:
        AggregateDataType.__init__(
            self,
            members=members,
        )
        Argument.__init__(
            self,
            name=name,
            default=default,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            encoding=encoding,
        )


class ArrayArgument(Argument, ArrayDataType):
    def __init__(
        self,
        name: str,
        data_type: DataType,
        length: int,
        *,
        default: Any = None,
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
        Argument.__init__(
            self,
            name=name,
            default=default,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            encoding=encoding,
        )


class BinaryArgument(Argument, BinaryDataType):
    def __init__(
        self,
        name: str,
        *,
        min_length: int | None = None,
        max_length: int | None = None,
        default: Any = None,
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
        Argument.__init__(
            self,
            name=name,
            default=default,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )


class BooleanArgument(Argument, BooleanDataType):
    def __init__(
        self,
        name: str,
        *,
        zero_string_value: str = "False",
        one_string_value: str = "True",
        default: Any = None,
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
        Argument.__init__(
            self,
            name=name,
            default=default,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )


class EnumeratedArgument(Argument, EnumeratedDataType):
    def __init__(
        self,
        name: str,
        choices: Choices,
        *,
        default: Any = None,
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
        Argument.__init__(
            self,
            name=name,
            default=default,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )


class FloatArgument(Argument, FloatDataType):
    def __init__(
        self,
        name: str,
        bits: Literal[32, 64] = 32,
        *,
        minimum: float | None = None,
        minimum_inclusive: bool = True,
        maximum: float | None = None,
        maximum_inclusive: bool = True,
        default: Any = None,
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
        Argument.__init__(
            self,
            name=name,
            default=default,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )


class IntegerArgument(Argument, IntegerDataType):
    def __init__(
        self,
        name: str,
        *,
        signed: bool = True,
        bits: int = 32,
        minimum: int | None = None,
        maximum: int | None = None,
        default: Any = None,
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
        Argument.__init__(
            self,
            name=name,
            default=default,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )


class StringArgument(Argument, StringDataType):
    def __init__(
        self,
        name: str,
        *,
        min_length: int | None = None,
        max_length: int | None = None,
        default: Any = None,
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
        Argument.__init__(
            self,
            name=name,
            default=default,
            short_description=short_description,
            long_description=long_description,
            extra=extra,
            units=units,
            encoding=encoding,
        )


class ArgumentEntry:
    def __init__(
        self,
        argument: Argument,
        *,
        short_description: str | None = None,
        absolute: bool = False,
        location_in_bits: int = 0,
        condition: Expression | None = None,
    ) -> None:
        self.argument: Argument = argument

        self.short_description: str | None = short_description
        """Oneline description"""

        self.absolute: bool = absolute
        self.location_in_bits: int = location_in_bits
        self.condition: Expression | None = condition


class FixedValueEntry:
    def __init__(
        self,
        binary: bytes,
        name: str | None = None,
        *,
        short_description: str | None = None,
        absolute: bool = False,
        location_in_bits: int = 0,
        condition: Expression | None = None,
        bits: int | None = None,
    ) -> None:
        self.binary: bytes = binary

        self.name: str | None = name

        self.short_description: str | None = short_description
        """Onleine description"""

        self.absolute: bool = absolute
        self.location_in_bits: int = location_in_bits
        self.condition: Expression | None = condition
        self.bits: int | None = bits


CommandEntry = ArgumentEntry | ParameterEntry | FixedValueEntry


class Command:
    def __init__(
        self,
        system: System,
        name: str,
        *,
        aliases: Mapping[str, str] | None = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        abstract: bool = False,
        parent: Command | None = None,
        condition: Expression | None = None,
        assignments: Mapping[str, Any] | None = None,
        arguments: Sequence[Argument] | None = None,
        entries: Sequence[CommandEntry] | None = None,
        level: CommandLevel = CommandLevel.NORMAL,
        warning_message: str | None = None,
    ):
        self.name: str = name
        """Short name of this command"""

        self.system: System = system
        """System this command belongs to"""

        self.aliases: dict[str, str] = dict(aliases or {})
        """Alternative names, keyed by namespace"""

        self.short_description: str | None = short_description
        """Oneline description"""

        self.long_description: str | None = long_description
        """Multiline description"""

        self.extra: dict[str, str] = dict(extra or {})
        """Arbitrary information, keyed by name"""

        self.abstract: bool = abstract
        self.parent: Command | str | None = parent
        self.condition: Expression | None = condition
        self.assignments: dict[str, Any] = dict(assignments or {})
        self.arguments: list[Argument] = list(arguments or [])
        self._entries: list[CommandEntry] | None = (
            list(entries) if entries is not None else None
        )

        self.transferred_to_range_verifier: TransferredToRangeVerifier | None = None
        self.sent_from_range_verifier: SentFromRangeVerifier | None = None
        self.received_verifier: ReceivedVerifier | None = None
        self.accepted_verifier: AcceptedVerifier | None = None
        self.queued_verifier: QueuedVerifier | None = None
        self.execution_verifiers: list[ExecutionVerifier] = []
        self.complete_verifiers: list[CompleteVerifier] = []
        self.failed_verifier: FailedVerifier | None = None

        self.level: CommandLevel = level
        """
        The importance of this telecommand in terms of the nature and
        significance of its on-board effect.
        """

        self.warning_message: str | None = warning_message
        """Message explaining the importance of this telecommand"""

        if name in system._commands_by_name:
            raise Exception(f"System already contains a command {name}")
        system._commands_by_name[name] = self

    @property
    def verifiers(self) -> list[Verifier]:
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

    def get_argument(self, name: str, visit_parents=True):
        """
        Return the argument for the given name

        :param visit_parents:
            Search upwards in parent commands
        """
        for argument in self.arguments:
            if argument.name == name:
                return argument

        if visit_parents and self.parent and isinstance(self.parent, Command):
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
    def entries(self, entries: Sequence[CommandEntry]):
        self._entries = list(entries)

    def __lt__(self, other: Command) -> bool:
        return self.qualified_name < other.qualified_name

    def __str__(self) -> str:
        return self.qualified_name
