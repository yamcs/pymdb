============
Name Summary
============

All public names of the ``yamcs.pymdb`` package, grouped by the chapter
that describes them. Everything is importable directly from
``yamcs.pymdb``, except where a submodule is noted.


Systems — :doc:`../systems`
===========================

``System``
    Top-level system, root of a model tree.

``Subsystem``
    A system nested inside another system.


Parameters — :doc:`../parameters`
=================================

``Parameter``
    Base class of all parameter kinds.

``IntegerParameter``, ``FloatParameter``, ``EnumeratedParameter``, ``BooleanParameter``, ``StringParameter``, ``BinaryParameter``, ``AbsoluteTimeParameter``, ``AggregateParameter``, ``ArrayParameter``
    The nine parameter kinds, by engineering type.

``DataSource``
    Enum: where a parameter's values come from (``TELEMETERED``,
    ``DERIVED``, ``CONSTANT``, ``LOCAL``, ``GROUND``).

``Epoch``
    Enum of standard time epochs (``GPS``, ``J2000``, ``TAI``, ``UNIX``)
    for absolute-time types.

``Choices``
    Type alias for enumeration states: a sequence of tuples, or a Python
    ``Enum`` class.

``Member``
    Base class for aggregate members.

``IntegerMember``, ``FloatMember``, ``EnumeratedMember``, ``BooleanMember``, ``StringMember``, ``BinaryMember``, ``AbsoluteTimeMember``, ``AggregateMember``, ``ArrayMember``
    Member variants of each data kind, for use inside aggregates and
    arrays.

``ParameterValue``
    Reference to a parameter's value, e.g. as a dynamic array length.

``ArgumentValue``
    Reference to an argument's value, e.g. as a dynamic array length in
    commands.

``DynamicInteger``
    Deprecated alias; use ``ParameterValue`` or ``ArgumentValue``.

``DataType``, ``IntegerDataType``, ``FloatDataType``, ``EnumeratedDataType``, ``BooleanDataType``, ``StringDataType``, ``BinaryDataType``, ``AbsoluteTimeDataType``, ``AggregateDataType``, ``ArrayDataType``
    Shared data-kind base classes. Rarely constructed directly, but useful
    with ``isinstance`` when post-processing a model.


Encodings — :doc:`../encodings`
===============================

``Encoding``
    Base class of all encodings.

``IntegerEncoding``, ``FloatEncoding``, ``StringEncoding``, ``BinaryEncoding``
    Raw representations for the respective value kinds.

``IntegerTimeEncoding``, ``FloatTimeEncoding``, ``TimeEncoding``
    Encodings for absolute times, adding ``offset``/``scale``
    (``TimeEncoding`` is the union of the two).

