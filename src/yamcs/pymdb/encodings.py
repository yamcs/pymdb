from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from yamcs.pymdb.algorithms import UnnamedAlgorithm


class Charset(Enum):
    """String encoding"""

    US_ASCII = auto()
    """US-ASCII"""

    ISO_8859_1 = auto()
    """ISO-8859-1"""

    WINDOWS_1252 = auto()
    """Windows-1252"""

    UTF_8 = auto()
    """UTF-8"""

    UTF_16 = auto()
    """UTF-16"""

    UTF_16LE = auto()
    """UTF-16LE"""

    UTF_16BE = auto()
    """UTF-16BE"""

    UTF_32 = auto()
    """UTF-32"""

    UTF_32LE = auto()
    """UTF-32LE"""

    UTF_32BE = auto()
    """UTF-16BE"""


class FloatEncodingScheme(Enum):
    """Float encoding"""

    IEEE754_1985 = auto()
    """IEEE 754-1985"""

    MILSTD_1750A = auto()
    """MIL-STD-1750A"""


class IntegerEncodingScheme(Enum):
    """Integer encoding"""

    UNSIGNED = auto()
    """Unsigned"""

    SIGN_MAGNITUDE = auto()
    """Sign-magnitude"""

    TWOS_COMPLEMENT = auto()
    """Two's complement"""

    ONES_COMPLEMENT = auto()
    """Ones' complement"""


class Encoding:
    def __init__(self, bits: int | None = None) -> None:
        self.bits = bits


class BinaryEncoding(Encoding):
    def __init__(
        self,
        bits: int | None = None,
        length_bits: int | None = None,
        encoder: UnnamedAlgorithm | None = None,
        decoder: UnnamedAlgorithm | None = None,
    ) -> None:
        super().__init__(bits=bits)

        self.length_bits: int | None = length_bits
        """
        Length in bits of a leading size tag
        """

        self.encoder: UnnamedAlgorithm | None = encoder
        """
        Custom encoder, when this encoding is used for telecommanding
        """

        self.decoder: UnnamedAlgorithm | None = decoder
        """
        Custom decoder, when this encoding is used for telemetry
        """


class IntegerEncoding(Encoding):
    def __init__(
        self,
        bits: int,
        little_endian: bool = False,
        scheme: IntegerEncodingScheme = IntegerEncodingScheme.UNSIGNED,
    ) -> None:
        super().__init__(bits=bits)
        self.little_endian: bool = little_endian
        self.scheme: IntegerEncodingScheme = scheme


class FloatEncoding(Encoding):
    def __init__(
        self,
        bits: int,
        little_endian: bool = False,
        scheme: FloatEncodingScheme = FloatEncodingScheme.IEEE754_1985,
    ) -> None:
        super().__init__(bits=bits)
        self.little_endian: bool = little_endian
        self.scheme: FloatEncodingScheme = scheme


class FloatTimeEncoding(FloatEncoding):
    def __init__(
        self,
        bits: int,
        little_endian: bool = False,
        scheme: FloatEncodingScheme = FloatEncodingScheme.IEEE754_1985,
        offset: float = 0,
        scale: float = 1,
    ) -> None:
        super().__init__(
            bits=bits,
            little_endian=little_endian,
            scheme=scheme,
        )
        self.offset: float = offset
        self.scale: float = scale


class IntegerTimeEncoding(IntegerEncoding):
    def __init__(
        self,
        bits: int,
        little_endian: bool = False,
        scheme: IntegerEncodingScheme = IntegerEncodingScheme.UNSIGNED,
        offset: float = 0,
        scale: float = 1,
    ) -> None:
        super().__init__(
            bits=bits,
            little_endian=little_endian,
            scheme=scheme,
        )
        self.offset: float = offset
        self.scale: float = scale


TimeEncoding: TypeAlias = FloatTimeEncoding | IntegerTimeEncoding


class StringEncoding(Encoding):
    def __init__(
        self,
        bits: int | None = None,
        length_bits: int | None = None,
        max_bits: int | None = 8388608,
        charset: Charset = Charset.US_ASCII,
        termination: bytes = b"\0",
    ) -> None:
        super().__init__(bits=bits)

        self.length_bits: int | None = length_bits

        self.max_bits: int | None = max_bits
        """
        Maximum number of bits, in case of a dynamically sized string.

        This value hints Yamcs about the buffer size that is allocated to
        read the string, although Yamcs can choose to use a smaller buffer
        when it can.

        Default is 1 MB
        """

        self.charset: Charset = charset
        self.termination: bytes = termination


uint1_t = IntegerEncoding(bits=1, scheme=IntegerEncodingScheme.UNSIGNED)
"""Unsigned 1-bit integer"""

uint2_t = IntegerEncoding(bits=2, scheme=IntegerEncodingScheme.UNSIGNED)
"""Unsigned 2-bit integer"""

uint3_t = IntegerEncoding(bits=3, scheme=IntegerEncodingScheme.UNSIGNED)
"""Unsigned 3-bit integer"""

