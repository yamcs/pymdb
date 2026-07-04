===========
Expressions
===========

.. index:: expressions
.. index:: Expression

Several features need a condition over telemetry or argument values:
container identification, conditional entries, context alarms, verifier
checks and transmission constraints all take an *expression*. Expressions
are built with six comparison helpers and two combinators:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Helper
     - Meaning
   * - ``eq(ref, value)``
     - equal to
   * - ``ne(ref, value)``
     - not equal to
   * - ``lt(ref, value)`` / ``lte(ref, value)``
     - less than (or equal)
   * - ``gt(ref, value)`` / ``gte(ref, value)``
     - greater than (or equal)
   * - ``all_of(expr1, expr2, ...)``
     - true when all sub-expressions hold (AND)
   * - ``any_of(expr1, expr2, ...)``
     - true when at least one holds (OR)

.. code-block:: python

   Y.all_of(
       Y.eq(mode, "NOMINAL"),
       Y.any_of(
           Y.gt(battery_voltage, 11.0),
           Y.eq(external_power, True),
       ),
   )

Combinators nest to any depth. Each helper is also available as a class
(``EqExpression``, ``AndExpression``, ...) with identical meaning; the
functions are simply shorter.


What can be referenced
======================

.. index:: ParameterMember
.. index:: ArgumentMember

The first operand, ``ref``, accepts:

* a ``Parameter`` — the usual case;
* an ``Argument`` — inside command definitions, to make entries or
  constraints depend on another argument of the same command;
* a ``ParameterMember`` or ``ArgumentMember`` — a member inside an
  aggregate, built from the parameter/argument and the member object(s)
  forming the path (see :doc:`parameters`);
* a plain string — the qualified name of a parameter not managed with
  PyMDB.

.. code-block:: python

   # Compare against a member of an aggregate parameter
   apid = Y.ParameterMember(ccsds_packet_id, path=apid_member)
   my_packet = Y.Container(
       system=spacecraft,
       name="my_packet",
       base=ccsds_space_packet,
       condition=Y.eq(apid, 101),
   )

The comparison ``value`` is a plain Python value matching the engineering
type: a number, a string (for enumeration states), a boolean.


Calibrated or raw
=================

By default comparisons use the calibrated (engineering) value. Pass
``calibrated=False`` to compare against the raw value instead:

.. code-block:: python

   Y.eq(status_field, 0x2A, calibrated=False)

This matters chiefly in container conditions on parameters that have a
calibrator or enumeration: comparing raw values spares Yamcs the
calibration during packet identification, and lets you match wire-level
constants directly.
