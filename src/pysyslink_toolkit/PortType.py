from dataclasses import dataclass
from enum import Enum, auto

class FullySupportedSignalValueType(Enum):
    Int = "int"
    Double = "double"
    Bool = "bool"
    ComplexDouble = "complex_double"
    String = "string"

class PortCategory(Enum):
    fully_supported_signal_value = "FullySupportedSignalValue"
    enumeration = "Enumeration"
    structure = "Structure"
    pointer_to_object = "PointerToObject"
    other_type = "OtherType"
    inherited = "Inherited"
    unknown = "Unknown"

@dataclass
class PortType:
    port_category: PortCategory = PortCategory.fully_supported_signal_value
    signal_value_type: FullySupportedSignalValueType | None = None
    enumeration_name: str | None = None
    structure_name: str | None = None
    pointing_object_class_name: str | None = None
    other_type_name: str | None = None
    supported_port_types_for_inheritance: list[PortType] | None = None

@dataclass
class PortTypeConfig:
    port_category: str = "FullySupportedSignalValue"
    signal_value_type: str | None = None
    enumeration_name: str | None = None
    structure_name: str | None = None
    pointing_object_class_name: str | None = None
    other_type_name: str | None = None
    supported_port_types_for_inheritance: list[PortTypeConfig] | None = None



