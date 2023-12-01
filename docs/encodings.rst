Encodings
=========

The ``encodings`` module contains reusable data encodings. These are optional to use as you can create entirely custom data encodings.


Unsigned integers
-----------------

.. autoattribute:: yamcs.pymdb.encodings.uint1_t
    :annotation: unsigned 1-bit integer

.. autoattribute:: yamcs.pymdb.encodings.uint2_t
    :annotation: unsigned 2-bit integer

.. autoattribute:: yamcs.pymdb.encodings.uint3_t
    :annotation: unsigned 3-bit integer

.. autoattribute:: yamcs.pymdb.encodings.uint4_t
    :annotation: unsigned 4-bit integer

.. autoattribute:: yamcs.pymdb.encodings.uint5_t
    :annotation: unsigned 5-bit integer

.. autoattribute:: yamcs.pymdb.encodings.uint6_t
    :annotation: unsigned 6-bit integer

.. autoattribute:: yamcs.pymdb.encodings.uint7_t
    :annotation: unsigned 7-bit integer

.. autoattribute:: yamcs.pymdb.encodings.uint8_t
    :annotation: unsigned 8-bit integer

.. autoattribute:: yamcs.pymdb.encodings.uint9_t
    :annotation: unsigned 9-bit integer

.. autoattribute:: yamcs.pymdb.encodings.uint10_t
    :annotation: unsigned 10-bit integer

.. autoattribute:: yamcs.pymdb.encodings.uint11_t
    :annotation: unsigned 11-bit integer

.. autoattribute:: yamcs.pymdb.encodings.uint12_t
    :annotation: unsigned 12-bit integer

.. autoattribute:: yamcs.pymdb.encodings.uint13_t
    :annotation: unsigned 13-bit integer

.. autoattribute:: yamcs.pymdb.encodings.uint14_t
    :annotation: unsigned 14-bit integer

.. autoattribute:: yamcs.pymdb.encodings.uint15_t
    :annotation: unsigned 15-bit integer

.. autoattribute:: yamcs.pymdb.encodings.uint16_t
    :annotation: unsigned 16-bit integer

.. autoattribute:: yamcs.pymdb.encodings.uint32_t
    :annotation: unsigned 32-bit integer


Signed integers
---------------

.. autoattribute:: yamcs.pymdb.encodings.int8_t
    :annotation: signed 8-bit integer (big endian)

.. autoattribute:: yamcs.pymdb.encodings.int16_t
    :annotation: signed 16-bit integer (big endian)

.. autoattribute:: yamcs.pymdb.encodings.int32_t
    :annotation: signed 32-bit integer (big endian)


Boolean integer
---------------

.. autoattribute:: yamcs.pymdb.encodings.bool_t
    :annotation: Same as uint8_t. 0=False, 1=True

Floats
------

.. autoattribute:: yamcs.pymdb.encodings.float32_t
    :annotation: 32-bit float in IEEE754-1985 encoding (big endian)

.. autoattribute:: yamcs.pymdb.encodings.float64_t
    :annotation: 64-bit float in IEEE754-1985 encoding (big endian)


Little endian variants
----------------------

.. autoattribute:: yamcs.pymdb.encodings.uint8le_t
    :annotation: unsigned 8-bit integer (little endian)

.. autoattribute:: yamcs.pymdb.encodings.int8le_t
    :annotation: signed 8-bit integer in two's complement notation (little endian)

.. autoattribute:: yamcs.pymdb.encodings.uint16le_t
    :annotation: unsigned 16-bit integer (little endian)

.. autoattribute:: yamcs.pymdb.encodings.int16le_t
    :annotation: signed 16-bit integer in two's complement notation (little endian)

.. autoattribute:: yamcs.pymdb.encodings.uint32le_t
    :annotation: unsigned 32-bit integer (little endian)

.. autoattribute:: yamcs.pymdb.encodings.int32le_t
    :annotation: signed 32-bit integer in two's complement notation (little endian)

.. autoattribute:: yamcs.pymdb.encodings.float32le_t
    :annotation: 32-bit float in IEEE754-1985 encoding (little endian)

.. autoattribute:: yamcs.pymdb.encodings.float64le_t
    :annotation: 64-bit float in IEEE754-1985 encoding (little endian)
