from enum import Enum, auto
from typing import TypeAlias

from yamcs.pymdb.algorithms import JavaAlgorithm


class ByteOrder(Enum):
    """
    Byte order (endianness)
    """

    BIG_ENDIAN = auto()
    """Big Endian (most significant byte first)"""

    LITTLE_ENDIAN = auto()
    """Little Endian (least significant byte first)"""


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


class FloatDataEncodingScheme(Enum):
    """Float encoding"""

    IEEE754_1985 = auto()
    """IEEE 754-1985"""

    MILSTD_1750A = auto()
    """MIL-STD-1750A"""


class IntegerDataEncodingScheme(Enum):
    """Integer encoding"""

    UNSIGNED = auto()
    """Unsigned"""

    SIGN_MAGNITUDE = auto()
    """Sign-magnitude"""

    TWOS_COMPLEMENT = auto()
    """Two's complement"""

    ONES_COMPLEMENT = auto()
    """Ones' complement"""


class DataEncoding:
    def __init__(self, bits: int | None = None) -> None:
        self.bits = bits


class BinaryDataEncoding(DataEncoding):
    def __init__(
        self,
        bits: int | None = None,
        length_bits: int | None = None,
        encoder: JavaAlgorithm | None = None,
        decoder: JavaAlgorithm | None = None,
    ) -> None:
        super().__init__(bits=bits)

        self.length_bits: int | None = length_bits
        """
        Length in bits of a leading size tag
        """

        self.encoder: JavaAlgorithm | None = encoder
        """
        Custom encoder, when this encoding is used for telecommanding
        """

        self.decoder: JavaAlgorithm | None = decoder
        """
        Custom decoder, when this encoding is used for telemetry
        """


class IntegerDataEncoding(DataEncoding):
    def __init__(
        self,
        bits: int,
        byte_order: ByteOrder = ByteOrder.BIG_ENDIAN,
        scheme: IntegerDataEncodingScheme = IntegerDataEncodingScheme.UNSIGNED,
    ) -> None:
        super().__init__(bits=bits)
        self.byte_order: ByteOrder = byte_order
        self.scheme: IntegerDataEncodingScheme = scheme


class FloatDataEncoding(DataEncoding):
    def __init__(
        self,
        bits: int,
        byte_order: ByteOrder = ByteOrder.BIG_ENDIAN,
        scheme: FloatDataEncodingScheme = FloatDataEncodingScheme.IEEE754_1985,
    ) -> None:
        super().__init__(bits=bits)
        self.byte_order: ByteOrder = byte_order
        self.scheme: FloatDataEncodingScheme = scheme


class FloatTimeEncoding(FloatDataEncoding):
    def __init__(
        self,
        bits: int,
        byte_order: ByteOrder = ByteOrder.BIG_ENDIAN,
        scheme: FloatDataEncodingScheme = FloatDataEncodingScheme.IEEE754_1985,
        offset: float = 0,
        scale: float = 1,
    ) -> None:
        super().__init__(
            bits=bits,
            byte_order=byte_order,
            scheme=scheme,
        )
        self.offset: float = offset
        self.scale: float = scale


class IntegerTimeEncoding(IntegerDataEncoding):
    def __init__(
        self,
        bits: int,
        byte_order: ByteOrder = ByteOrder.BIG_ENDIAN,
        scheme: IntegerDataEncodingScheme = IntegerDataEncodingScheme.UNSIGNED,
        offset: float = 0,
        scale: float = 1,
    ) -> None:
        super().__init__(
            bits=bits,
            byte_order=byte_order,
            scheme=scheme,
        )
        self.offset: float = offset
        self.scale: float = scale


TimeEncoding: TypeAlias = FloatTimeEncoding | IntegerTimeEncoding


class StringDataEncoding(DataEncoding):
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


uint1_t = IntegerDataEncoding(
    bits=1,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=IntegerDataEncodingScheme.UNSIGNED,
)
"""Unsigned 1-bit integer"""

uint2_t = IntegerDataEncoding(
    bits=2,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=IntegerDataEncodingScheme.UNSIGNED,
)
"""Unsigned 2-bit integer"""

uint3_t = IntegerDataEncoding(
    bits=3,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=IntegerDataEncodingScheme.UNSIGNED,
)
"""Unsigned 3-bit integer"""

uint4_t = IntegerDataEncoding(
    bits=4,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=IntegerDataEncodingScheme.UNSIGNED,
)
"""Unsigned 4-bit integer"""

uint5_t = IntegerDataEncoding(
    bits=5,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=IntegerDataEncodingScheme.UNSIGNED,
)
"""Unsigned 5-bit integer"""

uint6_t = IntegerDataEncoding(
    bits=6,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=IntegerDataEncodingScheme.UNSIGNED,
)
"""Unsigned 6-bit integer"""

