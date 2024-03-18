from __future__ import annotations

import os
import xml.etree.ElementTree as ET
from binascii import hexlify
from enum import Enum
from typing import TYPE_CHECKING, Any, Mapping, cast
from xml.dom import minidom

from yamcs.pymdb.alarms import AlarmLevel, ThresholdAlarm
from yamcs.pymdb.algorithms import JavaAlgorithm
from yamcs.pymdb.ancillary import AncillaryData
from yamcs.pymdb.calibrators import Calibrator, Interpolate, Polynomial
from yamcs.pymdb.commands import (
    Argument,
    ArgumentEntry,
    BooleanArgument,
    Command,
    CommandLevel,
    EnumeratedArgument,
    FixedValueEntry,
)
from yamcs.pymdb.containers import (
    Container,
    ContainerEntry,
    ParameterEntry,
    ReferenceLocation,
)
from yamcs.pymdb.datatypes import (
    AbsoluteTimeDataType,
    AbsoluteTimeMember,
    AggregateDataType,
    AggregateMember,
    ArrayDataType,
    ArrayMember,
    BinaryDataType,
    BinaryMember,
    BooleanDataType,
    BooleanMember,
    Choices,
    DataType,
    EnumeratedDataType,
    EnumeratedMember,
    Epoch,
    FloatDataType,
    FloatMember,
    IntegerDataType,
    IntegerMember,
    StringDataType,
    StringMember,
)
from yamcs.pymdb.encodings import (
    BinaryDataEncoding,
    ByteOrder,
    Charset,
    DataEncoding,
    FloatDataEncoding,
    FloatDataEncodingScheme,
    FloatTimeEncoding,
    IntegerDataEncoding,
    IntegerDataEncodingScheme,
    IntegerTimeEncoding,
    StringDataEncoding,
)
from yamcs.pymdb.exceptions import ExportError
from yamcs.pymdb.expressions import (
    AndExpression,
    EqExpression,
    Expression,
    GteExpression,
    GtExpression,
    LteExpression,
    LtExpression,
    NeExpression,
    OrExpression,
    ParameterMember,
)
from yamcs.pymdb.parameters import (
    AbsoluteTimeParameter,
    AggregateParameter,
    ArrayParameter,
    BinaryParameter,
    BooleanParameter,
    DataSource,
    EnumeratedParameter,
    FloatParameter,
    IntegerParameter,
    Parameter,
    StringParameter,
)
from yamcs.pymdb.verifiers import (
    AcceptedVerifier,
    AlgorithmCheck,
    CompleteVerifier,
    ContainerCheck,
    ExecutionVerifier,
    ExpressionCheck,
    FailedVerifier,
    QueuedVerifier,
    ReceivedVerifier,
    SentFromRangeVerifier,
    TransferredToRangeVerifier,
    Verifier,
)

if TYPE_CHECKING:
    from yamcs.pymdb.systems import System


def _to_xml_value(value: Any):
    if isinstance(value, (bytes, bytearray)):
        return hexlify(value).decode("ascii")
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, Enum):
        return value.name
    else:
        return str(value)


