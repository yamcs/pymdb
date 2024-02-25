from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING

from yamcs.pymdb.datatypes import AggregateDataType, ArrayDataType

if TYPE_CHECKING:
    from yamcs.pymdb.expressions import Expression
    from yamcs.pymdb.parameters import Parameter
    from yamcs.pymdb.systems import System


class ReferenceLocation(Enum):
    CONTAINER_START = auto()
    PREVIOUS_ENTRY = auto()


class ParameterEntry:
    def __init__(
        self,
        parameter: Parameter,
        short_description: str | None = None,
        reference_location: ReferenceLocation = ReferenceLocation.PREVIOUS_ENTRY,
        location_in_bits: int = 0,
        include_condition: Expression | None = None,
    ) -> None:
        self.parameter: Parameter = parameter

        self.short_description: str | None = short_description
        """Oneline description"""

        self.reference_location: ReferenceLocation = reference_location
        self.location_in_bits: int = location_in_bits
        self.include_condition: Expression | None = include_condition

    def __str__(self) -> str:
        return self.parameter.__str__()


class ContainerEntry:
    def __init__(
        self,
        container: Container,
        short_description: str | None = None,
        reference_location: ReferenceLocation = ReferenceLocation.PREVIOUS_ENTRY,
        location_in_bits: int = 0,
        include_condition: Expression | None = None,
    ) -> None:
        self.container: Container = container

        self.short_description: str | None = short_description
        """Oneline description"""

        self.reference_location: ReferenceLocation = reference_location
        self.location_in_bits: int = location_in_bits
        self.include_condition: Expression | None = include_condition

    def __str__(self) -> str:
        return self.container.__str__()


class Container:
    """
    A collection of entries where each entry may be another container
    or a parameter.
    """

    def __init__(
        self,
        system: System,
        name: str,
        entries: list[ParameterEntry | ContainerEntry] | None = None,
        *,
        parent: Container | None = None,
        abstract: bool = False,
        restriction_criteria: Expression | None = None,
        aliases: dict[str, str] | None = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: dict[str, str] | None = None,
        bits: int | None = None,
        hint_partition: bool = False,
    ):
        self.name: str = name
        """Short name of this parameter"""

        self.system: System = system
        """System this container belongs to"""

        self.aliases: dict[str, str] = aliases or {}
        """Alternative names, keyed by namespace"""

        self.short_description: str | None = short_description
        """Oneline description"""

        self.long_description: str | None = long_description
        """Multiline description"""

        self.extra: dict[str, str] = extra or {}
        """Arbitrary information, keyed by name"""

        self.bits: int | None = bits
        """
        Explicit fixed size in bits. Usually unnecessary, because Yamcs
        can derive a lot from the entries.

        If provided, Yamcs can use this information to speed up parameter
        extraction, especially when this container is used as an entry
        into another container.

        If this container extends base container(s), their size should be
        included.
        """

        self.hint_partition: bool = hint_partition
        """
        Hint that this container's name should be used for partitioning when
        stored to Yamcs.
        """

        self.entries: list[ParameterEntry | ContainerEntry] = entries or []
        self.parent: Container | None = parent
        self.abstract: bool = abstract
        self.restriction_criteria: Expression | None = restriction_criteria

        if name in system._containers_by_name:
            raise Exception(
                "System {} already contains a container {}".format(
                    system.qualified_name, name
                )
            )

        system._containers_by_name[name] = self

    @property
    def qualified_name(self):
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

    def fit_entries(self):
        """
        Automatically set a fixed size to this container based on the known entries.
        """
        if self.parent:
            raise NotImplementedError()

        max_pos = 0

        prev_pos = 0
        for entry in self.entries:
            if isinstance(entry, ParameterEntry):
                parameter = entry.parameter
                bits = None
                if isinstance(parameter, ArrayDataType):
                    length = parameter.length
                    encoding = parameter.data_type.encoding
                    if encoding and encoding.bits:
                        bits = length * encoding.bits
                elif isinstance(parameter, AggregateDataType):
                    raise NotImplementedError()
                elif parameter.encoding and parameter.encoding.bits:
                    bits = parameter.encoding.bits

                if not bits:
                    raise Exception(f"Cannot determine size of {entry.parameter}")

                pos = entry.location_in_bits
                if entry.reference_location == ReferenceLocation.PREVIOUS_ENTRY:
                    pos += prev_pos

                pos += bits

                prev_pos = pos
                if pos > max_pos:
                    max_pos = pos
            else:
                raise NotImplementedError()

        self.bits = max_pos

    def __lt__(self, other: Container) -> bool:
        return self.qualified_name < other.qualified_name

    def __str__(self) -> str:
        return self.qualified_name
