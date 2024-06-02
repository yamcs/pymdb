Encodings
=========

Charset
-------

.. autoclass:: yamcs.pymdb.Charset
   :members:
   :member-order: bysource


FloatEncodingScheme
-------------------

.. autoclass:: yamcs.pymdb.FloatEncodingScheme
   :members:
   :member-order: bysource


IntegerEncodingScheme
---------------------

.. autoclass:: yamcs.pymdb.IntegerEncodingScheme
   :members:
   :member-order: bysource


Encoding
--------

.. autoclass:: yamcs.pymdb.Encoding
   :members:


BinaryEncoding
--------------

.. autoclass:: yamcs.pymdb.BinaryEncoding
   :members:


IntegerEncoding
---------------

.. autoclass:: yamcs.pymdb.IntegerEncoding
   :members:


FloatEncoding
-------------

.. autoclass:: yamcs.pymdb.FloatEncoding
   :members:


FloatTimeEncoding
-----------------

.. autoclass:: yamcs.pymdb.FloatTimeEncoding
   :members:


IntegerTimeEncoding
-------------------

.. autoclass:: yamcs.pymdb.IntegerTimeEncoding
   :members:


StringEncoding
--------------

.. autoclass:: yamcs.pymdb.StringEncoding
   :members:


Common encodings
----------------

The ``encodings`` module contains reusable data encodings. These are optional to use as you can create entirely custom data encodings.


Unsigned integers
~~~~~~~~~~~~~~~~~

.. autoattribute:: yamcs.pymdb.uint1_t
    :annotation: unsigned 1-bit integer

.. autoattribute:: yamcs.pymdb.uint2_t
    :annotation: unsigned 2-bit integer

.. autoattribute:: yamcs.pymdb.uint3_t
    :annotation: unsigned 3-bit integer

.. autoattribute:: yamcs.pymdb.uint4_t
    :annotation: unsigned 4-bit integer

.. autoattribute:: yamcs.pymdb.uint5_t
    :annotation: unsigned 5-bit integer

.. autoattribute:: yamcs.pymdb.uint6_t
    :annotation: unsigned 6-bit integer

.. autoattribute:: yamcs.pymdb.uint7_t
    :annotation: unsigned 7-bit integer

.. autoattribute:: yamcs.pymdb.uint8_t
    :annotation: unsigned 8-bit integer

.. autoattribute:: yamcs.pymdb.uint9_t
    :annotation: unsigned 9-bit integer

.. autoattribute:: yamcs.pymdb.uint10_t
    :annotation: unsigned 10-bit integer

.. autoattribute:: yamcs.pymdb.uint11_t
    :annotation: unsigned 11-bit integer

.. autoattribute:: yamcs.pymdb.uint12_t
    :annotation: unsigned 12-bit integer

.. autoattribute:: yamcs.pymdb.uint13_t
    :annotation: unsigned 13-bit integer

.. autoattribute:: yamcs.pymdb.uint14_t
    :annotation: unsigned 14-bit integer

.. autoattribute:: yamcs.pymdb.uint15_t
    :annotation: unsigned 15-bit integer

.. autoattribute:: yamcs.pymdb.uint16_t
    :annotation: unsigned 16-bit integer

.. autoattribute:: yamcs.pymdb.uint24_t
    :annotation: unsigned 24-bit integer

.. autoattribute:: yamcs.pymdb.uint32_t
    :annotation: unsigned 32-bit integer


Signed integers
~~~~~~~~~~~~~~~

.. autoattribute:: yamcs.pymdb.int8_t
    :annotation: signed 8-bit integer (big endian)

.. autoattribute:: yamcs.pymdb.int16_t
    :annotation: signed 16-bit integer (big endian)

.. autoattribute:: yamcs.pymdb.int24_t
    :annotation: signed 24-bit integer (big endian)

.. autoattribute:: yamcs.pymdb.int32_t
    :annotation: signed 32-bit integer (big endian)


Boolean integer
~~~~~~~~~~~~~~~

.. autoattribute:: yamcs.pymdb.bool_t
    :annotation: Same as uint8_t. 0=False, 1=True


Floats
~~~~~~

.. autoattribute:: yamcs.pymdb.float32_t
    :annotation: 32-bit float in IEEE754-1985 encoding (big endian)

.. autoattribute:: yamcs.pymdb.float64_t
    :annotation: 64-bit float in IEEE754-1985 encoding (big endian)


Little endian variants
~~~~~~~~~~~~~~~~~~~~~~

.. autoattribute:: yamcs.pymdb.uint16le_t
    :annotation: unsigned 16-bit integer (little endian)

.. autoattribute:: yamcs.pymdb.int16le_t
    :annotation: signed 16-bit integer in two's complement notation (little endian)

.. autoattribute:: yamcs.pymdb.uint32le_t
    :annotation: unsigned 32-bit integer (little endian)

.. autoattribute:: yamcs.pymdb.int32le_t
    :annotation: signed 32-bit integer in two's complement notation (little endian)

.. autoattribute:: yamcs.pymdb.float32le_t
    :annotation: 32-bit float in IEEE754-1985 encoding (little endian)

.. autoattribute:: yamcs.pymdb.float64le_t
    :annotation: 64-bit float in IEEE754-1985 encoding (little endian)
