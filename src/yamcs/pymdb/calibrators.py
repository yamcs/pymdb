from dataclasses import dataclass


@dataclass
class Calibrator:
    """
    Transform a raw value (e.g. an integer count from a spacecraft) to an
    engineering value for users (e.g. a float).
    """


@dataclass
class Polynomial(Calibrator):
    """
    A calibration type where a curve in a raw vs calibrated plane is described
    using a set of polynomial coefficients. Raw values are converted to
    calibrated values by finding a position on the curve corresponding to the
    raw value.
    """

    coefficients: list[float]
    """Coefficients ordered from X^0 to X^n"""


@dataclass
class Interpolate(Calibrator):
    """
    One-dimensional piecewise interpolation. A segmented line in a raw vs
    calibrated plane is described using a set of points. Raw values are
    converted to calibrated values by finding a position on the line
    corresponding to the raw value.
    """

    xp: list[float]
    """
    The x-coordinates of the data points. Should be increasing.
    """

    fp: list[float]
    """
    The y-coordinates of the data-points. Should have same length as ``xp``.
    """
