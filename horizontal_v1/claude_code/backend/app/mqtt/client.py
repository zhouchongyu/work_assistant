"""
MQTT client for real-time notifications.

Implements publish-only MQTT client for:
- Public notifications (cool/public) - Analysis status, match results
- Personal notifications (cool/person) - User-specific messages

Reference:
- assistant_py/db/mqtt_client.py
- Wiki: 系统架构/消息队列系统.md
"""

import atexit
import json
import logging
import threading
import time
import uuid
from enum import Enum
from typing import Any

from paho.mqtt import client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

from app.core.config import settings

logger = logging.getLogger("work_assistant.mqtt")


# Topic constants
TOPIC_PUBLIC = "cool/public"
TOPIC_PERSON = "cool/person"


class NotificationType(str, Enum):
    """Notification type enumeration."""

    SUPPLY_ANALYSIS = "supply_analysis"
    DEMAND_ANALYSIS = "demand_analysis"
    MATCH_COMPLETE = "match_complete"
    MESSAGE = "message"
    WARNING = "warning"


class MqttClient:
    """
    Thread-safe singleton MQTT client for publishing notifications.

    Features:
    - Automatic reconnection
    - JSON serialization
    - Graceful shutdown on process exit
    """

    _instance: "MqttClient | None" = None
    _lock = threading.Lock()

    def __new__(cls) -> "MqttClient":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return

        with self._lock:
            if self._initialized:
                return

            self._host = settings.mqtt.broker_host
            self._port = settings.mqtt.broker_port
            self._username = settings.mqtt.username
            self._password = settings.mqtt.password
            self._keepalive = settings.mqtt.keepalive
            self._protocol_version = settings.mqtt.protocol_version

            # Generate unique client ID
            prefix = settings.mqtt.client_id_prefix
            self._client_id = f"{prefix}-{uuid.uuid4().hex[:8]}"

            # Create MQTT client
            protocol = mqtt.MQTTv5 if self._protocol_version == 5 else mqtt.MQTTv311
            self._client = mqtt.Client(
                client_id=self._client_id,
                protocol=protocol,
                callback_api_version=CallbackAPIVersion.VERSION2,
            )

            # Set callbacks
            self._client.on_connect = self._on_connect
            self._client.on_disconnect = self._on_disconnect

            # Set authentication if provided
            if self._username and self._password:
                self._client.username_pw_set(self._username, self._password)

            # Connect
            self._connect()

            # Register cleanup on exit
            atexit.register(self.close)

            self._initialized = True

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        flags: Any,
        reason_code: Any,
        properties: Any,
    ) -> None:
        """Handle connection event."""
        logger.info(f"MQTT connected as {self._client_id}, reason={reason_code}")

    def _on_disconnect(
        self,
        client: mqtt.Client,
        userdata: Any,
        disconnect_flags: Any,
        reason_code: Any,
        properties: Any,
    ) -> None:
        """Handle disconnection event."""
        logger.warning(f"MQTT disconnected, reason={reason_code}")

    def _connect(self) -> None:
        """Establish MQTT connection."""
        try:
            self._client.connect(self._host, self._port, keepalive=self._keepalive)
            self._client.loop_start()
            logger.info(f"MQTT connecting to {self._host}:{self._port}")
        except Exception as e:
            logger.error(f"MQTT connection failed: {e}")

    def reconnect_if_needed(self) -> None:
        """Reconnect if not connected."""
        if not self._client.is_connected():
            try:
                self._connect()
                time.sleep(0.2)  # Brief wait for connection
            except Exception as e:
                raise RuntimeError(f"MQTT reconnect failed: {e}") from e

    def close(self) -> None:
        """Gracefully close MQTT connection."""
        try:
            self._client.loop_stop()
            self._client.disconnect()
            logger.info("MQTT connection closed")
        except Exception as e:
            logger.error(f"Error closing MQTT: {e}")

    def send(
        self,
        topic: str,
        payload: dict[str, Any],
        qos: int = 1,
        retain: bool = False,
    ) -> bool:
        """
        Publish message to MQTT topic.

        Args:
            topic: MQTT topic
            payload: Message payload (will be JSON serialized)
            qos: Quality of Service level (0, 1, or 2)
            retain: Whether to retain the message

        Returns:
            True if publish succeeded
        """
        self.reconnect_if_needed()

        result = self._client.publish(
            topic,
            json.dumps(payload, ensure_ascii=False),
            qos=qos,
            retain=retain,
        )

        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            logger.error(f"MQTT publish failed to {topic}, rc={result.rc}")
            return False

        logger.debug(f"MQTT sent to {topic}: {payload}")
        return True

    # Convenience methods for common notification patterns

    def send_public(self, payload: dict[str, Any]) -> bool:
        """Send notification to public topic."""
        return self.send(TOPIC_PUBLIC, payload)

    def send_person(self, user_id: int, payload: dict[str, Any]) -> bool:
        """
        Send notification to personal topic.

        The payload will include user_id for client-side filtering.
        """
        payload_with_user = {"user_id": user_id, **payload}
        return self.send(TOPIC_PERSON, payload_with_user)


