import streamlit as st
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import threading
import time
from queue import Queue

# MQTT constants
BROKER_ADDRESS = "broker.hivemq.com"
TOPIC = "home/arduino/current"

# Initialize a queue for thread-safe data transfer
data_queue = Queue()

# MQTT client setup
client = mqtt.Client()


def on_connect(client, userdata, flags, rc):
    st.write(f"Connected with result code {rc}")
    client.subscribe(TOPIC)


def on_message(client, userdata, message):
    payload = message.payload.decode("utf-8").strip()
    # Put the received payload into the queue
    data_queue.put(payload)


client.on_connect = on_connect
client.on_message = on_message


# Run MQTT client in a separate thread
def run_mqtt_client():
    client.connect(BROKER_ADDRESS)
    client.loop_forever()


threading.Thread(target=run_mqtt_client).start()

# Streamlit layout
st.title("MQTT Streamlit Dashboard")

# Initialize session state variables
if 'current_value' not in st.session_state:
    st.session_state['current_value'] = 0.0
if 'status_times' not in st.session_state:
    st.session_state['status_times'] = {'ON': 0, 'OFF': 0}
if 'device_status' not in st.session_state:
    st.session_state['device_status'] = 'OFF'  # Default status

# Placeholders for live data
current_value_placeholder = st.empty()
status_placeholder = st.empty()
chart_placeholder = st.empty()


def update_chart():
    # Close previous figure to prevent memory leak
    plt.close('all')
    labels = ['ON', 'OFF']
    sizes = [st.session_state['status_times']['ON'], st.session_state['status_times']['OFF']]
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['green', 'red'])
    ax.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.
    chart_placeholder.pyplot(fig)


# Main loop to update the dashboard
def main():
    while True:
        # Check if there is new data in the queue
        if not data_queue.empty():
            payload = data_queue.get()
            # Update the current value and status times
            try:
                st.session_state.current_value = float(payload.rstrip(' A'))
                st.session_state.device_status = "ON" if st.session_state.current_value > 1 else "OFF"
                st.session_state.status_times[st.session_state.device_status] += 1
            except ValueError:
                st.error("Invalid payload received")

        # Update current value and status text
        current_value_placeholder.text(f"Current Value: {st.session_state.current_value} A")
        status_placeholder.markdown(
            f"<h2 style='color:{'green' if st.session_state.device_status == 'ON' else 'red'};'>{st.session_state.device_status}</h2>",
            unsafe_allow_html=True)

        # Update the pie chart if there is data
        if sum(st.session_state.status_times.values()) > 0:
            update_chart()
        else:
            chart_placeholder.text("Waiting for MQTT data...")

        time.sleep(1)  # Refresh interval


if __name__ == "__main__":
    main()
