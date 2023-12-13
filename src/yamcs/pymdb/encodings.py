import dataclasses
from dataclasses import dataclass
from enum import Enum, auto
from typing import TypeAlias

from yamcs.pymdb.algorithms import JavaAlgorithm


class ByteOrder(Enum):
    BIG_ENDIAN = auto()
    LITTLE_ENDIAN = auto()


class Charset(Enum):
    US_ASCII = auto()
    ISO_8859_1 = auto()
    WINDOWS_1252 = auto()
    UTF_8 = auto()
    UTF_16 = auto()
    UTF_16LE = auto()
    UTF_16BE = auto()
    UTF_32 = auto()
    UTF_32LE = auto()
    UTF_32BE = auto()


class FloatDataEncodingScheme(Enum):
    IEEE754_1985 = auto()
    MILSTD_1750A = auto()


class IntegerDataEncodingScheme(Enum):
    UNSIGNED = auto()
    SIGN_MAGNITUDE = auto()
    TWOS_COMPLEMENT = auto()
    ONES_COMPLEMENT = auto()


@dataclass(kw_only=True)
class DataEncoding:
    bits: int
    byte_order: ByteOrder = ByteOrder.BIG_ENDIAN


@dataclass(kw_only=True)
class BinaryDataEncoding(DataEncoding):
    bits: int | None = None
    length_bits: int | None = None
    deserializer: JavaAlgorithm | None = None


@dataclass(kw_only=True)
class IntegerDataEncoding(DataEncoding):
    scheme: IntegerDataEncodingScheme = IntegerDataEncodingScheme.UNSIGNED


@dataclass(kw_only=True)
class FloatDataEncoding(DataEncoding):
    scheme: FloatDataEncodingScheme = FloatDataEncodingScheme.IEEE754_1985


@dataclass(kw_only=True)
class FloatTimeEncoding(FloatDataEncoding):
    offset: int = 0
    scale: int = 1


@dataclass(kw_only=True)
class IntegerTimeEncoding(IntegerDataEncoding):
    offset: int = 0
    scale: int = 1


TimeEncoding: TypeAlias = FloatTimeEncoding | IntegerTimeEncoding


@dataclass(kw_only=True)
class StringDataEncoding(DataEncoding):
    bits: int | None = None
    length_bits: int | None = None

    max_bits: int | None = 8388608
    """
    Maximum number of bits, in case of a dynamically sized string.

    This value hints Yamcs about the buffer size that is allocated to
    read the string, although Yamcs can choose to use a smaller buffer
    when it can.

    Default is 1 MB
    """

    charset: Charset = Charset.US_ASCII
    termination: bytes = b"\0"


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

int8le_t = dataclasses.replace(int8_t, byte_order=ByteOrder.LITTLE_ENDIAN)
"""Signed 8-bit integer in two's complement notation (little endian)"""

uint8_t = IntegerDataEncoding(
    bits=8,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=IntegerDataEncodingScheme.UNSIGNED,
)
"""Unsigned 8-bit integer (big endian)"""

uint8le_t = dataclasses.replace(uint8_t, byte_order=ByteOrder.LITTLE_ENDIAN)
"""Unsigned 8-bit integer (little endian)"""

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

int16le_t = dataclasses.replace(int16_t, byte_order=ByteOrder.LITTLE_ENDIAN)
"""Signed 16-bit integer in two's complement notation (little endian)"""

uint16_t = IntegerDataEncoding(
    bits=16,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=IntegerDataEncodingScheme.UNSIGNED,
)
"""Unsigned 16-bit integer (big endian)"""

uint16le_t = dataclasses.replace(uint16_t, byte_order=ByteOrder.LITTLE_ENDIAN)
"""Unsigned 16-bit integer (little endian)"""

int32_t = IntegerDataEncoding(
    bits=32,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=IntegerDataEncodingScheme.TWOS_COMPLEMENT,
)
"""Signed 32-bit integer in two's complement notation (big endian)"""

int32le_t = dataclasses.replace(int32_t, byte_order=ByteOrder.LITTLE_ENDIAN)
"""Signed 32-bit integer in two's complement notation (little endian)"""

uint32_t = IntegerDataEncoding(
    bits=32,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=IntegerDataEncodingScheme.UNSIGNED,
)
"""Unsigned 32-bit integer (big endian)"""

uint32le_t = dataclasses.replace(uint32_t, byte_order=ByteOrder.LITTLE_ENDIAN)
"""Unsigned 32-bit integer (little endian)"""

float32_t = FloatDataEncoding(
    bits=32,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=FloatDataEncodingScheme.IEEE754_1985,
)
"""32-bit float in IEEE754-1985 encoding (big endian)"""

float32le_t = dataclasses.replace(float32_t, byte_order=ByteOrder.LITTLE_ENDIAN)
"""32-bit float in IEEE754-1985 encoding (little endian)"""

float64_t = FloatDataEncoding(
    bits=64,
    byte_order=ByteOrder.BIG_ENDIAN,
    scheme=FloatDataEncodingScheme.IEEE754_1985,
)
"""64-bit float in IEEE754-1985 encoding (big endian)"""

float64le_t = dataclasses.replace(float64_t, byte_order=ByteOrder.LITTLE_ENDIAN)
"""64-bit float in IEEE754-1985 encoding (little endian)"""
