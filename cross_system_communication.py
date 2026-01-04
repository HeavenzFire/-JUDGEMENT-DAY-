#!/usr/bin/env python3
"""
Cross-System Communication Module
Enables seamless communication and data exchange between all connected systems.
"""

import logging
import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from master_orchestrator import orchestrator

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Types of messages that can be exchanged between systems."""
    HEALTH_STATUS = "health_status"
    DATA_REQUEST = "data_request"
    DATA_RESPONSE = "data_response"
    EVENT_NOTIFICATION = "event_notification"
    COMMAND_EXECUTION = "command_execution"
    SYSTEM_ALERT = "system_alert"
    COORDINATION_SIGNAL = "coordination_signal"
    SYNCHRONIZATION_PULSE = "synchronization_pulse"

@dataclass
class SystemMessage:
    """Structured message for inter-system communication."""
    message_id: str
    from_system: str
    to_system: str
    message_type: MessageType
    payload: Any
    timestamp: float
    priority: int = 1  # 1=low, 5=high
    correlation_id: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert message to dictionary for serialization."""
        return {
            "message_id": self.message_id,
            "from_system": self.from_system,
            "to_system": self.to_system,
            "message_type": self.message_type.value,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "priority": self.priority,
            "correlation_id": self.correlation_id
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'SystemMessage':
        """Create message from dictionary."""
        return cls(
            message_id=data["message_id"],
            from_system=data["from_system"],
            to_system=data["to_system"],
            message_type=MessageType(data["message_type"]),
            payload=data["payload"],
            timestamp=data["timestamp"],
            priority=data.get("priority", 1),
            correlation_id=data.get("correlation_id")
        )

class CommunicationHub:
    """Central hub for cross-system communication."""

    def __init__(self):
        self.message_handlers: Dict[MessageType, List[callable]] = {}
        self.pending_responses: Dict[str, SystemMessage] = {}
        self.message_history: List[SystemMessage] = []
        self.max_history = 1000

        # Register default handlers
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default message handlers."""
        self.register_handler(MessageType.HEALTH_STATUS, self._handle_health_status)
        self.register_handler(MessageType.DATA_REQUEST, self._handle_data_request)
        self.register_handler(MessageType.EVENT_NOTIFICATION, self._handle_event_notification)
        self.register_handler(MessageType.SYSTEM_ALERT, self._handle_system_alert)

    def register_handler(self, message_type: MessageType, handler: callable):
        """Register a handler for a specific message type."""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)
        logger.info(f"Registered handler for {message_type.value}")

    def send_message(self, message: SystemMessage) -> bool:
        """Send a message to the target system."""
        try:
            # Add to history
            self.message_history.append(message)
            if len(self.message_history) > self.max_history:
                self.message_history.pop(0)

            # Route to target system
            target_system = orchestrator.systems.get(message.to_system)
            if target_system and target_system.instance:
                if hasattr(target_system.instance, 'receive_message'):
                    target_system.instance.receive_message(message)
                    logger.debug(f"Message {message.message_id} sent to {message.to_system}")
                    return True
                else:
                    logger.warning(f"System {message.to_system} does not support message receiving")
            else:
                logger.warning(f"Target system {message.to_system} not found or not initialized")

            return False

        except Exception as e:
            logger.error(f"Error sending message {message.message_id}: {e}")
            return False

    def broadcast_message(self, message: SystemMessage, exclude_systems: List[str] = None) -> int:
        """Broadcast message to all systems except excluded ones."""
        if exclude_systems is None:
            exclude_systems = []

        sent_count = 0
        for system_name in orchestrator.systems:
            if system_name not in exclude_systems:
                message_copy = SystemMessage(
                    message_id=f"{message.message_id}_broadcast_{system_name}",
                    from_system=message.from_system,
                    to_system=system_name,
                    message_type=message.message_type,
                    payload=message.payload,
                    timestamp=time.time(),
                    priority=message.priority,
                    correlation_id=message.correlation_id
                )
                if self.send_message(message_copy):
                    sent_count += 1

        logger.info(f"Broadcast message sent to {sent_count} systems")
        return sent_count

    def request_data(self, from_system: str, to_system: str, data_type: str, parameters: Dict = None) -> Optional[str]:
        """Request data from another system."""
        if parameters is None:
            parameters = {}

        message_id = f"data_req_{from_system}_{to_system}_{int(time.time())}"

        message = SystemMessage(
            message_id=message_id,
            from_system=from_system,
            to_system=to_system,
            message_type=MessageType.DATA_REQUEST,
            payload={
                "data_type": data_type,
                "parameters": parameters
            },
            timestamp=time.time(),
            priority=2
        )

        if self.send_message(message):
            self.pending_responses[message_id] = message
            return message_id
        return None

    def respond_to_request(self, original_message: SystemMessage, response_data: Any):
        """Respond to a data request."""
        response_message = SystemMessage(
            message_id=f"resp_{original_message.message_id}",
            from_system=original_message.to_system,
            to_system=original_message.from_system,
            message_type=MessageType.DATA_RESPONSE,
            payload=response_data,
            timestamp=time.time(),
            priority=original_message.priority,
            correlation_id=original_message.message_id
        )

        self.send_message(response_message)

    def send_alert(self, from_system: str, alert_type: str, alert_data: Dict):
        """Send a system alert to all systems."""
        message = SystemMessage(
            message_id=f"alert_{from_system}_{int(time.time())}",
            from_system=from_system,
            to_system="all",
            message_type=MessageType.SYSTEM_ALERT,
            payload={
                "alert_type": alert_type,
                "data": alert_data
            },
            timestamp=time.time(),
            priority=4
        )

        self.broadcast_message(message, exclude_systems=[from_system])

    def get_message_history(self, system_name: str = None, message_type: MessageType = None,
                          limit: int = 100) -> List[SystemMessage]:
        """Get message history with optional filtering."""
        messages = self.message_history

        if system_name:
            messages = [m for m in messages if m.from_system == system_name or m.to_system == system_name]

        if message_type:
            messages = [m for m in messages if m.message_type == message_type]

        return messages[-limit:]

    def _handle_health_status(self, message: SystemMessage):
        """Handle health status messages."""
        health_data = message.payload
        logger.info(f"Received health status from {message.from_system}: {health_data}")

        # Store health data for monitoring
        # This could be extended to trigger alerts or actions based on health

    def _handle_data_request(self, message: SystemMessage):
        """Handle data request messages."""
        request_data = message.payload
        data_type = request_data.get("data_type")
        parameters = request_data.get("parameters", {})

        logger.info(f"Data request from {message.from_system}: {data_type}")

        # This would typically be handled by the target system's specific logic
        # For now, we'll just acknowledge the request

    def _handle_event_notification(self, message: SystemMessage):
        """Handle event notification messages."""
        event_data = message.payload
        logger.info(f"Event notification from {message.from_system}: {event_data}")

    def _handle_system_alert(self, message: SystemMessage):
        """Handle system alert messages."""
        alert_data = message.payload
        alert_type = alert_data.get("alert_type")
        logger.warning(f"System alert from {message.from_system}: {alert_type} - {alert_data}")

class DataExchangeProtocol:
    """Protocol for structured data exchange between systems."""

    def __init__(self, communication_hub: CommunicationHub):
        self.communication_hub = communication_hub
        self.data_providers: Dict[str, callable] = {}
        self.data_consumers: Dict[str, List[callable]] = {}

    def register_data_provider(self, data_type: str, provider_function: callable):
        """Register a function that can provide specific data."""
        self.data_providers[data_type] = provider_function
        logger.info(f"Registered data provider for {data_type}")

    def register_data_consumer(self, data_type: str, consumer_function: callable):
        """Register a function that consumes specific data."""
        if data_type not in self.data_consumers:
            self.data_consumers[data_type] = []
        self.data_consumers[data_type].append(consumer_function)
        logger.info(f"Registered data consumer for {data_type}")

    def request_data(self, from_system: str, data_type: str, parameters: Dict = None) -> Any:
        """Request data through the protocol."""
        if data_type in self.data_providers:
            try:
                data = self.data_providers[data_type](parameters or {})
                logger.info(f"Data provided for {data_type} by {from_system}")
                return data
            except Exception as e:
                logger.error(f"Error providing data {data_type}: {e}")
                return None
        else:
            logger.warning(f"No provider available for data type {data_type}")
            return None

    def publish_data(self, from_system: str, data_type: str, data: Any):
        """Publish data to all registered consumers."""
        if data_type in self.data_consumers:
            for consumer in self.data_consumers[data_type]:
                try:
                    consumer(from_system, data)
                    logger.debug(f"Data {data_type} consumed by function")
                except Exception as e:
                    logger.error(f"Error in data consumer: {e}")

# Global instances
communication_hub = CommunicationHub()
data_exchange = DataExchangeProtocol(communication_hub)

def initialize_communication():
    """Initialize the communication system."""
    logger.info("Initializing cross-system communication")

    # Register default data providers
    data_exchange.register_data_provider("system_status", lambda params: orchestrator.get_system_status())
    data_exchange.register_data_provider("system_info", lambda params: orchestrator.get_system_info())

    # Register default data consumers
    data_exchange.register_data_consumer("health_data", lambda from_sys, data: logger.info(f"Health data from {from_sys}: {data}"))
    data_exchange.register_data_consumer("distress_alert", lambda from_sys, data: logger.warning(f"Distress alert from {from_sys}: {data}"))

    logger.info("Cross-system communication initialized")

if __name__ == "__main__":
    initialize_communication()

    # Example usage
    # Create a test message
    test_message = SystemMessage(
        message_id="test_msg_001",
        from_system="test_system",
        to_system="guardian_angel",
        message_type=MessageType.EVENT_NOTIFICATION,
        payload={"event": "test_event", "data": "test_data"},
        timestamp=time.time()
    )

    # Send the message
    communication_hub.send_message(test_message)