def _to_isoduration(seconds: float):
    d = int(seconds // 86400)
    s = round(seconds % 60, 6)
    hms = (
        int(seconds // 3600 % 24),
        int(seconds // 60 % 60),
        s if s % 1 != 0 else int(s),
    )
    t = "".join([str(p[0]) + p[1] for p in zip(hms, ["H", "M", "S"]) if p[0]])
    sep = "T" if any(hms) else ""
    return "P" + (str(d) + "D" if d else "") + sep + (t if seconds else "T0S")


class XTCE12Generator:
    def __init__(self, system: System):
        self.system = system

    def to_xtce(
        self,
        indent="",
        add_schema_location: bool = True,
        top_comment: bool | str = True,
    ) -> str:
        el = self.generate_space_system(
            self.system,
            add_schema_location=add_schema_location,
        )
        xtce = ET.tostring(el, encoding="unicode")
        xtce_dom = minidom.parseString(xtce)

        if top_comment is True:
            top_comment = (
                "\nThis file was automatically generated with Yamcs PyMDB.\n"
                "See https://github.com/yamcs/pymdb\n"
            )
        if top_comment:
            comment_el = xtce_dom.createComment(top_comment)
            xtce_dom.insertBefore(comment_el, xtce_dom.firstChild)
        return xtce_dom.toprettyxml(indent=indent)

    def add_command_metadata(self, parent: ET.Element, system: System):
        el = ET.SubElement(parent, "CommandMetaData")
        if system.commands:
            self.add_argument_type_set(el, system)
            self.add_meta_command_set(el, system)

    def add_argument_type_set(self, parent: ET.Element, system: System):
        set_el = None
        for command in system.commands:
            for argument in command.arguments:
                # Create this lazily, XML should not have this element if it's empty
                if not set_el:
                    set_el = ET.SubElement(parent, "ArgumentTypeSet")

                # Make an argument type unique to each command
                self.add_argument_type(
                    set_el,
                    name=f"{command.name}__{argument.name}",
                    default=argument.default,
                    data_type=argument,
                )

    def add_meta_command_set(self, parent: ET.Element, system: System):
        el = ET.SubElement(parent, "MetaCommandSet")
        for command in system.commands:
            self.add_meta_command(el, command)

    def add_meta_command(self, parent: ET.Element, command: Command):
        el = ET.SubElement(parent, "MetaCommand")
        el.attrib["name"] = command.name
        el.attrib["abstract"] = _to_xml_value(command.abstract)

        if command.short_description:
            el.attrib["shortDescription"] = command.short_description

        if command.long_description:
            ET.SubElement(el, "LongDescription").text = command.long_description

        if command.aliases:
            self.add_aliases(el, command.aliases)

        if command.extra:
            self.add_ancillary_data(el, command.extra)

        if command.parent:
            base_el = ET.SubElement(el, "BaseMetaCommand")
            base_el.attrib["metaCommandRef"] = self.make_ref(
                target=command.parent.qualified_name,
                start=command.system,
            )

            if command.assignments:
                assignments_el = ET.SubElement(base_el, "ArgumentAssignmentList")
                for k, v in command.assignments.items():
                    arg = command.get_argument(k)

                    str_value = _to_xml_value(v)
                    if isinstance(arg, BooleanArgument) and isinstance(v, bool):
                        str_value = arg.one_string_value if v else arg.zero_string_value
                    elif isinstance(arg, EnumeratedArgument) and isinstance(v, int):
                        str_value = arg.label_for(v)

                    assignment_el = ET.SubElement(assignments_el, "ArgumentAssignment")
                    assignment_el.attrib["argumentName"] = k
                    assignment_el.attrib["argumentValue"] = str_value

        if command.arguments:
            args_el = ET.SubElement(el, "ArgumentList")

            for argument in command.arguments:
                self.add_argument(args_el, command, argument)

        container_el = ET.SubElement(el, "CommandContainer")
        container_el.attrib["name"] = command.name

        self.add_command_entry_list(container_el, command)

        if command.parent:
            base_el = ET.SubElement(container_el, "BaseContainer")
            base_el.attrib["containerRef"] = self.make_ref(
                target=command.parent.qualified_name,
                start=command.system,
            )

        sign_el = ET.SubElement(el, "DefaultSignificance")

        if command.level == CommandLevel.NORMAL:
            sign_el.attrib["consequenceLevel"] = "normal"
        elif command.level == CommandLevel.VITAL:
            sign_el.attrib["consequenceLevel"] = "vital"
        elif command.level == CommandLevel.CRITICAL:
            sign_el.attrib["consequenceLevel"] = "critical"
        elif command.level == CommandLevel.FORBIDDEN:
            sign_el.attrib["consequenceLevel"] = "forbidden"
        else:
            raise ExportError(f"Unexpected command level {command.level}")

        if command.warning_message:
            sign_el.attrib["reasonForWarning"] = command.warning_message

        self.add_verifier_set(el, command)

    def add_verifier_set(self, parent: ET.Element, command: Command):
        set_el = ET.SubElement(parent, "VerifierSet")

        if command.transferred_to_range_verifier:
            self.add_verifier(set_el, command, command.transferred_to_range_verifier)
        if command.sent_from_range_verifier:
            self.add_verifier(set_el, command, command.sent_from_range_verifier)
        if command.received_verifier:
            self.add_verifier(set_el, command, command.received_verifier)
        if command.accepted_verifier:
            self.add_verifier(set_el, command, command.accepted_verifier)
        if command.queued_verifier:
            self.add_verifier(set_el, command, command.queued_verifier)
        for verifier in command.execution_verifiers or []:
            self.add_verifier(set_el, command, verifier)
        for verifier in command.complete_verifiers or []:
            self.add_verifier(set_el, command, verifier)
        if command.failed_verifier:
            self.add_verifier(set_el, command, command.failed_verifier)

    def add_verifier(
        self,
        parent: ET.Element,
        command: Command,
        verifier: Verifier,
    ):
        if isinstance(verifier, TransferredToRangeVerifier):
            el = ET.SubElement(parent, "TransferredToRangeVerifier")
        elif isinstance(verifier, SentFromRangeVerifier):
            el = ET.SubElement(parent, "SentFromRangeVerifier")
        elif isinstance(verifier, ReceivedVerifier):
            el = ET.SubElement(parent, "ReceivedVerifier")
        elif isinstance(verifier, AcceptedVerifier):
            el = ET.SubElement(parent, "AcceptedVerifier")
        elif isinstance(verifier, QueuedVerifier):
            el = ET.SubElement(parent, "QueuedVerifier")
        elif isinstance(verifier, ExecutionVerifier):
            el = ET.SubElement(parent, "ExecutionVerifier")
        elif isinstance(verifier, CompleteVerifier):
            el = ET.SubElement(parent, "CompleteVerifier")
        elif isinstance(verifier, FailedVerifier):
            el = ET.SubElement(parent, "FailedVerifier")
        else:
            raise ExportError(f"Unexpected verifier {verifier.__class__}")

        if verifier.name:
            el.attrib["name"] = verifier.name

        extra = verifier.extra or {}
        if verifier.on_success:
            extra["yamcs.onSuccess"] = verifier.on_success.name
        else:
            # Be explicit, to override Yamcs defaults
            extra["yamcs.onSuccess"] = ""

        if verifier.on_fail:
            extra["yamcs.onFail"] = verifier.on_fail.name
        else:
            # Be explicit, to override Yamcs defaults
            extra["yamcs.onFail"] = ""

        if verifier.on_timeout:
            extra["yamcs.onTimeout"] = verifier.on_timeout.name
        else:
            # Be explicit, to override Yamcs defaults
            extra["yamcs.onTimeout"] = ""

        self.add_ancillary_data(el, extra)

        check = verifier.check
        if isinstance(check, ContainerCheck):
            ref_el = ET.SubElement(el, "ContainerRef")
            ref_el.attrib["containerRef"] = self.make_ref(
                target=check.container.qualified_name,
                start=command.system,
            )
        elif isinstance(check, ExpressionCheck):
            expr_el = ET.SubElement(el, "BooleanExpression")
            self.add_expression_condition(expr_el, command.system, check.expression)
        elif isinstance(check, AlgorithmCheck):
            self.add_input_only_algorithm(el, "CustomAlgorithm", check.algorithm)
        else:
            raise ExportError(f"Unexpected check {check.__class__}")

        win_el = ET.SubElement(el, "CheckWindow")
        win_el.attrib["timeToStartChecking"] = _to_isoduration(verifier.delay)
        win_el.attrib["timeToStopChecking"] = _to_isoduration(verifier.timeout)
        win_el.attrib["timeWindowIsRelativeTo"] = "commandRelease"

        if isinstance(
            verifier,
            (
                CompleteVerifier,
                FailedVerifier,
            ),
        ):
            if verifier.return_parameter:
                ret_el = ET.SubElement(el, "ReturnParmRef")
                ret_el.attrib["parameterRef"] = self.make_ref(
                    target=verifier.return_parameter.qualified_name,
                    start=command.system,
                )

    def add_argument(self, parent: ET.Element, command: Command, argument: Argument):
        el = ET.SubElement(parent, "Argument")
        el.attrib["name"] = argument.name
        el.attrib["argumentTypeRef"] = f"{command.name}__{argument.name}"

        if argument.short_description:
            el.attrib["shortDescription"] = argument.short_description

        if argument.long_description:
            ET.SubElement(el, "LongDescription").text = argument.long_description

    def add_aliases(self, parent: ET.Element, aliases: dict[str, str]):
        aliases_el = ET.SubElement(parent, "AliasSet")
        for k, v in aliases.items():
            alias_el = ET.SubElement(aliases_el, "Alias")
            alias_el.attrib["nameSpace"] = k
            alias_el.attrib["alias"] = v

    def add_ancillary_data(
        self,
        parent: ET.Element,
        extra: Mapping[str, str | list[str]] | AncillaryData,
    ):
        if isinstance(extra, AncillaryData):
            if len(extra):
                set_el = ET.SubElement(parent, "AncillaryDataSet")
                for item in extra:
                    el = ET.SubElement(set_el, "AncillaryData")
                    el.attrib["name"] = item.name
                    if item.url:
                        el.attrib["href"] = item.url
                    if item.mimetype:
                        el.attrib["mimeType"] = item.mimetype
                    el.text = item.value
        else:
            set_el = ET.SubElement(parent, "AncillaryDataSet")
            for k, v in extra.items():
                # Yamcs allows the 'name' to be non-unique. This is somewhat unexpected,
                # but we support it because it is needed with some special options.
                if isinstance(v, list):
                    for item in v:
                        el = ET.SubElement(set_el, "AncillaryData")
                        el.attrib["name"] = k
                        el.text = item
                else:
                    el = ET.SubElement(set_el, "AncillaryData")
                    el.attrib["name"] = k
                    el.text = v

    def add_command_entry_list(self, parent: ET.Element, command: Command):
        el = ET.SubElement(parent, "EntryList")
        for entry in command.entries:
            if isinstance(entry, FixedValueEntry):
                self.add_fixed_value_entry(el, command, entry)
            elif isinstance(entry, ArgumentEntry):
                self.add_argument_ref_entry(el, command, entry)
            else:
                raise Exception(f"Unexpected command entry {entry.__class__}")

    def add_fixed_value_entry(
        self,
        parent: ET.Element,
        command: Command,
        entry: FixedValueEntry,
    ):
        el = ET.SubElement(parent, "FixedValueEntry")
        el.attrib["binaryValue"] = hexlify(entry.binary).decode("ascii")

        if entry.bits is None:
            el.attrib["sizeInBits"] = str(8 * len(entry.binary))
        else:
            el.attrib["sizeInBits"] = str(entry.bits)

        if entry.name:
            el.attrib["name"] = entry.name
        if entry.short_description:
            el.attrib["shortDescription"] = entry.short_description

        loc_el = ET.SubElement(el, "LocationInContainerInBits")

        if entry.reference_location == ReferenceLocation.PREVIOUS_ENTRY:
            loc_el.attrib["referenceLocation"] = "previousEntry"
        elif entry.reference_location == ReferenceLocation.CONTAINER_START:
            loc_el.attrib["referenceLocation"] = "containerStart"
        else:
            raise Exception("Unexpected reference location")

        fv_el = ET.SubElement(loc_el, "FixedValue")
        fv_el.text = str(entry.location_in_bits)

        if entry.include_condition:
            cond_el = ET.SubElement(el, "IncludeCondition")
            expr_el = ET.SubElement(cond_el, "BooleanExpression")
            self.add_expression_condition(
                expr_el,
                system=command.system,
                expression=entry.include_condition,
            )

    def add_argument_ref_entry(
        self,
        parent: ET.Element,
        command: Command,
        entry: ArgumentEntry,
    ):
        el = ET.SubElement(parent, "ArgumentRefEntry")
        el.attrib["argumentRef"] = entry.argument.name

        if entry.short_description:
            el.attrib["shortDescription"] = entry.short_description

        loc_el = ET.SubElement(el, "LocationInContainerInBits")

        if entry.reference_location == ReferenceLocation.PREVIOUS_ENTRY:
            loc_el.attrib["referenceLocation"] = "previousEntry"
        elif entry.reference_location == ReferenceLocation.CONTAINER_START:
            loc_el.attrib["referenceLocation"] = "containerStart"
        else:
            raise Exception("Unexpected reference location")

        fv_el = ET.SubElement(loc_el, "FixedValue")
        fv_el.text = str(entry.location_in_bits)

        if entry.include_condition:
            cond_el = ET.SubElement(el, "IncludeCondition")
            expr_el = ET.SubElement(cond_el, "BooleanExpression")
            self.add_expression_condition(
                expr_el,
                system=command.system,
                expression=entry.include_condition,
            )

    def add_telemetry_metadata(self, parent: ET.Element, system: System):
        el = ET.SubElement(parent, "TelemetryMetaData")
        self.add_parameter_type_set(el, system)
        self.add_parameter_set(el, system)
        self.add_container_set(el, system)

    def add_parameter_type_set(self, parent: ET.Element, system: System):
        if not system.parameters:
            return

        el = ET.SubElement(parent, "ParameterTypeSet")
        for parameter in system.parameters:
            if isinstance(parameter, AbsoluteTimeParameter):
                self.add_absolute_time_parameter_type(
                    el,
                    name=parameter.name,
                    data_type=parameter,
                )
            elif isinstance(parameter, AggregateParameter):
                self.add_aggregate_parameter_type(
                    el,
                    name=parameter.name,
                    data_type=parameter,
                )
            elif isinstance(parameter, ArrayParameter):
                self.add_array_parameter_type(
                    el,
                    name=parameter.name,
                    data_type=parameter,
                )
            elif isinstance(parameter, BinaryParameter):
                self.add_binary_parameter_type(
                    el,
                    name=parameter.name,
                    initial_value=parameter.initial_value,
                    data_type=parameter,
                )
            elif isinstance(parameter, BooleanParameter):
                self.add_boolean_parameter_type(
                    el,
                    name=parameter.name,
                    initial_value=parameter.initial_value,
                    data_type=parameter,
                )
            elif isinstance(parameter, EnumeratedParameter):
                self.add_enumerated_parameter_type(
                    el,
                    name=parameter.name,
                    initial_value=parameter.initial_value,
                    data_type=parameter,
                )
            elif isinstance(parameter, FloatParameter):
                self.add_float_parameter_type(
                    el,
                    name=parameter.name,
                    initial_value=parameter.initial_value,
                    alarm=parameter.alarm,
                    data_type=parameter,
                )
            elif isinstance(parameter, IntegerParameter):
                self.add_integer_parameter_type(
                    el,
                    name=parameter.name,
                    initial_value=parameter.initial_value,
                    alarm=parameter.alarm,
                    data_type=parameter,
                )
            elif isinstance(parameter, StringParameter):
                self.add_string_parameter_type(
                    el,
                    name=parameter.name,
                    initial_value=parameter.initial_value,
                    data_type=parameter,
                )
            else:
                raise ExportError(f"Unexpected parameter type {parameter.__class__}")

    def add_argument_type(
        self,
        parent: ET.Element,
        name: str,
        default: Any,
        data_type: DataType,
    ):
        if isinstance(data_type, AbsoluteTimeDataType):
            self.add_absolute_time_argument_type(parent, name, data_type)
        elif isinstance(data_type, BinaryDataType):
            self.add_binary_argument_type(parent, name, default, data_type)
        elif isinstance(data_type, BooleanDataType):
            self.add_boolean_argument_type(parent, name, default, data_type)
        elif isinstance(data_type, EnumeratedDataType):
            self.add_enumerated_argument_type(parent, name, default, data_type)
        elif isinstance(data_type, FloatDataType):
            self.add_float_argument_type(parent, name, default, data_type)
        elif isinstance(data_type, IntegerDataType):
            self.add_integer_argument_type(parent, name, default, data_type)
        elif isinstance(data_type, StringDataType):
            self.add_string_argument_type(parent, name, default, data_type)
        else:
            raise ExportError(f"Unexpected data type {data_type.__class__}")

    def add_absolute_time_argument_type(
        self,
        parent: ET.Element,
        name: str,
        data_type: AbsoluteTimeDataType,
    ):
        el = ET.SubElement(parent, "AbsoluteTimeArgumentType")
        el.attrib["name"] = name

        if data_type.encoding:
            self.add_data_encoding(el, data_type.encoding)

        ref_el = ET.SubElement(el, "ReferenceTime")

        if isinstance(data_type.reference, Epoch):
            epoch_el = ET.SubElement(ref_el, "Epoch")
            if data_type.reference == Epoch.UNIX:
                epoch_el.text = "UNIX"
            else:
                raise Exception(f"Unexpected epoch {data_type.reference}")
        else:
            raise Exception("Arguments can only reference epoch")

    def add_binary_argument_type(
        self,
        parent: ET.Element,
        name: str,
        default: Any,
        data_type: BinaryDataType,
    ):
        el = ET.SubElement(parent, "BinaryArgumentType")
        el.attrib["name"] = name
        if default:
            el.attrib["initialValue"] = _to_xml_value(default)

        # Non-standard options recognized by Yamcs
        opts = []
        if data_type.min_length is not None:
            opts.append(f"minLength={data_type.min_length}")
        if data_type.max_length is not None:
            opts.append(f"maxLength={data_type.max_length}")
        if opts:
            self.add_ancillary_data(el, {"Yamcs": opts})

        if data_type.units:
            unit_set_el = ET.SubElement(el, "UnitSet")
            unit_el = ET.SubElement(unit_set_el, "Unit")
            unit_el.attrib["form"] = "calibrated"
            unit_el.text = data_type.units

        if data_type.encoding:
            self.add_data_encoding(el, data_type.encoding)

    def add_boolean_argument_type(
        self,
        parent: ET.Element,
        name: str,
        default: Any,
        data_type: BooleanDataType,
    ):
        el = ET.SubElement(parent, "BooleanArgumentType")
        el.attrib["name"] = name

        if default is not None:
            if isinstance(default, bool):
                el.attrib["initialValue"] = (
                    data_type.one_string_value
                    if default
                    else data_type.zero_string_value
                )
            else:
                el.attrib["initialValue"] = str(default)

        el.attrib["zeroStringValue"] = data_type.zero_string_value
        el.attrib["oneStringValue"] = data_type.one_string_value

        if data_type.units:
            unit_set_el = ET.SubElement(el, "UnitSet")
            unit_el = ET.SubElement(unit_set_el, "Unit")
            unit_el.attrib["form"] = "calibrated"
            unit_el.text = data_type.units

        if data_type.encoding:
            self.add_data_encoding(el, data_type.encoding)

    def add_enumerated_argument_type(
        self,
        parent: ET.Element,
        name: str,
        default: Any,
        data_type: EnumeratedDataType,
    ):
        el = ET.SubElement(parent, "EnumeratedArgumentType")
        el.attrib["name"] = name

        if default:
            el.attrib["initialValue"] = str(default)

        if data_type.units:
            unit_set_el = ET.SubElement(el, "UnitSet")
            unit_el = ET.SubElement(unit_set_el, "Unit")
            unit_el.attrib["form"] = "calibrated"
            unit_el.text = data_type.units

        if data_type.encoding:
            self.add_data_encoding(el, data_type.encoding)

        self.add_enumeration_list(el, data_type.choices)

    def add_float_argument_type(
        self,
        parent: ET.Element,
        name: str,
        default: Any,
        data_type: FloatDataType,
    ):
        el = ET.SubElement(parent, "FloatArgumentType")
        el.attrib["name"] = name
        el.attrib["sizeInBits"] = str(data_type.bits)

        if default is not None:
            el.attrib["initialValue"] = str(default)

        if data_type.units:
            unit_set_el = ET.SubElement(el, "UnitSet")
            unit_el = ET.SubElement(unit_set_el, "Unit")
            unit_el.attrib["form"] = "calibrated"
            unit_el.text = data_type.units

        if data_type.encoding:
            self.add_data_encoding(el, data_type.encoding)

        if data_type.minimum is not None or data_type.maximum is not None:
            range_el = ET.SubElement(el, "ValidRange")
            range_el.attrib["validRangeAppliesToCalibrated"] = "true"
            if data_type.minimum is not None:
                if data_type.minimum_inclusive:
                    range_el.attrib["minInclusive"] = str(data_type.minimum)
                else:
                    range_el.attrib["minExclusive"] = str(data_type.minimum)
            if data_type.maximum is not None:
                if data_type.maximum_inclusive:
                    range_el.attrib["maxInclusive"] = str(data_type.maximum)
                else:
                    range_el.attrib["maxExclusive"] = str(data_type.maximum)

    def add_integer_argument_type(
        self,
        parent: ET.Element,
        name: str,
        default: Any,
        data_type: IntegerDataType,
    ):
        el = ET.SubElement(parent, "IntegerArgumentType")
        el.attrib["name"] = name
        el.attrib["signed"] = _to_xml_value(data_type.signed)
        el.attrib["sizeInBits"] = str(data_type.bits)

        if default is not None:
            el.attrib["initialValue"] = _to_xml_value(default)

        if data_type.units:
            unit_set_el = ET.SubElement(el, "UnitSet")
            unit_el = ET.SubElement(unit_set_el, "Unit")
            unit_el.attrib["form"] = "calibrated"
            unit_el.text = data_type.units

        if data_type.encoding:
            self.add_data_encoding(el, data_type.encoding)

        if data_type.minimum is not None or data_type.maximum is not None:
            set_el = ET.SubElement(el, "ValidRangeSet")
            set_el.attrib["validRangeAppliesToCalibrated"] = "true"
            range_el = ET.SubElement(set_el, "ValidRange")
            if data_type.minimum is not None:
                range_el.attrib["minInclusive"] = str(data_type.minimum)
            if data_type.maximum is not None:
                range_el.attrib["maxInclusive"] = str(data_type.maximum)

    def add_string_argument_type(
        self,
        parent: ET.Element,
        name: str,
        default: Any,
        data_type: StringDataType,
    ):
        el = ET.SubElement(parent, "StringArgumentType")
        el.attrib["name"] = name
        if default is not None:
            el.attrib["initialValue"] = _to_xml_value(default)

        if data_type.encoding:
            self.add_data_encoding(el, data_type.encoding)

        if data_type.min_length is not None or data_type.max_length is not None:
            range_el = ET.SubElement(el, "SizeRangeInCharacters")
            if data_type.min_length is not None:
                range_el.attrib["minInclusive"] = str(data_type.min_length)
            if data_type.max_length is not None:
                range_el.attrib["maxInclusive"] = str(data_type.max_length)

    def add_aggregate_parameter_type(
        self,
        parent: ET.Element,
        name: str,
        data_type: AggregateDataType,
    ):
        el = ET.SubElement(parent, "AggregateParameterType")
        el.attrib["name"] = name

        members_el = ET.SubElement(el, "MemberList")
        for member in data_type.members:
            # Always make a new type
            member_type_name = f"{name}__{member.name}"

            member_el = ET.SubElement(members_el, "Member")
            member_el.attrib["name"] = str(member.name)
            member_el.attrib["typeRef"] = member_type_name

            if isinstance(member, AbsoluteTimeMember):
                self.add_absolute_time_parameter_type(
                    parent,
                    name=member_type_name,
                    data_type=member,
                )
            elif isinstance(member, AggregateMember):
                self.add_aggregate_parameter_type(
                    parent,
                    name=member_type_name,
                    data_type=member,
                )
            elif isinstance(member, ArrayMember):
                self.add_array_parameter_type(
                    parent,
                    name=member_type_name,
                    data_type=member,
                )
            elif isinstance(member, BinaryMember):
                self.add_binary_parameter_type(
                    parent,
                    name=member_type_name,
                    initial_value=member.initial_value,
                    data_type=member,
                )
            elif isinstance(member, BooleanMember):
                self.add_boolean_parameter_type(
                    parent,
                    name=member_type_name,
                    initial_value=member.initial_value,
                    data_type=member,
                )
            elif isinstance(member, EnumeratedMember):
                self.add_enumerated_parameter_type(
                    parent,
                    name=member_type_name,
                    initial_value=member.initial_value,
                    data_type=member,
                )
            elif isinstance(member, FloatMember):
                self.add_float_parameter_type(
                    parent,
                    name=member_type_name,
                    initial_value=member.initial_value,
                    alarm=None,
                    data_type=member,
                )
            elif isinstance(member, IntegerMember):
                self.add_integer_parameter_type(
                    parent,
                    name=member_type_name,
                    initial_value=member.initial_value,
                    alarm=None,
                    data_type=member,
                )
            elif isinstance(member, StringMember):
                self.add_string_parameter_type(
                    parent,
                    name=member_type_name,
                    initial_value=member.initial_value,
                    data_type=member,
                )
            else:
                raise ExportError(f"Unexpected member type {member.__class__}")

    def add_array_parameter_type(
        self,
        parent: ET.Element,
        name: str,
        data_type: ArrayDataType,
    ):
        el = ET.SubElement(parent, "ArrayParameterType")
        el.attrib["name"] = name

        element_type_name = f"{name}__el"
        el.attrib["arrayTypeRef"] = element_type_name

        dims_el = ET.SubElement(el, "DimensionList")
        dim_el = ET.SubElement(dims_el, "Dimension")
        start_idx_el = ET.SubElement(dim_el, "StartingIndex")
        ET.SubElement(start_idx_el, "FixedValue").text = "0"
        end_idx_el = ET.SubElement(dim_el, "EndingIndex")
        ET.SubElement(end_idx_el, "FixedValue").text = str(data_type.length - 1)

        el_type = data_type.data_type
        if isinstance(el_type, AbsoluteTimeDataType):
            self.add_absolute_time_parameter_type(
                parent,
                name=element_type_name,
                data_type=el_type,
            )
        elif isinstance(el_type, AggregateDataType):
            self.add_aggregate_parameter_type(
                parent,
                name=element_type_name,
                data_type=el_type,
            )
        elif isinstance(el_type, ArrayDataType):
            self.add_array_parameter_type(
                parent,
                name=element_type_name,
                data_type=el_type,
            )
        elif isinstance(el_type, BinaryDataType):
            self.add_binary_parameter_type(
                parent,
                name=element_type_name,
                initial_value=None,
                data_type=el_type,
            )
        elif isinstance(el_type, BooleanDataType):
            self.add_boolean_parameter_type(
                parent,
                name=element_type_name,
                initial_value=None,
                data_type=el_type,
            )
        elif isinstance(el_type, EnumeratedDataType):
            self.add_enumerated_parameter_type(
                parent,
                name=element_type_name,
                initial_value=None,
                data_type=el_type,
            )
        elif isinstance(el_type, FloatDataType):
            self.add_float_parameter_type(
                parent,
                name=element_type_name,
                initial_value=None,
                alarm=None,
                data_type=el_type,
            )
        elif isinstance(el_type, IntegerDataType):
            self.add_integer_parameter_type(
                parent,
                name=element_type_name,
                initial_value=None,
                alarm=None,
                data_type=el_type,
            )
        elif isinstance(el_type, StringDataType):
            self.add_string_parameter_type(
                parent,
                name=element_type_name,
                initial_value=None,
                data_type=el_type,
            )
        else:
            raise ExportError(f"Unexpected data type {el_type.__class__}")

    def add_absolute_time_parameter_type(
        self,
        parent: ET.Element,
        name: str,
        data_type: AbsoluteTimeDataType,
    ):
        el = ET.SubElement(parent, "AbsoluteTimeParameterType")
        el.attrib["name"] = name

        if data_type.encoding:
            self.add_data_encoding(el, data_type.encoding)

        ref_el = ET.SubElement(el, "ReferenceTime")

        if isinstance(data_type.reference, Epoch):
            epoch_el = ET.SubElement(ref_el, "Epoch")
            if data_type.reference == Epoch.UNIX:
                epoch_el.text = "UNIX"
            else:
                raise Exception(f"Unexpected epoch {data_type.reference}")
        else:
            offset_el = ET.SubElement(ref_el, "OffsetFrom")
            offset_el.attrib["parameterRef"] = self.make_ref(
                data_type.reference.qualified_name,
                start=self.system,
            )

    def add_binary_parameter_type(
        self,
        parent: ET.Element,
        name: str,
        initial_value: Any,
        data_type: BinaryDataType,
    ):
        el = ET.SubElement(parent, "BinaryParameterType")
        el.attrib["name"] = name
        if initial_value:
            el.attrib["initialValue"] = _to_xml_value(initial_value)

        if data_type.units:
            unit_set_el = ET.SubElement(el, "UnitSet")
            unit_el = ET.SubElement(unit_set_el, "Unit")
            unit_el.attrib["form"] = "calibrated"
            unit_el.text = data_type.units

        if data_type.encoding:
            self.add_data_encoding(el, data_type.encoding)

    def add_boolean_parameter_type(
        self,
        parent: ET.Element,
        name: str,
        initial_value: Any,
        data_type: BooleanDataType,
    ):
        el = ET.SubElement(parent, "BooleanParameterType")
        el.attrib["name"] = name

        if initial_value is not None:
            if isinstance(initial_value, bool):
                el.attrib["initialValue"] = (
                    data_type.one_string_value
                    if initial_value
                    else data_type.zero_string_value
                )
            else:
                el.attrib["initialValue"] = str(initial_value)

        el.attrib["zeroStringValue"] = data_type.zero_string_value
        el.attrib["oneStringValue"] = data_type.one_string_value

        if data_type.units:
            unit_set_el = ET.SubElement(el, "UnitSet")
            unit_el = ET.SubElement(unit_set_el, "Unit")
            unit_el.attrib["form"] = "calibrated"
            unit_el.text = data_type.units

        if data_type.encoding:
            self.add_data_encoding(el, data_type.encoding)

    def add_enumerated_parameter_type(
        self,
        parent: ET.Element,
        name: str,
        initial_value: Any,
        data_type: EnumeratedDataType,
    ):
        el = ET.SubElement(parent, "EnumeratedParameterType")
        el.attrib["name"] = name

        if initial_value:
            el.attrib["initialValue"] = initial_value

        if data_type.units:
            unit_set_el = ET.SubElement(el, "UnitSet")
            unit_el = ET.SubElement(unit_set_el, "Unit")
            unit_el.attrib["form"] = "calibrated"
            unit_el.text = data_type.units

        if data_type.encoding:
            self.add_data_encoding(el, data_type.encoding)

        self.add_enumeration_list(el, data_type.choices)

        if isinstance(data_type, EnumeratedParameter):
            if data_type.alarm:
                alarm = data_type.alarm
                alarm_el = ET.SubElement(el, "DefaultAlarm")
                alarm_el.attrib["minViolations"] = str(alarm.minimum_violations)
                alarm_el.attrib["defaultAlarmLevel"] = self.alarm_level_to_text(
                    alarm.default_level
                )
                states_el = ET.SubElement(alarm_el, "EnumerationAlarmList")
                for k, v in alarm.states.items():
                    state_el = ET.SubElement(states_el, "EnumerationAlarm")
                    state_el.attrib["alarmLevel"] = self.alarm_level_to_text(v)
                    state_el.attrib["enumerationLabel"] = k

    def add_float_parameter_type(
        self,
        parent: ET.Element,
        name: str,
        initial_value: Any,
        alarm: ThresholdAlarm | None,
        data_type: FloatDataType,
    ):
        el = ET.SubElement(parent, "FloatParameterType")
        el.attrib["name"] = name
        el.attrib["sizeInBits"] = str(data_type.bits)

        if initial_value is not None:
            el.attrib["initialValue"] = str(initial_value)

        if data_type.units:
            unit_set_el = ET.SubElement(el, "UnitSet")
            unit_el = ET.SubElement(unit_set_el, "Unit")
            unit_el.attrib["form"] = "calibrated"
            unit_el.text = data_type.units

        if data_type.encoding:
            self.add_data_encoding(el, data_type.encoding, data_type.calibrator)

        if data_type.calibrator and not data_type.encoding:
            raise ExportError(
                "A calibrator should only be specified if there is an encoding"
            )

        if data_type.minimum is not None or data_type.maximum is not None:
            range_el = ET.SubElement(el, "ValidRange")
            range_el.attrib["validRangeAppliesToCalibrated"] = "true"
            if data_type.minimum is not None:
                if data_type.minimum_inclusive:
                    range_el.attrib["minInclusive"] = str(data_type.minimum)
                else:
                    range_el.attrib["minExclusive"] = str(data_type.minimum)
            if data_type.maximum is not None:
                if data_type.maximum_inclusive:
                    range_el.attrib["maxInclusive"] = str(data_type.maximum)
                else:
                    range_el.attrib["maxExclusive"] = str(data_type.maximum)

        if alarm:
            alarm_el = ET.SubElement(el, "DefaultAlarm")
            alarm_el.attrib["minViolations"] = str(alarm.minimum_violations)
            self.add_static_alarm_ranges(alarm_el, alarm)

    def add_integer_parameter_type(
        self,
        parent: ET.Element,
        name: str,
        initial_value: Any,
        alarm: ThresholdAlarm | None,
        data_type: IntegerDataType,
    ):
        el = ET.SubElement(parent, "IntegerParameterType")
        el.attrib["name"] = name
        if initial_value is not None:
            el.attrib["initialValue"] = str(initial_value)
        el.attrib["signed"] = _to_xml_value(data_type.signed)
        el.attrib["sizeInBits"] = str(data_type.bits)

        if data_type.units:
            unit_set_el = ET.SubElement(el, "UnitSet")
            unit_el = ET.SubElement(unit_set_el, "Unit")
            unit_el.attrib["form"] = "calibrated"
            unit_el.text = data_type.units

        if data_type.encoding:
            self.add_data_encoding(el, data_type.encoding, data_type.calibrator)

        if data_type.calibrator and not data_type.encoding:
            raise ExportError(
                "A calibrator should only be specified if there is an encoding"
            )

        if data_type.minimum is not None or data_type.maximum is not None:
            range_el = ET.SubElement(el, "ValidRange")
            range_el.attrib["validRangeAppliesToCalibrated"] = "true"
            if data_type.minimum is not None:
                range_el.attrib["minInclusive"] = str(data_type.minimum)
            if data_type.maximum is not None:
                range_el.attrib["maxInclusive"] = str(data_type.maximum)

        if alarm:
            alarm_el = ET.SubElement(el, "DefaultAlarm")
            alarm_el.attrib["minViolations"] = str(alarm.minimum_violations)
            self.add_static_alarm_ranges(alarm_el, alarm)

    def add_string_parameter_type(
        self,
        parent: ET.Element,
        name: str,
        initial_value: Any,
        data_type: StringDataType,
    ):
        el = ET.SubElement(parent, "StringParameterType")
        el.attrib["name"] = name
        if initial_value is not None:
            el.attrib["initialValue"] = str(initial_value)

        if data_type.encoding:
            self.add_data_encoding(el, data_type.encoding)

    def alarm_level_to_text(self, level: AlarmLevel):
        if level == AlarmLevel.NORMAL:
            return "normal"
        elif level == AlarmLevel.WATCH:
            return "watch"
        elif level == AlarmLevel.WARNING:
            return "warning"
        elif level == AlarmLevel.DISTRESS:
            return "distress"
        elif level == AlarmLevel.CRITICAL:
            return "critical"
        elif level == AlarmLevel.SEVERE:
            return "severe"
        else:
            raise Exception("Unexpected alarm level")

    def add_static_alarm_ranges(self, parent: ET.Element, alarm: ThresholdAlarm):
        ranges_el = ET.SubElement(parent, "StaticAlarmRanges")
        if alarm.watch_low is not None or alarm.watch_high is not None:
            range_el = ET.SubElement(ranges_el, "WatchRange")
            if alarm.watch_low is not None:
                if alarm.watch_low_exclusive:
                    range_el.attrib["minExclusive"] = str(alarm.watch_low)
                else:
                    range_el.attrib["minInclusive"] = str(alarm.watch_low)
            if alarm.watch_high is not None:
                if alarm.watch_high_exclusive:
                    range_el.attrib["maxExclusive"] = str(alarm.watch_high)
                else:
                    range_el.attrib["maxInclusive"] = str(alarm.watch_high)
        if alarm.warning_low is not None or alarm.warning_high is not None:
            range_el = ET.SubElement(ranges_el, "WarningRange")
            if alarm.warning_low is not None:
                if alarm.warning_low_exclusive:
                    range_el.attrib["minExclusive"] = str(alarm.warning_low)
                else:
                    range_el.attrib["minInclusive"] = str(alarm.warning_low)
            if alarm.warning_high is not None:
                if alarm.warning_high_exclusive:
                    range_el.attrib["maxExclusive"] = str(alarm.warning_high)
                else:
                    range_el.attrib["maxInclusive"] = str(alarm.warning_high)
        if alarm.distress_low is not None or alarm.distress_high is not None:
            range_el = ET.SubElement(ranges_el, "DistressRange")
            if alarm.distress_low is not None:
                if alarm.distress_low_exclusive:
                    range_el.attrib["minExclusive"] = str(alarm.distress_low)
                else:
                    range_el.attrib["minInclusive"] = str(alarm.distress_low)
            if alarm.distress_high is not None:
                if alarm.distress_high_exclusive:
                    range_el.attrib["maxExclusive"] = str(alarm.distress_high)
                else:
                    range_el.attrib["maxInclusive"] = str(alarm.distress_high)
        if alarm.critical_low is not None or alarm.critical_high is not None:
            range_el = ET.SubElement(ranges_el, "CriticalRange")
            if alarm.critical_low is not None:
                if alarm.critical_low_exclusive:
                    range_el.attrib["minExclusive"] = str(alarm.critical_low)
                else:
                    range_el.attrib["minInclusive"] = str(alarm.critical_low)
            if alarm.critical_high is not None:
                if alarm.critical_high_exclusive:
                    range_el.attrib["maxExclusive"] = str(alarm.critical_high)
                else:
                    range_el.attrib["maxInclusive"] = str(alarm.critical_high)
        if alarm.severe_low is not None or alarm.severe_high is not None:
            range_el = ET.SubElement(ranges_el, "SevereRange")
            if alarm.severe_low is not None:
                if alarm.severe_low_exclusive:
                    range_el.attrib["minExclusive"] = str(alarm.severe_low)
                else:
                    range_el.attrib["minInclusive"] = str(alarm.severe_low)
            if alarm.severe_high is not None:
                if alarm.severe_high_exclusive:
                    range_el.attrib["maxExclusive"] = str(alarm.severe_high)
                else:
                    range_el.attrib["maxInclusive"] = str(alarm.severe_high)

    def add_data_encoding(
        self,
        parent: ET.Element,
        encoding: DataEncoding,
        calibrator: Calibrator | None = None,
    ):
        if isinstance(encoding, FloatTimeEncoding):
            self.add_float_time_encoding(parent, encoding)
        elif isinstance(encoding, IntegerTimeEncoding):
            self.add_integer_time_encoding(parent, encoding)
        elif isinstance(encoding, BinaryDataEncoding):
            self.add_binary_data_encoding(parent, encoding)
        elif isinstance(encoding, IntegerDataEncoding):
            self.add_integer_data_encoding(parent, encoding, calibrator)
        elif isinstance(encoding, FloatDataEncoding):
            self.add_float_data_encoding(parent, encoding, calibrator)
        elif isinstance(encoding, StringDataEncoding):
            self.add_string_data_encoding(parent, encoding)
        else:
            raise Exception("Unexpected encoding")

    def add_binary_data_encoding(
        self, parent: ET.Element, encoding: BinaryDataEncoding
    ):
        el = ET.SubElement(parent, "BinaryDataEncoding")
        size_el = ET.SubElement(el, "SizeInBits")

        if encoding.bits is not None:
            fv_el = ET.SubElement(size_el, "FixedValue")
            fv_el.text = str(encoding.bits)
        else:
            # XTCE 1.2 enforces the use of either DynamicValue or DiscreteLookupList.
            # Use a special value recognized by Yamcs to work around this limitation.
            dyn_el = ET.SubElement(size_el, "DynamicValue")
            ref_el = ET.SubElement(dyn_el, "ParameterInstanceRef")
            ref_el.attrib["parameterRef"] = "_yamcs_ignore"

            # These are the ones that are really relevant
            if encoding.length_bits:
                if encoding.encoder:
                    raise ExportError(
                        "It is not possible to have both an encoder and a "
                        "leading-size binary"
                    )
                if encoding.decoder:
                    raise ExportError(
                        "It is not possible to have both a decoder and a "
                        "leading-size binary"
                    )

                algo_el = ET.SubElement(el, "FromBinaryTransformAlgorithm")
                algo_el.attrib["name"] = "LeadingSizeBinaryDecoder"
                text_el = ET.SubElement(algo_el, "AlgorithmText")
                text_el.attrib["language"] = "Java"
                text_el.text = (
                    f"org.yamcs.algo.LeadingSizeBinaryDecoder({encoding.length_bits})"
                )
                algo_el = ET.SubElement(el, "ToBinaryTransformAlgorithm")
                algo_el.attrib["name"] = "LeadingSizeBinaryEncoder"
                text_el = ET.SubElement(algo_el, "AlgorithmText")
                text_el.attrib["language"] = "Java"
                text_el.text = (
                    f"org.yamcs.algo.LeadingSizeBinaryEncoder({encoding.length_bits})"
                )

        if encoding.decoder:
            self.add_input_only_algorithm(
                el, "FromBinaryTransformAlgorithm", encoding.decoder
            )

        if encoding.encoder:
            self.add_input_only_algorithm(
                el, "ToBinaryTransformAlgorithm", encoding.encoder
            )

    def add_input_only_algorithm(
        self, parent: ET.Element, tag: str, algorithm: JavaAlgorithm
    ):
        el = ET.SubElement(parent, tag)
        if isinstance(algorithm, JavaAlgorithm):
            el.attrib["name"] = algorithm.java.replace(".", "_")
            if algorithm.extra:
                self.add_ancillary_data(el, algorithm.extra)
            text_el = ET.SubElement(el, "AlgorithmText")
            text_el.attrib["language"] = "Java"
            text_el.text = algorithm.java

            if algorithm.inputs:
                inputset_el = ET.SubElement(el, "InputSet")
                for input in algorithm.inputs:
                    ref_el = ET.SubElement(inputset_el, "InputParameterInstanceRef")
                    ref_el.attrib["parameterRef"] = input.parameter.qualified_name
                    if input.name:
                        ref_el.attrib["inputName"] = input.name
        else:
            raise Exception("Unexpected algorithm type")

    def add_string_data_encoding(
        self, parent: ET.Element, encoding: StringDataEncoding
    ):
        el = ET.SubElement(parent, "StringDataEncoding")

        if encoding.charset == Charset.US_ASCII:
            el.attrib["encoding"] = "US-ASCII"
        elif encoding.charset == Charset.ISO_8859_1:
            el.attrib["encoding"] = "ISO-8859-1"
        elif encoding.charset == Charset.WINDOWS_1252:
            el.attrib["encoding"] = "Windows-1252"
        elif encoding.charset == Charset.UTF_8:
            el.attrib["encoding"] = "UTF-8"
        elif encoding.charset == Charset.UTF_16:
            el.attrib["encoding"] = "UTF-16"
        elif encoding.charset == Charset.UTF_16LE:
            el.attrib["encoding"] = "UTF-16LE"
        elif encoding.charset == Charset.UTF_16BE:
            el.attrib["encoding"] = "UTF-16BE"
        elif encoding.charset == Charset.UTF_32:
            el.attrib["encoding"] = "UTF-32"
        elif encoding.charset == Charset.UTF_32LE:
            el.attrib["encoding"] = "UTF-32LE"
        elif encoding.charset == Charset.UTF_32BE:
            el.attrib["encoding"] = "UTF-32BE"
        else:
            raise Exception(f"Unexpected charset {encoding.charset}")

        if encoding.bits is not None:
            size_el = ET.SubElement(el, "SizeInBits")
            fixed_el = ET.SubElement(size_el, "Fixed")
            fv_el = ET.SubElement(fixed_el, "FixedValue")
            fv_el.text = str(encoding.bits)
            if encoding.length_bits:
                lsize_el = ET.SubElement(size_el, "LeadingSize")
                lsize_el.attrib["sizeInBitsOfSizeTag"] = str(encoding.length_bits)
            if encoding.termination is not None:
                termination_el = ET.SubElement(size_el, "TerminationChar")
                termination_el.text = hexlify(encoding.termination).decode("ascii")
        else:
            var_el = ET.SubElement(el, "Variable")
            var_el.attrib["maxSizeInBits"] = str(encoding.max_bits)  # Required

            # XTCE 1.2 enforces the use of either DynamicValue or DiscreteLookupList.
            # Use a special value recognized by Yamcs to work around this limitation.
            dyn_el = ET.SubElement(var_el, "DynamicValue")
            ref_el = ET.SubElement(dyn_el, "ParameterInstanceRef")
            ref_el.attrib["parameterRef"] = "_yamcs_ignore"

            # These are the ones that are really relevant
            if encoding.length_bits:
                lsize_el = ET.SubElement(var_el, "LeadingSize")
                lsize_el.attrib["sizeInBitsOfSizeTag"] = str(encoding.length_bits)
            if encoding.termination is not None:
                termination_el = ET.SubElement(var_el, "TerminationChar")
                termination_el.text = hexlify(encoding.termination).decode("ascii")

    def add_float_time_encoding(self, parent: ET.Element, encoding: FloatTimeEncoding):
        el = ET.SubElement(parent, "Encoding")
        el.attrib["offset"] = str(encoding.offset)
        el.attrib["scale"] = str(encoding.scale)
        el.attrib["units"] = "seconds"
        self.add_float_data_encoding(el, encoding, calibrator=None)

    def add_integer_time_encoding(
        self, parent: ET.Element, encoding: IntegerTimeEncoding
    ):
        el = ET.SubElement(parent, "Encoding")
        el.attrib["offset"] = str(encoding.offset)
        el.attrib["scale"] = str(encoding.scale)
        el.attrib["units"] = "seconds"
        self.add_integer_data_encoding(el, encoding, calibrator=None)

    def add_integer_data_encoding(
        self,
        parent: ET.Element,
        encoding: IntegerDataEncoding,
        calibrator: Calibrator | None,
    ):
        el = ET.SubElement(parent, "IntegerDataEncoding")
        el.attrib["sizeInBits"] = str(encoding.bits)

        if encoding.scheme == IntegerDataEncodingScheme.UNSIGNED:
            el.attrib["encoding"] = "unsigned"
        elif encoding.scheme == IntegerDataEncodingScheme.SIGN_MAGNITUDE:
            el.attrib["encoding"] = "signMagnitude"
        elif encoding.scheme == IntegerDataEncodingScheme.TWOS_COMPLEMENT:
            el.attrib["encoding"] = "twosComplement"
        elif encoding.scheme == IntegerDataEncodingScheme.ONES_COMPLEMENT:
            el.attrib["encoding"] = "onesComplement"

        if (encoding.bits is not None) and (encoding.bits > 8):
            if encoding.byte_order == ByteOrder.BIG_ENDIAN:
                el.attrib["byteOrder"] = "mostSignificantByteFirst"
            elif encoding.byte_order == ByteOrder.LITTLE_ENDIAN:
                el.attrib["byteOrder"] = "leastSignificantByteFirst"

        if calibrator:
            self.add_calibrator(el, calibrator)

    def add_float_data_encoding(
        self,
        parent: ET.Element,
        encoding: FloatDataEncoding,
        calibrator: Calibrator | None,
    ):
        el = ET.SubElement(parent, "FloatDataEncoding")
        el.attrib["sizeInBits"] = str(encoding.bits)

        if encoding.scheme == FloatDataEncodingScheme.IEEE754_1985:
            el.attrib["encoding"] = "IEEE754_1985"
        elif encoding.scheme == FloatDataEncodingScheme.MILSTD_1750A:
            el.attrib["encoding"] = "MILSTD_1750A"

        if encoding.byte_order == ByteOrder.BIG_ENDIAN:
            el.attrib["byteOrder"] = "mostSignificantByteFirst"
        elif encoding.byte_order == ByteOrder.LITTLE_ENDIAN:
            el.attrib["byteOrder"] = "leastSignificantByteFirst"

        if calibrator:
            self.add_calibrator(el, calibrator)

    def add_calibrator(self, parent: ET.Element, calibrator: Calibrator):
        el = ET.SubElement(parent, "DefaultCalibrator")
        if isinstance(calibrator, Polynomial):
            poly_el = ET.SubElement(el, "PolynomialCalibrator")
            for idx, coef in enumerate(calibrator.coefficients):
                term_el = ET.SubElement(poly_el, "Term")
                term_el.attrib["coefficient"] = str(coef)
                term_el.attrib["exponent"] = str(idx)
        elif isinstance(calibrator, Interpolate):
            spline_el = ET.SubElement(el, "SplineCalibrator")
            for idx, x in enumerate(calibrator.xp):
                point_el = ET.SubElement(spline_el, "SplinePoint")
                point_el.attrib["raw"] = str(x)
                point_el.attrib["calibrated"] = str(calibrator.fp[idx])
        else:
            raise ExportError(f"Unexpected calibrator {calibrator.__class__}")

    def add_enumeration_list(self, parent: ET.Element, choices: Choices):
        el = ET.SubElement(parent, "EnumerationList")
        if isinstance(choices, list):
            for choice in choices:
                enumeration_el = ET.SubElement(el, "Enumeration")
                enumeration_el.attrib["value"] = str(choice[0])
                enumeration_el.attrib["label"] = choice[1]
                if len(choice) > 2:
                    typeless_choice = cast(Any, choice)
                    enumeration_el.attrib["shortDescription"] = typeless_choice[2]
        else:
            for choice in choices:
                enumeration_el = ET.SubElement(el, "Enumeration")
                enumeration_el.attrib["value"] = str(choice.value)
                enumeration_el.attrib["label"] = choice.name

    def add_parameter_set(self, parent: ET.Element, system: System):
        if not system.parameters:
            return

        el = ET.SubElement(parent, "ParameterSet")
        for parameter in system.parameters:
            parameter_el = ET.SubElement(el, "Parameter")
            parameter_el.attrib["name"] = parameter.name
            parameter_el.attrib["parameterTypeRef"] = parameter.name

            if parameter.short_description:
                parameter_el.attrib["shortDescription"] = parameter.short_description

            if parameter.long_description:
                ET.SubElement(parameter_el, "LongDescription").text = (
                    parameter.long_description
                )

            if parameter.aliases:
                self.add_aliases(parameter_el, parameter.aliases)

            if parameter.extra:
                self.add_ancillary_data(el, parameter.extra)

            props_el = ET.SubElement(parameter_el, "ParameterProperties")
            if parameter.data_source == DataSource.TELEMETERED:
                props_el.attrib["dataSource"] = "telemetered"
            elif parameter.data_source == DataSource.DERIVED:
                props_el.attrib["dataSource"] = "derived"
            elif parameter.data_source == DataSource.CONSTANT:
                props_el.attrib["dataSource"] = "constant"
            elif parameter.data_source == DataSource.LOCAL:
                props_el.attrib["dataSource"] = "local"
            elif parameter.data_source == DataSource.GROUND:
                props_el.attrib["dataSource"] = "ground"
            else:
                raise ExportError(f"Unexpected data source {parameter.data_source}")

            props_el.attrib["persistence"] = "true" if parameter.persistent else "false"

    def add_container_set(self, parent: ET.Element, system: System):
        if not system.containers:
            return

        el = ET.SubElement(parent, "ContainerSet")
        for container in system.containers:
            self.add_sequence_container(el, container)

    def add_sequence_container(self, parent: ET.Element, container: Container):
        el = ET.SubElement(parent, "SequenceContainer")
        el.attrib["name"] = container.name
        el.attrib["abstract"] = _to_xml_value(container.abstract)

        if container.short_description:
            el.attrib["shortDescription"] = container.short_description

        if container.long_description:
            ET.SubElement(el, "LongDescription").text = container.long_description

        if container.aliases:
            self.add_aliases(el, container.aliases)

        extra = dict(container.extra)
        if container.hint_partition:
            extra["Yamcs"] = "UseAsArchivingPartition"

        if extra:
            self.add_ancillary_data(el, extra)

        if container.bits is not None:
            encoding_el = ET.SubElement(el, "BinaryEncoding")
            size_el = ET.SubElement(encoding_el, "SizeInBits")
            fv_el = ET.SubElement(size_el, "FixedValue")
            fv_el.text = str(container.bits)

        self.add_packet_entry_list(el, container)

    def add_expression_condition(
        self,
        parent: ET.Element,
        system: System,
        expression: Expression,
    ):
        if isinstance(expression, EqExpression):
            self.add_condition(
                parent,
                system,
                expression.ref,
                expression.value,
                "==",
                expression.calibrated,
            )
        elif isinstance(expression, NeExpression):
            self.add_condition(
                parent,
                system,
                expression.ref,
                expression.value,
                "!=",
                expression.calibrated,
            )
        elif isinstance(expression, LtExpression):
            self.add_condition(
                parent,
                system,
                expression.ref,
                expression.value,
                "<",
                expression.calibrated,
            )
        elif isinstance(expression, LteExpression):
            self.add_condition(
                parent,
                system,
                expression.ref,
                expression.value,
                "<=",
                expression.calibrated,
            )
        elif isinstance(expression, GtExpression):
            self.add_condition(
                parent,
                system,
                expression.ref,
                expression.value,
                ">",
                expression.calibrated,
            )
        elif isinstance(expression, GteExpression):
            self.add_condition(
                parent,
                system,
                expression.ref,
                expression.value,
                ">=",
                expression.calibrated,
            )
        elif isinstance(expression, AndExpression):
            el = ET.SubElement(parent, "ANDedConditions")
            for expression in expression.expressions:
                self.add_expression_condition(el, system, expression)
        elif isinstance(expression, OrExpression):
            el = ET.SubElement(parent, "ORedConditions")
            for expression in expression.expressions:
                self.add_expression_condition(el, system, expression)
        else:
            raise Exception(f"Unexpected expression condition {expression.__class__}")

    def add_condition(
        self,
        parent: ET.Element,
        system: System,
        ref: Parameter | ParameterMember,
        value: Any,
        operator: str,
        calibrated: bool,
    ):
        condition_el = ET.SubElement(parent, "Condition")

        pref_el = ET.SubElement(condition_el, "ParameterInstanceRef")
        data_type: DataType
        if isinstance(ref, Parameter):
            data_type = ref
            pref_el.attrib["parameterRef"] = self.make_ref(
                ref.qualified_name,
                start=system,
            )
        else:  # ParameterMember
            data_type = ref.path[-1]
            parameter_ref = self.make_ref(
                ref.parameter.qualified_name,
                start=system,
            )
            for member in ref.path:
                parameter_ref += "/" + member.name
            pref_el.attrib["parameterRef"] = parameter_ref
        pref_el.attrib["useCalibratedValue"] = _to_xml_value(calibrated)

        ET.SubElement(condition_el, "ComparisonOperator").text = operator
        val_el = ET.SubElement(condition_el, "Value")

        val_el.text = _to_xml_value(value)
        if isinstance(data_type, BooleanDataType) and isinstance(value, bool):
            if value:
                val_el.text = data_type.one_string_value
            else:
                val_el.text = data_type.zero_string_value
        elif isinstance(data_type, EnumeratedDataType) and isinstance(value, int):
            if value:
                val_el.text = data_type.label_for(value)

    def add_packet_entry_list(self, parent: ET.Element, container: Container):
        el = ET.SubElement(parent, "EntryList")
        for entry in container.entries:
            if isinstance(entry, ParameterEntry):
                self.add_parameter_ref_entry(el, container, entry)
            elif isinstance(entry, ContainerEntry):
                self.add_container_ref_entry(el, container, entry)
            else:
                raise ExportError(f"Unexpected entry {entry.__class__}")

        if container.parent:
            self.add_base_container(parent, container.parent, container)

    def add_parameter_ref_entry(
        self,
        parent: ET.Element,
        container: Container,
        entry: ParameterEntry,
    ):
        el = ET.SubElement(parent, "ParameterRefEntry")
        el.attrib["parameterRef"] = self.make_ref(
            entry.parameter.qualified_name,
            start=container.system,
        )
        if entry.short_description:
            el.attrib["shortDescription"] = entry.short_description

        loc_el = ET.SubElement(el, "LocationInContainerInBits")

        if entry.reference_location == ReferenceLocation.PREVIOUS_ENTRY:
            loc_el.attrib["referenceLocation"] = "previousEntry"
        elif entry.reference_location == ReferenceLocation.CONTAINER_START:
            loc_el.attrib["referenceLocation"] = "containerStart"
        else:
            raise Exception("Unexpected reference location")

        fv_el = ET.SubElement(loc_el, "FixedValue")
        fv_el.text = str(entry.location_in_bits)

        if entry.include_condition:
            cond_el = ET.SubElement(el, "IncludeCondition")
            expr_el = ET.SubElement(cond_el, "BooleanExpression")
            self.add_expression_condition(
                expr_el,
                system=container.system,
                expression=entry.include_condition,
            )

    def add_container_ref_entry(
        self,
        parent: ET.Element,
        container: Container,
        entry: ContainerEntry,
    ):
        el = ET.SubElement(parent, "ContainerRefEntry")
        el.attrib["containerRef"] = self.make_ref(
            entry.container.qualified_name,
            start=container.system,
        )
        if entry.short_description:
            el.attrib["shortDescription"] = entry.short_description

        loc_el = ET.SubElement(el, "LocationInContainerInBits")

        if entry.reference_location == ReferenceLocation.PREVIOUS_ENTRY:
            loc_el.attrib["referenceLocation"] = "previousEntry"
        elif entry.reference_location == ReferenceLocation.CONTAINER_START:
            loc_el.attrib["referenceLocation"] = "containerStart"
        else:
            raise Exception("Unexpected reference location")

        fv_el = ET.SubElement(loc_el, "FixedValue")
        fv_el.text = str(entry.location_in_bits)

        if entry.include_condition:
            cond_el = ET.SubElement(el, "IncludeCondition")
            expr_el = ET.SubElement(cond_el, "BooleanExpression")
            self.add_expression_condition(
                expr_el,
                system=container.system,
                expression=entry.include_condition,
            )

    def make_ref(self, target: str, start: System):
        if os.path.commonprefix([target, start.qualified_name]) == "/":
            return target  # abs path
        else:
            return os.path.relpath(target, start=start.qualified_name)

    def add_base_container(
        self,
        parent: ET.Element,
        base_container: Container,
        container: Container,
    ):
        el = ET.SubElement(parent, "BaseContainer")

        el.attrib["containerRef"] = self.make_ref(
            base_container.qualified_name,
            start=container.system,
        )

        if container.restriction_criteria:
            criteria_el = ET.SubElement(el, "RestrictionCriteria")
            expr_el = ET.SubElement(criteria_el, "BooleanExpression")
            self.add_expression_condition(
                expr_el,
                system=container.system,
                expression=container.restriction_criteria,
            )

    def add_space_systems(self, parent: ET.Element, system: System):
        for subsystem in system.subsystems:
            self.generate_space_system(subsystem, parent)

    def generate_space_system(
        self,
        system: System,
        parent: ET.Element | None = None,
        add_schema_location: bool = False,
    ):
        if not parent:
            el = ET.Element("SpaceSystem")
            el.attrib["xmlns"] = "http://www.omg.org/spec/XTCE/20180204"
            if add_schema_location:
                el.attrib["xmlns:xsi"] = "http://www.w3.org/2001/XMLSchema-instance"
                el.attrib["xsi:schemaLocation"] = "{} {}".format(
                    "http://www.omg.org/spec/XTCE/20180204",
                    "https://www.omg.org/spec/XTCE/20180204/SpaceSystem.xsd",
                )
        else:
            el = ET.SubElement(parent, "SpaceSystem")

        el.attrib["name"] = system.name

        if system.short_description:
            el.attrib["shortDescription"] = system.short_description

        if system.long_description:
            ET.SubElement(el, "LongDescription").text = system.long_description

        if system.aliases:
            self.add_aliases(el, system.aliases)

        if system.extra:
            self.add_ancillary_data(el, system.extra)

        self.add_telemetry_metadata(el, system)
        self.add_command_metadata(el, system)
        self.add_space_systems(el, system)
        return el
