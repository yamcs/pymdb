from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from yamcs.pymdb.datatypes import AggregateDataType, ArrayDataType, DynamicInteger

if TYPE_CHECKING:
    from yamcs.pymdb.expressions import Expression
    from yamcs.pymdb.parameters import Parameter
    from yamcs.pymdb.systems import System


class ParameterEntry:
    def __init__(
        self,
        parameter: Parameter,
        location_in_bits: int = 0,
        *,
        absolute: bool = False,
        short_description: str | None = None,
        condition: Expression | None = None,
    ) -> None:
        self.parameter: Parameter = parameter

        self.short_description: str | None = short_description
        """Oneline description"""

        self.absolute: bool = absolute
        self.location_in_bits: int = location_in_bits
        self.condition: Expression | None = condition

    def __str__(self) -> str:
        return self.parameter.__str__()


class ContainerEntry:
    def __init__(
        self,
        container: Container,
        short_description: str | None = None,
        absolute: bool = False,
        location_in_bits: int = 0,
        condition: Expression | None = None,
    ) -> None:
        self.container: Container = container

        self.short_description: str | None = short_description
        """Oneline description"""

        self.absolute: bool = absolute
        self.location_in_bits: int = location_in_bits
        self.condition: Expression | None = condition

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
        entries: Sequence[ParameterEntry | ContainerEntry] | None = None,
        *,
        parent: Container | str | None = None,
        abstract: bool = False,
        condition: Expression | None = None,
        aliases: Mapping[str, str] | None = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        bits: int | None = None,
        rate: float | None = None,
        hint_partition: bool = False,
    ):
        self.name: str = name
        """Short name of this parameter"""

        self.system: System = system
        """System this container belongs to"""

        self.aliases: dict[str, str] = dict(aliases or {})
        """Alternative names, keyed by namespace"""

        self.short_description: str | None = short_description
        """Oneline description"""

        self.long_description: str | None = long_description
        """Multiline description"""

        self.extra: dict[str, str] = dict(extra or {})
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

        self.rate: float | None = rate
        """
        Expected rate in seconds.

        This is used by Yamcs to determine parameter expiration. A parameter's
        realtime value is considered expired when ``1.9 * rate`` has passed
        without a new update (where ``1.9`` is a configurable tolerance multiplier).

        If ``None``, the contained parameters are not checked for expiration.
        """

        self.hint_partition: bool = hint_partition
        """
        Hint that this container's name should be used for partitioning when
        stored to Yamcs.
        """

        self.entries: list[ParameterEntry | ContainerEntry] = list(entries or [])
        self.parent: Container | str | None = parent
        self.abstract: bool = abstract
        self.condition: Expression | None = condition
        """Restriction criteria for this container."""

        if name in system._containers_by_name:
            raise Exception(
                "System {} already contains a container {}".format(
                    system.qualified_name, name
                )
            )

        system._containers_by_name[name] = self

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
                        if isinstance(length, DynamicInteger):
                            raise Exception("Cannot determine dynamic integer value")
                        bits = length * encoding.bits
                elif isinstance(parameter, AggregateDataType):
                    raise NotImplementedError()
                elif parameter.encoding and parameter.encoding.bits:
                    bits = parameter.encoding.bits

                if not bits:
                    raise Exception(f"Cannot determine size of {entry.parameter}")

                pos = entry.location_in_bits
                if not entry.absolute:
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
