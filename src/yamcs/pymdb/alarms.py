from collections.abc import Mapping
from enum import Enum, auto


class AlarmLevel(Enum):
    """
    Alarm levels with increasing concern.
    """

    NORMAL = auto()
    """
    Used to indicate there is no concern.
    """

    WATCH = auto()
    """
    Least concern. Considered to be below the more commonly used WARNING level.
    """

    WARNING = auto()
    """
    Concern that represents the most commonly used minimum concern level for
    many software applications.
    """

    DISTRESS = auto()
    """
    An alarm level of concern in-between the more commonly used WARNING and
    CRITICAL levels.
    """

    CRITICAL = auto()
    """
    An alarm level of concern that represents the most commonly used maximum
    concern level for many software applications.
    """

    SEVERE = auto()
    """
    An alarm level of highest concern. Considered to be above the most commonly
    used Critical level.
    """


class Alarm:
    """
    Base class for an alarm definition
    """

    def __init__(self, minimum_violations: int = 1):
        self.minimum_violations = minimum_violations


class EnumerationAlarm(Alarm):
    """
    Alarm definition for an :class:`EnumeratedParameter`
    """

    def __init__(
        self,
        states: Mapping[str, AlarmLevel],
        *,
        default_level: AlarmLevel = AlarmLevel.NORMAL,
        minimum_violations: int = 1,
    ):
        Alarm.__init__(
            self,
            minimum_violations=minimum_violations,
        )
        self.states: dict[str, AlarmLevel] = dict(states)
        """
        Alarm levels, keyed by enumeration label
        """

        self.default_level: AlarmLevel = default_level
        """
        Default alarm level (when the parameter value is not contained in
        :attr:`states`)
        """


class ThresholdAlarm(Alarm):
    """
    Alarm definition specifying the thresholds for detecting out of limit values.

    The threshold have increasing severity levels: watch, warning, distress, critical
    and severe.

    Warning and critical are the most commonly used levels.
    """

    def __init__(
        self,
        *,
        watch_low: float | None = None,
        watch_low_exclusive: bool = False,
        warning_low: float | None = None,
        warning_low_exclusive: bool = False,
        distress_low: float | None = None,
        distress_low_exclusive: bool = False,
        critical_low: float | None = None,
        critical_low_exclusive: bool = False,
        severe_low: float | None = None,
        severe_low_exclusive: bool = False,
        severe_high: float | None = None,
        severe_high_exclusive: bool = False,
        critical_high: float | None = None,
        critical_high_exclusive: bool = False,
        distress_high: float | None = None,
        distress_high_exclusive: bool = False,
        warning_high: float | None = None,
        warning_high_exclusive: bool = False,
        watch_high: float | None = None,
        watch_high_exclusive: bool = False,
        minimum_violations: int = 1,
    ):
        Alarm.__init__(
            self,
            minimum_violations=minimum_violations,
        )
        self.watch_low = watch_low
        self.watch_low_exclusive = watch_low_exclusive
        self.warning_low = warning_low
        self.warning_low_exclusive = warning_low_exclusive
        self.distress_low = distress_low
        self.distress_low_exclusive = distress_low_exclusive
        self.critical_low = critical_low
        self.critical_low_exclusive = critical_low_exclusive
        self.severe_low = severe_low
        self.severe_low_exclusive = severe_low_exclusive
        self.severe_high = severe_high
        self.severe_high_exclusive = severe_high_exclusive
        self.critical_high = critical_high
        self.critical_high_exclusive = critical_high_exclusive
        self.distress_high = distress_high
        self.distress_high_exclusive = distress_high_exclusive
        self.warning_high = warning_high
        self.warning_high_exclusive = warning_high_exclusive
        self.watch_high = watch_high
        self.watch_high_exclusive = watch_high_exclusive
