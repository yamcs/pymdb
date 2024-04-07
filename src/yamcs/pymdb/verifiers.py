from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from yamcs.pymdb.algorithms import UnnamedAlgorithm
    from yamcs.pymdb.containers import Container
    from yamcs.pymdb.expressions import Expression
    from yamcs.pymdb.parameters import Parameter


class TerminationAction(Enum):
    SUCCESS = auto()
    FAIL = auto()


class AlgorithmCheck:
    def __init__(self, algorithm: UnnamedAlgorithm):
        self.algorithm = algorithm


class ContainerCheck:
    def __init__(self, container: Container):
        self.container = container


class ExpressionCheck:
    def __init__(self, expression: Expression):
        self.expression = expression


Check: TypeAlias = AlgorithmCheck | ContainerCheck | ExpressionCheck


@dataclass
class Verifier:
    check: Check
    """Check to perform"""

    timeout: float
    """How long to wait for a check result (in seconds)"""

    delay: float = 0
    """Wait time before starting to check (in seconds)"""

    name: str | None = None
    """Optional name"""

    on_success: TerminationAction | None = None
    """What it means for the whole command, when this single verifier succeeds"""

    on_fail: TerminationAction | None = None
    """What it means for the whole command, when this single verifier fails"""

    on_timeout: TerminationAction | None = None
    """What it means for the whole command, when this single verifier times out"""

    extra: dict[str, str] = field(default_factory=lambda: {})
    """Arbitrary information, keyed by name"""


@dataclass
class TransferredToRangeVerifier(Verifier):
    """
    A verifier that checks whether the command has been received to the network
    that connects the ground system to the spacecraft.

    The result of this verifier must originate from something other than the
    spacecraft.
    """

    on_fail: TerminationAction | None = TerminationAction.FAIL
    """What it means for the whole command, when this single verifier fails"""


@dataclass
class SentFromRangeVerifier(Verifier):
    """
    A verifier that checks whether the command been transmitted to the
    spacecraft by the network that connects the ground system to the
    spacecraft.

    The result of this verifier must originate from something other than the
    system.
    """

    on_fail: TerminationAction | None = TerminationAction.FAIL
    """What it means for the whole command, when this single verifier fails"""


@dataclass
class ReceivedVerifier(Verifier):
    """
    A verifier that checks that the system has received the command
    """

    on_fail: TerminationAction | None = TerminationAction.FAIL
    """What it means for the whole command, when this single verifier fails"""


@dataclass
class AcceptedVerifier(Verifier):
    """
    A verifier that checks that the system has accepted the command
    """

    on_fail: TerminationAction | None = TerminationAction.FAIL
    """What it means for the whole command, when this single verifier fails"""


@dataclass
class QueuedVerifier(Verifier):
    """
    A verifier that checks that the command is scheduled for execution by
    the system
    """

    on_fail: TerminationAction | None = TerminationAction.FAIL
    """What it means for the whole command, when this single verifier fails"""


@dataclass
class ExecutionVerifier(Verifier):
    """
    A verifier that checks that the command is being executed.
    """

    on_fail: TerminationAction | None = TerminationAction.FAIL
    """What it means for the whole command, when this single verifier fails"""


@dataclass
class CompleteVerifier(Verifier):
    """
    A verifier that checks whether the command to be considered completed
    """

    on_success: TerminationAction | None = TerminationAction.SUCCESS
    """What it means for the whole command, when this single verifier succeeds"""

    on_fail: TerminationAction | None = TerminationAction.FAIL
    """What it means for the whole command, when this single verifier fails"""

    return_parameter: Parameter | None = None


@dataclass
class FailedVerifier(Verifier):
    """
    A verifier that checks that the command failed.
    """

    on_success: TerminationAction | None = TerminationAction.FAIL
    """What it means for the whole command, when this single verifier succeeds"""

    return_parameter: Parameter | None = None
