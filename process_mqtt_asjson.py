import paho.mqtt.client as mqtt
import datetime
import json

# MQTT Broker settings
broker_address = "broker.hivemq.com"  # Replace with your MQTT broker address
broker_port = 1883  # Replace with your MQTT broker port
topic = "home/arduino/current"  # Replace with your MQTT topic

# Topics for publishing processed data
processed_state_topic = "processed/home/arduino/state"
processed_timestamp_topic = "processed/home/arduino/timestamp"

# This variable will keep track of the last 'OFF' timestamp
last_off_timestamp = None

# The MQTT client callback for when a connection is established
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(topic)

# The MQTT client callback for when a message is received
def on_message(client, userdata, msg):
    global last_off_timestamp
    payload = float(msg.payload.decode())
    current_time = datetime.datetime.now()

    # Determine 'ON'/'OFF' state
    state = 'ON' if payload >= 1 else 'OFF'

    # Handle 'OFF' timestamp logic
    if state == 'OFF':
        if last_off_timestamp is None:
            last_off_timestamp = current_time
            # Publish the timestamp when 'OFF' condition is first met
            publish_data(client, processed_timestamp_topic, last_off_timestamp.strftime('%H:%M:%S'))
    else:
        last_off_timestamp = None

    # Prepare and publish state data
    data = {
        'time': current_time.strftime('%Y-%m-%d %H:%M:%S'),
        'state': state
    }
    publish_data(client, processed_state_topic, json.dumps(data))

# Function to publish data to a specific MQTT topic
def publish_data(client, topic, message):
    client.publish(topic, message)
    print(f"Published to {topic}: {message}")  # Add this line


# Set up MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT Broker
client.connect(broker_address, broker_port, 60)

# Start the loop
client.loop_forever()
