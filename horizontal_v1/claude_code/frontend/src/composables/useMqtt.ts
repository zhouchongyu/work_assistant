/**
 * MQTT composable for real-time notifications.
 *
 * Features:
 * - Auto-connect/reconnect
 * - Topic subscription
 * - Message handling
 */
import { ref, onMounted, onUnmounted } from 'vue'
import mqtt, { type MqttClient, type IClientOptions } from 'mqtt'

export interface MqttMessage {
  topic: string
  payload: any
}

// MQTT topics
export const MQTT_TOPICS = {
  PUBLIC: 'cool/public',
  PERSON: 'cool/person',
}

export function useMqtt(userId?: number) {
  const client = ref<MqttClient | null>(null)
  const connected = ref(false)
  const messages = ref<MqttMessage[]>([])

  // Connection options
  const options: IClientOptions = {
    host: import.meta.env.VITE_MQTT_HOST || 'localhost',
    port: parseInt(import.meta.env.VITE_MQTT_PORT || '9001'),
    path: import.meta.env.VITE_MQTT_PATH || '/mqtt',
    protocol: 'ws',
    clientId: `wa_${Date.now()}_${Math.random().toString(16).substr(2, 8)}`,
    keepalive: 60,
    reconnectPeriod: 5000,
    connectTimeout: 30000,
    clean: true,
  }

  // Connect to broker
  function connect() {
    if (client.value?.connected) return

    const url = `ws://${options.host}:${options.port}${options.path}`
    client.value = mqtt.connect(url, options)

    client.value.on('connect', () => {
      connected.value = true
      console.log('[MQTT] Connected')
      subscribeTopics()
    })

    client.value.on('error', (error) => {
      console.error('[MQTT] Error:', error)
    })

    client.value.on('close', () => {
      connected.value = false
      console.log('[MQTT] Disconnected')
    })

    client.value.on('message', (topic, payload) => {
      try {
        const message = JSON.parse(payload.toString())
        messages.value.push({ topic, payload: message })

        // Limit message history
        if (messages.value.length > 100) {
          messages.value = messages.value.slice(-100)
        }
      } catch (e) {
        console.error('[MQTT] Failed to parse message:', e)
      }
    })
  }

  // Subscribe to topics
  function subscribeTopics() {
    if (!client.value) return

    // Subscribe to public topic
    client.value.subscribe(MQTT_TOPICS.PUBLIC, (err) => {
      if (err) {
        console.error('[MQTT] Failed to subscribe to public:', err)
      }
    })

    // Subscribe to personal topic if userId provided
    if (userId) {
      const personalTopic = `${MQTT_TOPICS.PERSON}/${userId}`
      client.value.subscribe(personalTopic, (err) => {
        if (err) {
          console.error('[MQTT] Failed to subscribe to personal:', err)
        }
      })
    }
  }

  // Disconnect from broker
  function disconnect() {
    if (client.value) {
      client.value.end()
      client.value = null
      connected.value = false
    }
  }

  // Publish message
  function publish(topic: string, payload: any) {
    if (client.value?.connected) {
      const message = typeof payload === 'string' ? payload : JSON.stringify(payload)
      client.value.publish(topic, message)
    }
  }

  // Subscribe to additional topic
  function subscribe(topic: string, callback?: (message: MqttMessage) => void) {
    if (client.value) {
      client.value.subscribe(topic, (err) => {
        if (err) {
          console.error(`[MQTT] Failed to subscribe to ${topic}:`, err)
        }
      })

      if (callback) {
        client.value.on('message', (t, payload) => {
          if (t === topic) {
            try {
              const message = JSON.parse(payload.toString())
              callback({ topic: t, payload: message })
            } catch (e) {
              // Ignore parse errors
            }
          }
        })
      }
    }
  }

  // Unsubscribe from topic
  function unsubscribe(topic: string) {
    if (client.value) {
      client.value.unsubscribe(topic)
    }
  }

  // Get latest message for topic
  function getLatestMessage(topic: string): MqttMessage | undefined {
    return [...messages.value].reverse().find(m => m.topic === topic)
  }

  // Clear messages
  function clearMessages() {
    messages.value = []
  }

  // Auto-connect on mount
  onMounted(() => {
    connect()
  })

  // Disconnect on unmount
  onUnmounted(() => {
    disconnect()
  })

  return {
    client,
    connected,
    messages,
    connect,
    disconnect,
    publish,
    subscribe,
    unsubscribe,
    getLatestMessage,
    clearMessages,
  }
}

export default useMqtt
