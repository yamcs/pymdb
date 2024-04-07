from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from yamcs.pymdb.ancillary import AncillaryData

if TYPE_CHECKING:
    from yamcs.pymdb.containers import Container
    from yamcs.pymdb.parameters import Parameter
    from yamcs.pymdb.systems import System


class Algorithm:
    def __init__(
        self,
        system: System,
        name: str,
        *,
        aliases: Mapping[str, str] | None = None,
        short_description: str | None = None,
        long_description: str | None = None,
        extra: Mapping[str, str] | None = None,
        language: str,
        text: str,
        inputs: Sequence[InputParameter] | None = None,
        outputs: Sequence[OutputParameter] | None = None,
        triggers: Sequence[Trigger] | None = None,
    ):
        self.name: str = name
        """Short name of this algorithm"""

        self.system: System = system
        """System this algorithm belongs to"""

        self.aliases: dict[str, str] = dict(aliases or {})
        """Alternative names, keyed by namespace"""

        self.short_description: str | None = short_description
        """Oneline description"""

        self.long_description: str | None = long_description
        """Multiline description"""

        self.extra: dict[str, str] = dict(extra or {})
        """Arbitrary information, keyed by name"""

        self.language: str = language
        """Algorithm language"""

        self.text: str = text
        """Algorithm text"""

        self.inputs: list[InputParameter] = list(inputs or [])
        """Parameter inputs available to the algorithm"""

        self.outputs: list[OutputParameter] = list(outputs or [])
        """Parameter outputs available to the algorithm"""

        self.triggers: list[Trigger] = list(triggers or [])
        """Algorithm triggers"""

        if name in system._algorithms_by_name:
            raise Exception(f"System already contains an algorithm {name}")
        system._algorithms_by_name[name] = self

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

    def __lt__(self, other: Algorithm) -> bool:
        return self.qualified_name < other.qualified_name

    def __str__(self) -> str:
        return self.qualified_name


class InputParameter:
    def __init__(
        self,
        parameter: Parameter | str,
        *,
        name: str | None = None,
        required: bool = False,
    ):
        self.parameter = parameter
        """Reference parameter"""

        self.name: str | None = name
        """
        Variable name to be used inside the algorithm. If not specified, a
        name is derived from the basename of the parameter.
        """

        self.required: bool = required


class OutputParameter:
    def __init__(
        self,
        parameter: Parameter | str,
        *,
        name: str | None = None,
    ):
        self.parameter = parameter
        """Reference parameter"""

        self.name: str | None = name
        """
        Variable name to be used inside the algorithm. If not specified, a
        name is derived from the basename of the parameter.
        """


class Trigger:
    pass


class ParameterTrigger(Trigger):

    def __init__(self, parameter: Parameter | str) -> None:
        self.parameter = parameter
        """Reference parameter"""


class ContainerTrigger(Trigger):

    def __init__(self, container: Container | str) -> None:
        self.container = container
        """Reference container"""


class UnnamedAlgorithm:
    def __init__(
        self,
        language: str,
        text: str,
        *,
        inputs: Sequence[InputParameter] | None = None,
        extra: Mapping[str, str] | AncillaryData | None = None,
    ):
        self.language: str = language
        self.text: str = text

        self.inputs: list[InputParameter] = list(inputs or [])
        """Parameter inputs available to the algorithm"""

        self.extra: AncillaryData
        """Arbitrary information, keyed by name"""
        if isinstance(extra, AncillaryData):
            self.extra = extra
        else:
            self.extra = AncillaryData(extra)


class UnnamedJavaAlgorithm(UnnamedAlgorithm):
    def __init__(
        self,
        java: str,
        *,
        inputs: Sequence[InputParameter] | None = None,
        extra: Mapping[str, str] | AncillaryData | None = None,
    ):
        super().__init__(
            language="Java",
            text=java,
            inputs=inputs,
            extra=extra,
        )


class UnnamedJavaScriptAlgorithm(UnnamedAlgorithm):
    def __init__(
        self,
        js: str,
        *,
        inputs: Sequence[InputParameter] | None = None,
        extra: Mapping[str, str] | AncillaryData | None = None,
    ):
        super().__init__(
            language="JavaScript",
            text=js,
            inputs=inputs,
            extra=extra,
        )


hex_string_decoder = UnnamedJavaAlgorithm("org.yamcs.algo.HexStringDecoder")
"""
Decoder algorithm that returns the `string` value in hex format of read bytes.
This is intended to be used for special use cases where the hex value
represents the actual string value.

This is intended to be used with a custom transformation for the
:class:`.BinaryEncoding` of a string parameter.

The implementation assumes a fixed-size encoding.
"""

remaining_binary_decoder = UnnamedJavaAlgorithm("org.yamcs.algo.RemainingBinaryDecoder")
"""
A decoder that returns a binary value containing all of the remaining bytes.

An example where this may be useful is a packet that contains an arbitrarily
sized blob of data with no length indication.
"""


reverse_binary_decoder = UnnamedJavaAlgorithm("org.yamcs.algo.ReverseBinaryDecoder")
"""
A decoder that returns a binary value containing all of the remaining bytes.

An example where this may be useful is a packet that contains an arbitrarily
sized blob of data with no length indication.
"""

reverse_binary_encoder = UnnamedJavaAlgorithm("org.yamcs.algo.ReverseBinaryEncoder")
"""
A custom data encoder that converts provided binary to encoded binary in the
reverse byte order.
"""
