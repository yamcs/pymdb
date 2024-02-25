from textwrap import dedent
from typing import NamedTuple

from yamcs.pymdb.commands import (
    ArgumentEntry,
    BooleanArgument,
    Command,
    FixedValueEntry,
    IntegerArgument,
)
from yamcs.pymdb.containers import Container, ParameterEntry
from yamcs.pymdb.datatypes import BooleanMember, EnumeratedMember, IntegerMember
from yamcs.pymdb.encodings import (
    uint1_t,
    uint2_t,
    uint3_t,
    uint11_t,
    uint14_t,
    uint16_t,
)
from yamcs.pymdb.expressions import ParameterMember
from yamcs.pymdb.parameters import AggregateParameter, IntegerParameter
from yamcs.pymdb.systems import System


class CcsdsHeader(NamedTuple):
    tm_container: Container
    tm_version: ParameterMember
    tm_type: ParameterMember
    tm_secondary_header: ParameterMember
    tm_apid: ParameterMember
    tc_command: Command
    tc_secondary_header: BooleanArgument
    tc_apid: IntegerArgument


def add_ccsds_header(system: System) -> CcsdsHeader:
    tm_version_member = IntegerMember(
        name="version",
        signed=False,
        encoding=uint3_t,
    )
    tm_type_member = EnumeratedMember(
        name="type",
        choices=[
            (0, "TM"),
            (1, "TC"),
        ],
        long_description=dedent(
            """
            Used to distinguish telemetry (or reporting) packets from
            telecommand (or requesting) packets.

            Note that some systems, notably the International Space System,
            use a different convention where 0=core and 1=payload.
            """
        ),
        encoding=uint1_t,
    )
    tm_secondary_header_member = BooleanMember(
        name="secondary_header",
        zero_string_value="Not Present",
        one_string_value="Present",
        encoding=uint1_t,
    )
    tm_apid_member = IntegerMember(
        name="apid",
        signed=False,
        encoding=uint11_t,
    )
    tm_packet_id = AggregateParameter(
        system=system,
        name="ccsds_packet_id",
        short_description="First word of the primary CCSDS header",
        members=[
            tm_version_member,
            tm_type_member,
            tm_secondary_header_member,
            tm_apid_member,
        ],
    )

    tm_packet_sequence = AggregateParameter(
        system=system,
        name="ccsds_packet_sequence",
        short_description="Second word of the primary CCSDS header",
        members=[
            EnumeratedMember(
                name="group_flags",
                choices=[
                    (0, "Continuation"),
                    (1, "First"),
                    (2, "Last"),
                    (3, "Standalone"),
                ],
                encoding=uint2_t,
            ),
            IntegerMember(
                name="source_sequence_count",
                signed=False,
                encoding=uint14_t,
            ),
        ],
    )

    tm_packet_length = IntegerParameter(
        system=system,
        name="ccsds_packet_length",
        signed=False,
        units="Octets",
        encoding=uint16_t,
    )

    tm_container = Container(
        system=system,
        name="ccsds_space_packet",
        abstract=True,
        short_description="CCSDS 133.0-B-1 Space Packet",
        long_description=dedent(
            """
            Represents a Space Packet as defined in CCSDS 133.0-B-1

            The first 6 bytes of a Space Packet are known as the
            "Primary Header".
            """
        ),
        bits=8 * 6,
        entries=[
            ParameterEntry(tm_packet_id),
            ParameterEntry(tm_packet_sequence),
            ParameterEntry(tm_packet_length),
        ],
    )

    tc_secondary_header = BooleanArgument(
        name="ccsds_secondary_header",
        zero_string_value="Not Present",
        one_string_value="Present",
        encoding=uint1_t,
    )

    tc_apid = IntegerArgument(
        name="ccsds_apid",
        signed=False,
        encoding=uint11_t,
    )

    tc_command = Command(
        system=system,
        name="ccsds_space_packet",
        abstract=True,
        short_description="CCSDS 133.0-B-1 Space Packet",
        long_description=dedent(
            """
            Represents a Space Packet as defined in CCSDS 133.0-B-1

            The first 6 bytes of a Space Packet are known as the
            "Primary Header".
            """
        ),
        arguments=[
            tc_secondary_header,
            tc_apid,
        ],
        entries=[
            FixedValueEntry(
                name="ccsds_version",
                binary=bytes.fromhex("00"),
                bits=3,
            ),
            FixedValueEntry(
                name="ccsds_type",
                binary=bytes.fromhex("01"),
                bits=1,
            ),
            ArgumentEntry(tc_secondary_header),
            ArgumentEntry(tc_apid),
            FixedValueEntry(
                name="ccsds_group_flags",
                binary=bytes.fromhex("03"),  # Always standalone
                bits=2,
            ),
            FixedValueEntry(
                name="ccsds_source_sequence_count",
                binary=bytes.fromhex("0000"),
                bits=14,
                short_description="Value set by Yamcs during link post-processing",
            ),
            FixedValueEntry(
                name="ccsds_packet_length",
                binary=bytes.fromhex("0000"),
                bits=16,
                short_description="Value set by Yamcs during link post-processing",
            ),
        ],
    )

    tm_version = ParameterMember(
        tm_packet_id,
        path=tm_version_member,
    )
    tm_type = ParameterMember(
        tm_packet_id,
        path=tm_type_member,
    )
    tm_secondary_header = ParameterMember(
        tm_packet_id,
        path=tm_secondary_header_member,
    )
    tm_apid = ParameterMember(
        tm_packet_id,
        path=tm_apid_member,
    )

    return CcsdsHeader(
        tm_container,
        tm_version,
        tm_type,
        tm_secondary_header,
        tm_apid,
        tc_command,
        tc_secondary_header,
        tc_apid,
    )