uint7_t = IntegerDataEncoding(
    bits=7,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=IntegerDataEncodingScheme.UNSIGNED,
)
"""Unsigned 7-bit integer"""

int8_t = IntegerDataEncoding(
    bits=8,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=IntegerDataEncodingScheme.TWOS_COMPLEMENT,
)
"""Signed 8-bit integer in two's complement notation (big endian)"""

uint8_t = IntegerDataEncoding(
    bits=8,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=IntegerDataEncodingScheme.UNSIGNED,
)
"""Unsigned 8-bit integer (big endian)"""

uint8_t = IntegerDataEncoding(
    bits=8,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=IntegerDataEncodingScheme.UNSIGNED,
)
"""Unsigned 8-bit integer"""

bool_t = uint8_t
"""Same as ``uint8_t``. 0=False, 1=True"""

uint9_t = IntegerDataEncoding(
    bits=9,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=IntegerDataEncodingScheme.UNSIGNED,
)
"""Unsigned 9-bit integer"""

uint10_t = IntegerDataEncoding(
    bits=10,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=IntegerDataEncodingScheme.UNSIGNED,
)
"""Unsigned 10-bit integer"""

uint11_t = IntegerDataEncoding(
    bits=11,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=IntegerDataEncodingScheme.UNSIGNED,
)
"""Unsigned 11-bit integer"""

uint12_t = IntegerDataEncoding(
    bits=12,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=IntegerDataEncodingScheme.UNSIGNED,
)
"""Unsigned 12-bit integer"""

uint13_t = IntegerDataEncoding(
    bits=13,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=IntegerDataEncodingScheme.UNSIGNED,
)
"""Unsigned 13-bit integer"""

uint14_t = IntegerDataEncoding(
    bits=14,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=IntegerDataEncodingScheme.UNSIGNED,
)
"""Unsigned 14-bit integer"""

uint15_t = IntegerDataEncoding(
    bits=15,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=IntegerDataEncodingScheme.UNSIGNED,
)
"""Unsigned 15-bit integer"""

int16_t = IntegerDataEncoding(
    bits=16,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=IntegerDataEncodingScheme.TWOS_COMPLEMENT,
)
"""Signed 16-bit integer in two's complement notation (big endian)"""

int16le_t = IntegerDataEncoding(
    bits=16,
    byte_order=ByteOrder.LITTLE_ENDIAN,
    scheme=IntegerDataEncodingScheme.TWOS_COMPLEMENT,
)
"""Signed 16-bit integer in two's complement notation (little endian)"""

uint16_t = IntegerDataEncoding(
    bits=16,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=IntegerDataEncodingScheme.UNSIGNED,
)
"""Unsigned 16-bit integer (big endian)"""

uint16le_t = IntegerDataEncoding(
    bits=16,
    byte_order=ByteOrder.LITTLE_ENDIAN,
    scheme=IntegerDataEncodingScheme.UNSIGNED,
)
"""Unsigned 16-bit integer (little endian)"""

int32_t = IntegerDataEncoding(
    bits=32,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=IntegerDataEncodingScheme.TWOS_COMPLEMENT,
)
"""Signed 32-bit integer in two's complement notation (big endian)"""

int32le_t = IntegerDataEncoding(
    bits=32,
    byte_order=ByteOrder.LITTLE_ENDIAN,
    scheme=IntegerDataEncodingScheme.TWOS_COMPLEMENT,
)
"""Signed 32-bit integer in two's complement notation (little endian)"""

uint32_t = IntegerDataEncoding(
    bits=32,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=IntegerDataEncodingScheme.UNSIGNED,
)
"""Unsigned 32-bit integer (big endian)"""

uint32le_t = IntegerDataEncoding(
    bits=32,
    byte_order=ByteOrder.LITTLE_ENDIAN,
    scheme=IntegerDataEncodingScheme.UNSIGNED,
)
"""Unsigned 32-bit integer (little endian)"""

float32_t = FloatDataEncoding(
    bits=32,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=FloatDataEncodingScheme.IEEE754_1985,
)
"""32-bit float in IEEE754-1985 encoding (big endian)"""

float32le_t = FloatDataEncoding(
    bits=32,
    byte_order=ByteOrder.LITTLE_ENDIAN,
    scheme=FloatDataEncodingScheme.IEEE754_1985,
)
"""32-bit float in IEEE754-1985 encoding (little endian)"""

float64_t = FloatDataEncoding(
    bits=64,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=FloatDataEncodingScheme.IEEE754_1985,
)
"""64-bit float in IEEE754-1985 encoding (big endian)"""

float64le_t = FloatDataEncoding(
    bits=64,
    byte_order=ByteOrder.LITTLE_ENDIAN,
    scheme=FloatDataEncodingScheme.IEEE754_1985,
)
"""64-bit float in IEEE754-1985 encoding (little endian)"""