``IntegerEncodingScheme``, ``FloatEncodingScheme``
    Enums selecting the binary scheme (two's complement, IEEE 754, ...).

``Charset``
    Enum of character sets for string encodings.

``uint1_t`` ... ``uint32_t``, ``int8_t`` ... ``int32_t``, ``uint16le_t``, ``uint32le_t``, ``int16le_t``, ``int32le_t``, ``float32_t``, ``float64_t``, ``float32le_t``, ``float64le_t``, ``bool_t``
    Predefined encoding constants for common cases.


Containers — :doc:`../containers`
=================================

``Container``
    A telemetry packet (or reusable packet fragment).

``ParameterEntry``
    Places a parameter in a container (also usable in commands).

``ContainerEntry``
    Embeds a container inside another container.


Calibrators — :doc:`../calibrators`
===================================

``Calibrator``
    Base class for raw-to-engineering conversions.

``Polynomial``
    Calibration by polynomial coefficients.

``Interpolate``
    Calibration by piecewise linear interpolation.


Alarms — :doc:`../alarms`
=========================

``Alarm``
    Base class for alarm definitions.

``AlarmLevel``
    Enum of severity levels (``WATCH`` ... ``SEVERE``).

``ThresholdAlarm``
    Numeric limit alarms per severity level.

``EnumerationAlarm``
    Alarm levels per enumeration state.

``ThresholdContextAlarm``, ``EnumerationContextAlarm``
    Alternative alarm specifications that apply while a context
    expression holds.


Commands — :doc:`../commands`
=============================

``Command``
    A telecommand definition.

``CommandLevel``
    Enum of command significance (``NORMAL``, ``VITAL``, ``CRITICAL``,
    ``FORBIDDEN``).

``Argument``
    Base class of all argument kinds.

``IntegerArgument``, ``FloatArgument``, ``EnumeratedArgument``, ``BooleanArgument``, ``StringArgument``, ``BinaryArgument``, ``AbsoluteTimeArgument``, ``AggregateArgument``, ``ArrayArgument``
    The nine argument kinds, by engineering type.

``ArgumentEntry``
    Places an argument in the encoded command.

``FixedValueEntry``
    Places a constant in the encoded command.

``CommandEntry``
    Type alias: ``ArgumentEntry``, ``ParameterEntry`` or
    ``FixedValueEntry``.

``TransmissionConstraint``
    Telemetry condition that must hold before a command is released.


Command verification — :doc:`../verifiers`
==========================================

``Verifier``
    Base class of all verifiers.

``TransferredToRangeVerifier``, ``SentFromRangeVerifier``, ``ReceivedVerifier``, ``AcceptedVerifier``, ``QueuedVerifier``, ``ExecutionVerifier``, ``CompleteVerifier``, ``FailedVerifier``
    Verifiers per command lifecycle stage.

``AlgorithmCheck``, ``ContainerCheck``, ``ExpressionCheck``, ``Check``
    The checks a verifier can perform (``Check`` is the union).

``TerminationAction``
    Enum: effect of a verifier outcome on the whole command (``SUCCESS``,
    ``FAIL``).


Algorithms — :doc:`../algorithms`
=================================

``Algorithm``
    A named algorithm attached to a system.

``InputParameter``, ``OutputParameter``
    Bindings between parameters and algorithm variables.

``Trigger``, ``ParameterTrigger``, ``ContainerTrigger``
    When an algorithm runs.

``UnnamedAlgorithm``, ``UnnamedJavaAlgorithm``, ``UnnamedJavaScriptAlgorithm``
    Inline algorithms for encoders, decoders and verifier checks.

``hex_string_decoder``, ``remaining_binary_decoder``, ``reverse_binary_decoder``, ``reverse_binary_encoder``
    Ready-made decoders/encoders shipping with Yamcs.

``AncillaryData``, ``AncillaryDataItem``
    Richer form of the ``extra`` option of inline algorithms, supporting
    URLs and MIME types per item.


Expressions — :doc:`../expressions`
===================================

``eq``, ``ne``, ``lt``, ``lte``, ``gt``, ``gte``
    Comparison helpers.

``all_of``, ``any_of``
    AND / OR combinators.

``Expression``, ``EqExpression``, ``NeExpression``, ``LtExpression``, ``LteExpression``, ``GtExpression``, ``GteExpression``, ``AndExpression``, ``OrExpression``
    Class forms of the helpers above.

``ParameterMember``, ``ArgumentMember``
    References to a member inside an aggregate parameter or argument.


Packet headers — :doc:`../headers`
==================================

``ccsds.add_ccsds_header``, ``ccsds.CcsdsHeader``
    CCSDS Space Packet primary header (module ``yamcs.pymdb.ccsds``).

``csp.add_csp_header``, ``csp.CspHeader``
    CubeSat Space Protocol header (module ``yamcs.pymdb.csp``).


Generating and validating — :doc:`../generating`
================================================

``System.dump``, ``System.dumps``
    Export a system tree as XTCE.

``checks.check_complete_verifiers``, ``checks.check_float_encoding``, ``checks.check_little_endian_only``
    Model sanity checks (module ``yamcs.pymdb.checks``).

``ExportError``, ``DuplicateNameError``, ``SizeCalculationError``
    Exceptions raised by the library.
