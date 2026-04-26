from dataclasses import dataclass
from enum import Enum, auto
from typing import Literal

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
    supported_port_types_for_inheritance: list[PortType | Literal["FullySupportedSignalValueType.Any"]] | None = None
    inheritance_group: int = 0 # Ports with the same inheritance group within a block inherit at the same time, their types are the same
    
    def to_dict(self):
        base = {
            "port_category": self.port_category.value,
            "inheritance_group": self.inheritance_group,
        }

        if self.port_category == PortCategory.fully_supported_signal_value:
            base["signal_value_type"] = (
                self.signal_value_type.value if self.signal_value_type else None
            )

        elif self.port_category == PortCategory.enumeration:
            base["enumeration_name"] = self.enumeration_name

        elif self.port_category == PortCategory.structure:
            base["structure_name"] = self.structure_name

        elif self.port_category == PortCategory.pointer_to_object:
            base["pointing_object_class_name"] = self.pointing_object_class_name

        elif self.port_category == PortCategory.other_type:
            base["other_type_name"] = self.other_type_name

        elif self.port_category == PortCategory.inherited: 
            base["supported_port_types_for_inheritance"] = [x.to_dict() if isinstance(x, PortType) else x for x in self.supported_port_types_for_inheritance] if self.supported_port_types_for_inheritance else None
        
        print(f"PortType to_dict output: {base}")
        return base
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            port_category=PortCategory(data.get("port_category")),
            signal_value_type=FullySupportedSignalValueType(data.get("signal_value_type")) if data.get("signal_value_type") else None,
            enumeration_name=data.get("enumeration_name"),
            structure_name=data.get("structure_name"),
            pointing_object_class_name=data.get("pointing_object_class_name"),
            other_type_name=data.get("other_type_name"),
            supported_port_types_for_inheritance=[
                PortType.from_dict(sub_data) if isinstance(sub_data, dict) else sub_data for sub_data in data.get("supported_port_types_for_inheritance", [])
            ] if data.get("supported_port_types_for_inheritance") else None,
            inheritance_group=data.get("inheritance_group", 0)
        )

@dataclass
class PortTypeConfig:
    port_category: str = "FullySupportedSignalValue"
    signal_value_type: str | None = None
    enumeration_name: str | None = None
    structure_name: str | None = None
    pointing_object_class_name: str | None = None
    other_type_name: str | None = None
    supported_port_types_for_inheritance: list[PortTypeConfig | Literal["FullySupportedSignalValueType.Any"]] | None = None

    # @classmethod
    # def from_dic


