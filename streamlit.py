import paho.mqtt.client as mqtt
import streamlit as st
import threading
import datetime
import time

# MQTT Settings
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "toaster/current"

# Global variables to store data
current_value = 0
last_updated = datetime.datetime.now()

# Callback when connected to MQTT broker
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(MQTT_TOPIC)

# Callback when receiving a message from MQTT broker
def on_message(client, userdata, msg):
    global current_value, last_updated
    current_value = float(msg.payload.decode())
    last_updated = datetime.datetime.now()

# MQTT Client Setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT Broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Start a separate thread for MQTT client loop
threading.Thread(target=client.loop_forever, daemon=True).start()

# Streamlit App
# Streamlit App
def main():
    st.title("Toaster Current Monitor")

    # Run this block every second to update the values
    while True:
        with st.empty():
            # Display current value and last updated time
            st.write(f"Current Value: {current_value} mA")
            st.write(f"Last Updated: {last_updated}")

            # Display color based on the current value
            if current_value > 5:
                st.markdown("<h1 style='color:green;'>ON</h1>", unsafe_allow_html=True)
            else:
                st.markdown("<h1 style='color:red;'>OFF</h1>", unsafe_allow_html=True)

            time.sleep(1)  # Use time.sleep() here

if __name__ == "__main__":
    main()
