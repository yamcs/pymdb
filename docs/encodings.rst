=========
Encodings
=========

.. index:: Encoding

An encoding describes how a value is laid out in binary when it travels to
or from the remote system: how many bits, signed or unsigned, byte order,
character set, terminators. Encodings are independent of the engineering
type: the same ``uint8_t`` encoding can back an ``IntegerParameter``, an
``EnumeratedParameter`` or a ``BooleanParameter``.

An encoding is attached to a parameter, argument or member through its
``encoding`` option. The same encoding object can be reused freely — it
carries no reference to the things that use it.


Predefined encodings
====================

The most common cases are available as module-level constants, and most
models rarely need anything else:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Constant
     - Meaning
   * - ``uint1_t`` ... ``uint7_t``
     - Unsigned integers of 1 to 7 bits, for bitfields
   * - ``uint8_t``, ``uint16_t``, ``uint24_t``, ``uint32_t``
     - Unsigned big-endian integers
   * - ``int8_t``, ``int16_t``, ``int24_t``, ``int32_t``
     - Signed (two's complement) big-endian integers
   * - ``uint9_t`` ... ``uint15_t``
     - Unsigned integers of 9 to 15 bits
   * - ``uint16le_t``, ``uint32le_t``, ``int16le_t``, ``int32le_t``
     - Little-endian variants
   * - ``float32_t``, ``float64_t``
     - IEEE 754 floats, big endian
   * - ``float32le_t``, ``float64le_t``
     - IEEE 754 floats, little endian
   * - ``bool_t``
     - Alias of ``uint8_t`` (0=False, 1=True)

.. code-block:: python

   Y.IntegerParameter(eps, "counter", signed=False, encoding=Y.uint16_t)


Integer encodings
=================

.. index:: IntegerEncoding
.. index:: IntegerEncodingScheme

For anything not covered by the constants, construct an
``IntegerEncoding``:

.. code-block:: python

   Y.IntegerEncoding(
       bits=20,
       little_endian=False,
       scheme=Y.IntegerEncodingScheme.TWOS_COMPLEMENT,
   )

``scheme`` selects the binary representation: ``UNSIGNED``,
``TWOS_COMPLEMENT``, ``SIGN_MAGNITUDE``, ``ONES_COMPLEMENT``, or ``STRING``
for integers transmitted as text (see the warning below).


Float encodings
===============

.. index:: FloatEncoding
.. index:: FloatEncodingScheme

``FloatEncoding`` takes ``bits``, ``little_endian`` and a ``scheme``:
``IEEE754_1985`` (the default), ``MILSTD_1750A``, or ``STRING``.

.. warning::

   The ``STRING`` schemes of ``IntegerEncoding`` and ``FloatEncoding``
   describe numbers transmitted as text (requiring the ``string_encoding``
   option to spell out the text format). They are understood by Yamcs but
   are not part of the XTCE standard, so the exported file will not
   validate against the XTCE schema. The standard-compliant alternative —
   a plain ``StringEncoding`` on a numeric parameter — does not support
   calibrators.


String encodings
================

.. index:: StringEncoding
.. index:: Charset

``StringEncoding`` covers text values. The size of a string on the wire is
determined by whichever of these options is used:

``bits``
    A fixed size box. The string always occupies exactly this many bits;
    within the box it may still end early at a terminator.

``length_bits``
    The string is preceded by a size tag of this many bits, holding the
    string's byte length.

``termination``
    The string ends at this terminator byte (default ``b"\0"``). Set to
    ``None`` when the size is established by other means.

``max_bits``
    For dynamically sized strings, a hint for the buffer Yamcs allocates
    (default 1 MB).

``charset`` selects the character set: ``Charset.US_ASCII`` (default),
``ISO_8859_1``, ``WINDOWS_1252``, ``UTF_8``, ``UTF_16`` (plus LE/BE
variants) or ``UTF_32`` (plus LE/BE variants).

.. code-block:: python

   # A semicolon-terminated ASCII string
   Y.StringParameter(
       system=gt,
       name="status_text",
       encoding=Y.StringEncoding(termination=b"\x3B"),
   )

   # A length-prefixed UTF-8 string: 16-bit length tag, then the bytes
   Y.StringEncoding(length_bits=16, charset=Y.Charset.UTF_8, termination=None)


Binary encodings
================

.. index:: BinaryEncoding

``BinaryEncoding`` covers raw byte blocks. ``bits`` gives a fixed size;
``length_bits`` a leading size tag, as for strings. For anything more
exotic, binary encodings support custom *decoders* (telemetry direction)
and *encoders* (commanding direction), written as small algorithms:

.. code-block:: python

   Y.BinaryEncoding(decoder=Y.remaining_binary_decoder)

Several ready-made algorithms ship with the library, referring to decoder
and encoder implementations built into Yamcs:

.. list-table::
   :widths: 40 60

   * - ``remaining_binary_decoder``
     - Consumes all remaining bytes of the packet — useful for a trailing
       blob without a length indication.
   * - ``reverse_binary_decoder`` / ``reverse_binary_encoder``
     - Reverse the byte order.
   * - ``hex_string_decoder``
     - Reads fixed-size bytes and yields their hex representation as a
       string value.

You can also point to your own Java class with ``UnnamedJavaAlgorithm``,
or provide inline script code — see :doc:`algorithms`.


Time encodings
==============

.. index:: IntegerTimeEncoding
.. index:: FloatTimeEncoding

``AbsoluteTimeParameter`` uses one of the two time encodings:
``IntegerTimeEncoding`` or ``FloatTimeEncoding``. They extend the integer
and float encodings with ``offset`` and ``scale``, converting the raw count
into seconds since the parameter's reference epoch::

   time in seconds = offset + scale * raw

.. code-block:: python

   # 32-bit unsigned count of milliseconds since the mission epoch
   Y.AbsoluteTimeParameter(
       system=obc,
       name="obt",
       reference=datetime(2010, 1, 1, tzinfo=timezone.utc),
       encoding=Y.IntegerTimeEncoding(bits=32, scale=0.001),
   )
