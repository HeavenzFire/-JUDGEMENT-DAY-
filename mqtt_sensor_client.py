#!/usr/bin/env python3
"""
MQTT Sensor Client for Syntropic Child Protection System

This module connects to an MQTT broker and receives sensor data from distributed sensors.
It processes incoming messages and forwards them to the anomaly detection system.
"""

import paho.mqtt.client as mqtt
import json
import logging
import time
from typing import Callable, Dict, Any
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MQTTSensorClient:
    """
    MQTT client for receiving sensor data from distributed sensors.
    """

    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883,
                 client_id: str = "syntropic_monitor", topics: list = None):
        """
        Initialize the MQTT sensor client.

        Args:
            broker_host: MQTT broker hostname
            broker_port: MQTT broker port
            client_id: Unique client identifier
            topics: List of MQTT topics to subscribe to
        """
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client_id = client_id
        self.topics = topics or ["sensors/temperature", "sensors/motion", "sensors/sound"]
        self.client = None
        self.connected = False
        self.data_callback = None
        self.running = False

    def on_connect(self, client, userdata, flags, rc):
        """Callback for when the client receives a CONNACK response from the server."""
        if rc == 0:
            logger.info(f"Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            self.connected = True
            # Subscribe to all topics
            for topic in self.topics:
                client.subscribe(topic)
                logger.info(f"Subscribed to topic: {topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker. Return code: {rc}")

    def on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the server."""
        logger.warning(f"Disconnected from MQTT broker. Return code: {rc}")
        self.connected = False

    def on_message(self, client, userdata, msg):
        """Callback for when a PUBLISH message is received from the server."""
        try:
            # Parse JSON payload
            payload = json.loads(msg.payload.decode('utf-8'))

            # Add metadata
            sensor_data = {
                'topic': msg.topic,
                'timestamp': time.time(),
                'sensor_id': payload.get('sensor_id', 'unknown'),
                'sensor_type': payload.get('sensor_type', msg.topic.split('/')[-1]),
                'value': payload.get('value'),
                'location': payload.get('location', 'unknown'),
                'raw_payload': payload
            }

            logger.debug(f"Received sensor data: {sensor_data}")

            # Call the data callback if registered
            if self.data_callback:
                self.data_callback(sensor_data)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON payload: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def set_data_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Set the callback function to be called when sensor data is received.

        Args:
            callback: Function that takes sensor data dictionary as argument
        """
        self.data_callback = callback

    def connect(self) -> bool:
        """
        Connect to the MQTT broker.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.client = mqtt.Client(client_id=self.client_id)
            self.client.on_connect = self.on_connect
            self.client.on_disconnect = self.on_disconnect
            self.client.on_message = self.on_message

            logger.info(f"Connecting to MQTT broker at {self.broker_host}:{self.broker_port}")
            self.client.connect(self.broker_host, self.broker_port, 60)

            # Start the network loop in a separate thread
            self.client.loop_start()
            self.running = True

            # Wait for connection
            timeout = 10
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)

            if self.connected:
                logger.info("MQTT client connected successfully")
                return True
            else:
                logger.error("Failed to connect to MQTT broker within timeout")
                return False

        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False

    def disconnect(self):
        """Disconnect from the MQTT broker."""
        if self.client and self.running:
            logger.info("Disconnecting from MQTT broker")
            self.client.loop_stop()
            self.client.disconnect()
            self.running = False
            self.connected = False

    def is_connected(self) -> bool:
        """Check if the client is connected to the MQTT broker."""
        return self.connected

    def publish_test_message(self, topic: str, sensor_data: Dict[str, Any]):
        """
        Publish a test message to verify MQTT functionality.

        Args:
            topic: MQTT topic to publish to
            sensor_data: Sensor data dictionary
        """
        if not self.connected:
            logger.warning("Cannot publish: not connected to MQTT broker")
            return

        try:
            payload = json.dumps(sensor_data)
            self.client.publish(topic, payload, qos=1)
            logger.info(f"Published test message to topic: {topic}")
        except Exception as e:
            logger.error(f"Failed to publish test message: {e}")


def create_sensor_client(broker_host: str = "localhost", broker_port: int = 1883) -> MQTTSensorClient:
    """
    Factory function to create and configure an MQTT sensor client.

    Args:
        broker_host: MQTT broker hostname
        broker_port: MQTT broker port

    Returns:
        Configured MQTTSensorClient instance
    """
    topics = [
        "sensors/temperature",
        "sensors/motion",
        "sensors/sound",
        "sensors/humidity",
        "sensors/light"
    ]

    client = MQTTSensorClient(
        broker_host=broker_host,
        broker_port=broker_port,
        topics=topics
    )

    return client


if __name__ == "__main__":
    # Example usage
    def sensor_data_handler(data):
        print(f"Received sensor data: {data}")

    client = create_sensor_client()
    client.set_data_callback(sensor_data_handler)

    if client.connect():
        print("MQTT client connected. Listening for sensor data...")
        try:
            # Keep running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down...")
        finally:
            client.disconnect()
    else:
        print("Failed to connect to MQTT broker")