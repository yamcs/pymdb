from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any

from yamcs.pymdb.containers import ParameterEntry, ReferenceLocation
from yamcs.pymdb.datatypes import (
    AbsoluteTimeDataType,
    AggregateDataType,
    ArrayDataType,
    BinaryDataType,
    BooleanDataType,
    DataType,
    EnumeratedDataType,
    Epoch,
    FloatDataType,
    IntegerDataType,
    Member,
    StringDataType,
)
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
        system: System,
        aliases: dict[str, str] | None = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: dict[str, str] | None = None,
        abstract: bool = False,
        parent: Command | None = None,
        restriction_criteria: Expression | None = None,
        assignments: dict[str, Any] | None = None,
        arguments: list[Argument] | None = None,
        entries: list[CommandEntry] | None = None,
        level: CommandLevel = CommandLevel.NORMAL,
        warning_message: str | None = None,
    ):
        self.name = name
        """Short name of this command"""

        self.system = system
        """System this command belongs to"""

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

        self.transferred_to_range_verifier: TransferredToRangeVerifier | None = None
        self.sent_from_range_verifier: SentFromRangeVerifier | None = None
        self.received_verifier: ReceivedVerifier | None = None
        self.accepted_verifier: AcceptedVerifier | None = None
        self.queued_verifier: QueuedVerifier | None = None
        self.execution_verifiers: list[ExecutionVerifier] = []
        self.complete_verifiers: list[CompleteVerifier] = []
        self.failed_verifier: FailedVerifier | None = None

        self.level = level
        """
        The importance of this telecommand in terms of the nature and
        significance of its on-board effect.
        """

        self.warning_message = warning_message
        """Message explaining the importance of this telecommand"""

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
    def qualified_name(self):
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
