======
Alarms
======

.. index:: Alarm
.. index:: AlarmLevel

An alarm definition tells Yamcs when a parameter value is a reason for
concern, and how concerned to be. Yamcs evaluates alarms as values arrive
and surfaces them to operators for acknowledgment.

Alarm severity uses six levels, in increasing order of concern:

.. list-table::
   :widths: 25 75

   * - ``NORMAL``
     - No concern.
   * - ``WATCH``
     - Least concern, below the commonly used WARNING.
   * - ``WARNING``
     - The usual minimum concern level.
   * - ``DISTRESS``
     - Between WARNING and CRITICAL.
   * - ``CRITICAL``
     - The usual maximum concern level.
   * - ``SEVERE``
     - Highest concern, above CRITICAL.

These are the values of the ``AlarmLevel`` enum. Most missions use only
WARNING and CRITICAL.


Threshold alarms
================

.. index:: ThresholdAlarm

For numeric parameters (``IntegerParameter``, ``FloatParameter``),
``ThresholdAlarm`` defines low and/or high limits per severity level. Each
limit is optional; each has an ``*_exclusive`` companion to exclude the
boundary value itself.

.. code-block:: python

   battery_voltage = Y.FloatParameter(
       system=eps,
       name="battery_voltage",
       units="V",
       encoding=Y.uint12_t,
       calibrator=Y.Polynomial([0, 0.00805]),
       alarm=Y.ThresholdAlarm(
           watch_low=11.5,
           warning_low=11.0,
           critical_low=10.2,
           warning_high=14.4,
           critical_high=15.0,
       ),
   )

Available limits: ``watch_low``, ``warning_low``, ``distress_low``,
``critical_low``, ``severe_low`` and the corresponding ``*_high`` options.
Thresholds compare against the calibrated engineering value.

``minimum_violations`` (default 1) requires the limit to be violated that
many successive times before the alarm triggers, filtering out one-sample
glitches.


Enumeration alarms
==================

.. index:: EnumerationAlarm

For ``EnumeratedParameter``, ``EnumerationAlarm`` assigns an alarm level per
state, keyed by enumeration label. States not listed get the
``default_level`` (``NORMAL`` unless overridden):

.. code-block:: python

   mode = Y.EnumeratedParameter(
       system=obc,
       name="mode",
       choices=[(0, "OFF"), (1, "SAFE"), (2, "NOMINAL")],
       encoding=Y.uint8_t,
       alarm=Y.EnumerationAlarm(
           states={"SAFE": Y.AlarmLevel.WARNING},
       ),
   )

Setting ``default_level`` to a non-normal value inverts the logic: every
state alarms unless explicitly declared safe.


Context alarms
==============

.. index:: context alarm
.. index:: ThresholdContextAlarm
.. index:: EnumerationContextAlarm

Alarm limits often depend on the situation: a battery current that is
nominal during transmission would be alarming in idle mode. *Context
alarms* attach an alternative alarm specification that applies while a
condition — an :doc:`expression <expressions>` over other parameters —
holds:

.. code-block:: python

   current = Y.FloatParameter(
       system=eps,
       name="bus_current",
       units="A",
       encoding=Y.uint12_t,
       alarm=Y.ThresholdAlarm(warning_high=1.0),
       context_alarms=[
           Y.ThresholdContextAlarm(
               context=Y.eq(mode, "TRANSMIT"),
               alarm=Y.ThresholdAlarm(warning_high=3.5),
           ),
       ],
   )

While the context matches, the context alarm's specification replaces the
default one. ``EnumerationContextAlarm`` is the equivalent for enumerated
parameters. Multiple context alarms may be given; the plain ``alarm``
serves as the fallback when no context matches.
