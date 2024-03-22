from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from yamcs.pymdb.ancillary import AncillaryData

if TYPE_CHECKING:
    from yamcs.pymdb.parameters import Parameter


class InputParameter:
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
        Name to be used inside the algorithm. If not specified, a name
        is derived from the basename of the parameter.
        """


class JavaAlgorithm:
    def __init__(
        self,
        java: str,
        *,
        inputs: Sequence[InputParameter] | None = None,
        extra: Mapping[str, str] | AncillaryData | None = None,
    ):
        self.java: str = java

        self.inputs: list[InputParameter] = list(inputs or [])
        """Parameter inputs available to the algorithm"""

        self.extra: AncillaryData
        """Arbitrary information, keyed by name"""
        if isinstance(extra, AncillaryData):
            self.extra = extra
        else:
            self.extra = AncillaryData(extra)


hex_string_decoder = JavaAlgorithm("org.yamcs.algo.HexStringDecoder")
"""
Decoder algorithm that returns the `string` value in hex format of read bytes.
This is intended to be used for special use cases where the hex value
represents the actual string value.

This is intended to be used with a custom transformation for the
:class:`.BinaryDataEncoding` of a string parameter.

The implementation assumes a fixed-size encoding.
"""

remaining_binary_decoder = JavaAlgorithm("org.yamcs.algo.RemainingBinaryDecoder")
"""
A decoder that returns a binary value containing all of the remaining bytes.

An example where this may be useful is a packet that contains an arbitrarily
sized blob of data with no length indication.
"""


reverse_binary_decoder = JavaAlgorithm("org.yamcs.algo.ReverseBinaryDecoder")
"""
A decoder that returns a binary value containing all of the remaining bytes.

An example where this may be useful is a packet that contains an arbitrarily
sized blob of data with no length indication.
"""

reverse_binary_encoder = JavaAlgorithm("org.yamcs.algo.ReverseBinaryEncoder")
"""
A custom data encoder that converts provided binary to encoded binary in the
reverse byte order.
"""
