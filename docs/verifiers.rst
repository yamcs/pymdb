====================
Command Verification
====================

.. index:: Verifier

Sending a command is only half the job; the ground system should also
confirm what became of it. Verifiers describe how Yamcs tracks a command
through its lifecycle, by checking telemetry after transmission. The
outcome is visible to operators as the command's acknowledgment status,
and drives automation such as command queues and procedures.


Verification stages
===================

.. index:: TransferredToRangeVerifier
.. index:: SentFromRangeVerifier
.. index:: ReceivedVerifier
.. index:: AcceptedVerifier
.. index:: QueuedVerifier
.. index:: ExecutionVerifier
.. index:: CompleteVerifier
.. index:: FailedVerifier

A command can define verifiers for successive stages. Each stage is a
field on the ``Command`` object, set after construction:

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Field
     - Confirms that...
   * - ``transferred_to_range_verifier``
     - the command reached the ground network connecting to the
       spacecraft
   * - ``sent_from_range_verifier``
     - the ground network transmitted it to the spacecraft
   * - ``received_verifier``
     - the remote system received it
   * - ``accepted_verifier``
     - the remote system accepted it
   * - ``queued_verifier``
     - it is scheduled for execution
   * - ``execution_verifiers`` (list)
     - it is being executed
   * - ``complete_verifiers`` (list)
     - it completed
   * - ``failed_verifier``
     - it failed

Most projects use only one or two stages — typically a complete verifier,
sometimes with a failed verifier for an explicit error report:

.. code-block:: python

   reboot = Y.Command(system=obc, name="Reboot")

   reboot.complete_verifiers = [
       Y.CompleteVerifier(
           check=Y.ExpressionCheck(Y.eq(last_command_status, "OK")),
           timeout=5,
       ),
   ]


Checks
======

.. index:: ExpressionCheck
.. index:: ContainerCheck
.. index:: AlgorithmCheck

Each verifier performs one check, given as its ``check`` option:

``ExpressionCheck(expression)``
    Succeeds when the :doc:`expression <expressions>` over telemetry
    parameters evaluates to true.

``ContainerCheck(container)``
    Succeeds when an instance of the given container (packet) is received
    — e.g. an acknowledgment packet.

``AlgorithmCheck(algorithm)``
    Delegates the decision to a custom algorithm (an ``UnnamedAlgorithm``,
    see :doc:`algorithms`), for logic beyond simple expressions — matching
    a command counter echoed in telemetry, for instance. The algorithm's
    inputs may reference Yamcs-internal parameters by name, such as
    ``/yamcs/cmdHist/binary`` for the binary of the command being
    verified.


The request/reply pattern
=========================

Many devices answer every command with a reply packet. The natural model
is a *pair*: a command, and a container identifying its reply — connected
by a ``ContainerCheck``:

.. code-block:: python

   ping = Y.Command(
       system=device,
       name="ping",
       base=header.tc_command,
       assignments={dport_arg.name: 1},
   )

   ping_reply = Y.Container(
       system=device,
       name="ping_reply",
       base=header.tm_container,
       condition=Y.eq(header.tm_sport, 1),
   )

   ping.complete_verifiers.append(
       Y.CompleteVerifier(check=Y.ContainerCheck(ping_reply), timeout=5)
   )

The command completes when its reply arrives, and any parameters carried
by the reply container are extracted as regular telemetry. Projects with
many such request/reply services usually generate the trio —
command, reply container, verifier — from a single helper function; see
:doc:`large-models`.


Timing
======

``timeout`` (required) bounds how long the verifier waits for its check to
succeed. ``delay`` postpones the start of checking, for systems that need
time to react:

.. code-block:: python

   Y.CompleteVerifier(
       check=Y.ContainerCheck(ack_packet),
       delay=2,      # start checking after 2 s
       timeout=10,   # then allow 10 s for the ack
   )


Outcomes
========

.. index:: TerminationAction

What a verifier's success, failure or timeout means *for the command as a
whole* is set with ``on_success``, ``on_fail`` and ``on_timeout``, each
either ``None`` (no effect, continue with other verifiers) or a
``TerminationAction``: ``SUCCESS`` or ``FAIL``.

The defaults do the expected thing:

* every stage verifier fails the command when its check fails
  (``on_fail=FAIL``);
* a ``CompleteVerifier`` additionally completes the command on success
  (``on_success=SUCCESS``);
* a ``FailedVerifier`` fails the command when its check *succeeds*
  (``on_success=FAIL``).

Override them for less common arrangements — for example several
alternative complete verifiers where none is individually decisive.

``CompleteVerifier`` and ``FailedVerifier`` also accept a
``return_parameter``, a parameter whose value Yamcs attaches to the
command's completion as its return value.

.. tip::

   Every non-abstract command should have some verifier able to complete
   it successfully, otherwise it lingers unacknowledged. The helper
   ``checks.check_complete_verifiers`` audits a whole system tree for
   this — see :doc:`generating`.
