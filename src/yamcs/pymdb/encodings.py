import dataclasses

from yamcs.pymdb.model import (
    ByteOrder,
    FloatDataEncoding,
    FloatDataEncodingScheme,
    IntegerDataEncoding,
    IntegerDataEncodingScheme,
)

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
