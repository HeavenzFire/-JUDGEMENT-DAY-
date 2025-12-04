"""
Semantic Ontology for Capability Expression
==========================================

This module defines the ontology format for expressing what services can do,
enabling semantic communication beyond rigid API schemas.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class DataType(Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"
    BINARY = "binary"


class ProtocolType(Enum):
    REQUEST_RESPONSE = "request_response"
    STREAMING = "streaming"
    EVENT_DRIVEN = "event_driven"
    NEGOTIATED = "negotiated"


@dataclass
class DataSchema:
    """Schema for data inputs/outputs"""
    type: DataType
    description: str
    required: bool = True
    constraints: Optional[Dict[str, Any]] = None


@dataclass
class Capability:
    """
    A capability represents what a service can do semantically.

    Instead of endpoints like "GET /weather", we express:
    "I can provide weather information for a given location"
    """
    id: str
    name: str
    description: str
    domain: str  # e.g., "weather", "notification", "data_processing"
    inputs: List[DataSchema]
    outputs: List[DataSchema]
    constraints: Dict[str, Any]  # rate limits, costs, requirements
    protocols_supported: List[ProtocolType]
    semantic_tags: List[str]  # for discovery: ["real_time", "forecast", "alerts"]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "domain": self.domain,
            "inputs": [
                {
                    "type": inp.type.value,
                    "description": inp.description,
                    "required": inp.required,
                    "constraints": inp.constraints
                } for inp in self.inputs
            ],
            "outputs": [
                {
                    "type": out.type.value,
                    "description": out.description,
                    "required": out.required,
                    "constraints": out.constraints
                } for out in self.outputs
            ],
            "constraints": self.constraints,
            "protocols_supported": [p.value for p in self.protocols_supported],
            "semantic_tags": self.semantic_tags
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Capability':
        """Create from dictionary"""
        return cls(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            domain=data["domain"],
            inputs=[
                DataSchema(
                    type=DataType(inp["type"]),
                    description=inp["description"],
                    required=inp.get("required", True),
                    constraints=inp.get("constraints")
                ) for inp in data["inputs"]
            ],
            outputs=[
                DataSchema(
                    type=DataType(out["type"]),
                    description=out["description"],
                    required=out.get("required", True),
                    constraints=out.get("constraints")
                ) for out in data["outputs"]
            ],
            constraints=data["constraints"],
            protocols_supported=[ProtocolType(p) for p in data["protocols_supported"]],
            semantic_tags=data["semantic_tags"]
        )


@dataclass
class Intent:
    """
    An intent represents what a service wants to accomplish.

    Instead of calling "POST /notify", we express:
    "I want to inform the user about this weather alert"
    """
    id: str
    description: str
    required_capabilities: List[str]  # capability IDs needed
    context: Dict[str, Any]  # additional context for negotiation
    priority: int = 1  # 1-10, higher = more urgent

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "required_capabilities": self.required_capabilities,
            "context": self.context,
            "priority": self.priority
        }


@dataclass
class NegotiationResult:
    """
    Result of protocol negotiation between services
    """
    protocol: ProtocolType
    transformation_rules: Dict[str, Any]  # how to adapt data
    agreed_constraints: Dict[str, Any]
    session_id: str
    expires_at: Optional[float] = None  # timestamp