# Singleton instance
_mqtt_client: MqttClient | None = None


def get_mqtt_client() -> MqttClient:
    """Get MQTT client singleton instance."""
    global _mqtt_client
    if _mqtt_client is None:
        _mqtt_client = MqttClient()
    return _mqtt_client


# Convenience functions for sending notifications

def send_supply_analysis_notification(supply_id: int, status: str) -> bool:
    """
    Send supply analysis status notification.

    Args:
        supply_id: Supply ID
        status: Analysis status (e.g., "done", "error")
    """
    client = get_mqtt_client()
    return client.send_public({
        "supply_id": supply_id,
        "status": status,
        "type": NotificationType.SUPPLY_ANALYSIS.value,
    })


def send_demand_analysis_notification(demand_id: int, status: str) -> bool:
    """
    Send demand analysis status notification.

    Args:
        demand_id: Demand ID
        status: Analysis status (e.g., "done", "error")
    """
    client = get_mqtt_client()
    return client.send_public({
        "demand_id": demand_id,
        "status": status,
        "type": NotificationType.DEMAND_ANALYSIS.value,
    })


def send_match_complete_notification(demand_id: int, match_count: int) -> bool:
    """
    Send match completion notification.

    Args:
        demand_id: Demand ID
        match_count: Number of matches found
    """
    client = get_mqtt_client()
    return client.send_public({
        "demand_id": demand_id,
        "match_count": match_count,
        "status": "done",
        "type": NotificationType.MATCH_COMPLETE.value,
    })


def send_user_message(user_id: int, message: str, message_type: str = "info") -> bool:
    """
    Send personal message to user.

    Args:
        user_id: Target user ID
        message: Message content
        message_type: Message type (info, warning, error)
    """
    client = get_mqtt_client()
    return client.send_person(user_id, {
        "message": message,
        "message_type": message_type,
        "type": NotificationType.MESSAGE.value,
    })


def send_warning_notification(
    user_id: int,
    supply_id: int | None = None,
    demand_id: int | None = None,
    message: str = "",
) -> bool:
    """
    Send warning notification to user.

    Args:
        user_id: Target user ID
        supply_id: Related supply ID (optional)
        demand_id: Related demand ID (optional)
        message: Warning message
    """
    client = get_mqtt_client()
    payload: dict[str, Any] = {
        "message": message,
        "type": NotificationType.WARNING.value,
    }
    if supply_id:
        payload["supply_id"] = supply_id
    if demand_id:
        payload["demand_id"] = demand_id

    return client.send_person(user_id, payload)


__all__ = [
    "MqttClient",
    "get_mqtt_client",
    "TOPIC_PUBLIC",
    "TOPIC_PERSON",
    "NotificationType",
    "send_supply_analysis_notification",
    "send_demand_analysis_notification",
    "send_match_complete_notification",
    "send_user_message",
    "send_warning_notification",
]
