from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING

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
        path = "/" + self.name

        parent = self.system
        while parent:
            path = "/" + parent.name + path
            parent = getattr(parent, "system", None)

        return path