uint4_t = IntegerEncoding(bits=4, scheme=IntegerEncodingScheme.UNSIGNED)
"""Unsigned 4-bit integer"""

uint5_t = IntegerEncoding(bits=5, scheme=IntegerEncodingScheme.UNSIGNED)
"""Unsigned 5-bit integer"""

uint6_t = IntegerEncoding(bits=6, scheme=IntegerEncodingScheme.UNSIGNED)
"""Unsigned 6-bit integer"""

uint7_t = IntegerEncoding(bits=7, scheme=IntegerEncodingScheme.UNSIGNED)
"""Unsigned 7-bit integer"""

int8_t = IntegerEncoding(bits=8, scheme=IntegerEncodingScheme.TWOS_COMPLEMENT)
"""Signed 8-bit integer in two's complement notation (big endian)"""

uint8_t = IntegerEncoding(bits=8, scheme=IntegerEncodingScheme.UNSIGNED)
"""Unsigned 8-bit integer (big endian)"""

uint8_t = IntegerEncoding(bits=8, scheme=IntegerEncodingScheme.UNSIGNED)
"""Unsigned 8-bit integer"""

bool_t = uint8_t
"""Same as ``uint8_t``. 0=False, 1=True"""

uint9_t = IntegerEncoding(bits=9, scheme=IntegerEncodingScheme.UNSIGNED)
"""Unsigned 9-bit integer"""

uint10_t = IntegerEncoding(bits=10, scheme=IntegerEncodingScheme.UNSIGNED)
"""Unsigned 10-bit integer"""

uint11_t = IntegerEncoding(bits=11, scheme=IntegerEncodingScheme.UNSIGNED)
"""Unsigned 11-bit integer"""

uint12_t = IntegerEncoding(bits=12, scheme=IntegerEncodingScheme.UNSIGNED)
"""Unsigned 12-bit integer"""

uint13_t = IntegerEncoding(bits=13, scheme=IntegerEncodingScheme.UNSIGNED)
"""Unsigned 13-bit integer"""

uint14_t = IntegerEncoding(bits=14, scheme=IntegerEncodingScheme.UNSIGNED)
"""Unsigned 14-bit integer"""

uint15_t = IntegerEncoding(bits=15, scheme=IntegerEncodingScheme.UNSIGNED)
"""Unsigned 15-bit integer"""

int16_t = IntegerEncoding(bits=16, scheme=IntegerEncodingScheme.TWOS_COMPLEMENT)
"""Signed 16-bit integer in two's complement notation (big endian)"""

int16le_t = IntegerEncoding(
    bits=16,
    little_endian=True,
    scheme=IntegerEncodingScheme.TWOS_COMPLEMENT,
)
"""Signed 16-bit integer in two's complement notation (little endian)"""

uint16_t = IntegerEncoding(bits=16, scheme=IntegerEncodingScheme.UNSIGNED)
"""Unsigned 16-bit integer (big endian)"""

uint16le_t = IntegerEncoding(
    bits=16,
    little_endian=True,
    scheme=IntegerEncodingScheme.UNSIGNED,
)
"""Unsigned 16-bit integer (little endian)"""

int24_t = IntegerEncoding(bits=24, scheme=IntegerEncodingScheme.TWOS_COMPLEMENT)
"""Signed 24-bit integer in two's complement notation"""

uint24_t = IntegerEncoding(bits=24, scheme=IntegerEncodingScheme.UNSIGNED)
"""Unsigned 24-bit integer"""

int32_t = IntegerEncoding(bits=32, scheme=IntegerEncodingScheme.TWOS_COMPLEMENT)
"""Signed 32-bit integer in two's complement notation (big endian)"""

int32le_t = IntegerEncoding(
    bits=32,
    little_endian=True,
    scheme=IntegerEncodingScheme.TWOS_COMPLEMENT,
)
"""Signed 32-bit integer in two's complement notation (little endian)"""

uint32_t = IntegerEncoding(bits=32, scheme=IntegerEncodingScheme.UNSIGNED)
"""Unsigned 32-bit integer (big endian)"""

uint32le_t = IntegerEncoding(
    bits=32,
    little_endian=True,
    scheme=IntegerEncodingScheme.UNSIGNED,
)
"""Unsigned 32-bit integer (little endian)"""

float32_t = FloatEncoding(bits=32, scheme=FloatEncodingScheme.IEEE754_1985)
"""32-bit float in IEEE754-1985 encoding (big endian)"""

float32le_t = FloatEncoding(
    bits=32,
    little_endian=True,
    scheme=FloatEncodingScheme.IEEE754_1985,
)
"""32-bit float in IEEE754-1985 encoding (little endian)"""

float64_t = FloatEncoding(bits=64, scheme=FloatEncodingScheme.IEEE754_1985)
"""64-bit float in IEEE754-1985 encoding (big endian)"""

float64le_t = FloatEncoding(
    bits=64,
    little_endian=True,
    scheme=FloatEncodingScheme.IEEE754_1985,
)
"""64-bit float in IEEE754-1985 encoding (little endian)"""
