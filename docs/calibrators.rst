===========
Calibrators
===========

.. index:: Calibrator

Sensors often transmit counts rather than engineering units directly. A
calibrator converts the raw value extracted from the packet into the
engineering value users see. Calibrators attach to integer and float
parameters (and to the corresponding members and command arguments) through
the ``calibrator`` option — many parameters need no calibrator at all, for
instance when the raw count already is the engineering value.

Two calibrator types are available.


Polynomial calibration
======================

.. index:: Polynomial

``Polynomial`` describes the transfer curve as polynomial coefficients,
ordered from x\ :sup:`0` upward — ``Polynomial([c0, c1, c2])`` means
``eng = c0 + c1·raw + c2·raw²``:

.. code-block:: python

   voltage = Y.FloatParameter(
       system=eps,
       name="bus_voltage",
       units="V",
       encoding=Y.uint12_t,
       calibrator=Y.Polynomial([0.0, 0.00805]),   # eng = 0.00805 * raw
   )

A linear scale-and-offset is simply a two-coefficient polynomial.


Piecewise interpolation
=======================

.. index:: Interpolate

``Interpolate`` describes the curve as a set of points; values in between
are interpolated linearly. ``xp`` holds the raw coordinates (increasing),
``fp`` the corresponding engineering values:

.. code-block:: python

   temperature = Y.FloatParameter(
       system=eps,
       name="battery_temp",
       units="degC",
       encoding=Y.uint8_t,
       calibrator=Y.Interpolate(
           xp=[0, 64, 128, 192, 255],
           fp=[-50.0, -10.0, 20.0, 45.0, 60.0],
       ),
   )

This suits thermistors and other sensors with non-linear response, where
the calibration comes from a lookup table.


Computing calibrators
=====================

Since the model is a Python program, calibration data does not have to be
transcribed by hand. At its simplest, writing coefficients as arithmetic
keeps the derivation visible in the source:

.. code-block:: python

   # 10-bit ADC, 3.3 V reference, 20 mV/unit sensor
   calibrator=Y.Polynomial([0, 3.3 / 1023 * 0.02])

And when the transfer function of the sensor circuit is known, the
calibrator can be *derived* at build time — sample the function over the
raw range and either feed the points straight into ``Interpolate``, or fit
a polynomial with a library such as NumPy:

.. code-block:: python

   import numpy

   def pt1000_temperature(raw):
       """Transfer function of the PT1000 readout circuit."""
       v_out = raw * 3 / 1023
       r = (2310 + 462 * v_out) / (3 - (0.231 + 0.0462 * v_out))
       return (r / 1000 - 1) / 3.85e-3

   xp = list(range(0, 1023, 10))
   fp = [pt1000_temperature(x) for x in xp]

   coef = numpy.polyfit(xp, fp, 2).tolist()
   coef.reverse()   # polyfit returns highest degree first; Polynomial wants x^0 first
   calibrator = Y.Polynomial(coef)

Note the ``reverse()``: NumPy's ``polyfit`` orders coefficients from the
highest power down, while ``Polynomial`` expects them from x\ :sup:`0`
upward. Libraries used this way are build-time tools only — PyMDB itself
has no such dependencies, and nothing of them remains in the exported
XTCE.

.. note::

   In the other direction, calibrators also apply to *command arguments*:
   the operator enters the engineering value and Yamcs de-calibrates it to
   the raw count before encoding. Alarm thresholds and validity ranges are
   always expressed on the calibrated (engineering) side.
