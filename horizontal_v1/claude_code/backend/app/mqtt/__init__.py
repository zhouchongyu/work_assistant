"""
MQTT client module for real-time notifications.

Provides:
- MqttClient singleton for publishing notifications
- Convenience functions for common notification patterns
- Topic constants (cool/public, cool/person)

Reference:
- assistant_py/db/mqtt_client.py
"""

from app.mqtt.client import (
    MqttClient,
    get_mqtt_client,
    TOPIC_PUBLIC,
    TOPIC_PERSON,
    NotificationType,
    send_supply_analysis_notification,
    send_demand_analysis_notification,
    send_match_complete_notification,
    send_user_message,
    send_warning_notification,
)

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
