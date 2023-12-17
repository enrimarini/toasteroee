import streamlit as st
import paho.mqtt.client as mqtt
import json
import threading
import datetime
import pandas as pd
import time
import matplotlib.pyplot as plt
from queue import Queue

# MQTT Constants
BROKER_ADDRESS = "broker.hivemq.com"
TOPIC1 = "processed/home/arduino/state"
TOPIC2 = "home/arduino/current"

# Data Storage
data_stream = []  # For TOPIC1
data_queue = Queue()  # For TOPIC2

# Additional Global Variables
last_off_timestamp = None

# MQTT Client Setup
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    st.write(f"Connected with result code {rc}")
    client.subscribe([(TOPIC1, 0), (TOPIC2, 0)])

def on_message(client, userdata, msg):
    if msg.topic == TOPIC1:
        process_topic1(msg)
    elif msg.topic == TOPIC2:
        process_topic2(msg)

def process_topic1(msg):
    global data_stream, last_off_timestamp
    payload = json.loads(msg.payload.decode())
    payload_time = datetime.datetime.strptime(payload['time'], '%Y-%m-%d %H:%M:%S')

    data_stream.append({
        'time': payload_time,
        'state': payload['state']
    })

    # Cleaning and timestamp logic (same as in app 1)

def process_topic2(msg):
    payload = msg.payload.decode("utf-8").strip()
    data_queue.put(payload)

def run_mqtt_client():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_ADDRESS)
    client.loop_start()

def create_chart(df, last_off_timestamp):
    # Ensure DataFrame is not empty
    if df.empty:
        return None

    # Determine the height of the bar to offset the annotations appropriately
    bar_height = 0.8  # Adjust this as needed to scale the bar chart

    # Create a horizontal bar chart
    fig, ax = plt.subplots(figsize=(10, 1))
    # Track the previous state to control annotation display
    previous_state = None
    # Variable to alternate the annotations
    annotate_above = True

    # Plot each data point individually
    for index, row in df.iterrows():
        color = 'green' if row['state'] == 'ON' else 'red'
        bar = ax.barh(0, 1, left=index, color=color, height=bar_height)

        # Add the timestamp for 'OFF' events, alternating their position
        if row['state'] == 'OFF' and previous_state != 'OFF':
            # Alternate the vertical position of the annotations
            vertical_position = 10 if annotate_above else -10  # Adjust this as needed
            vertical_alignment = 'bottom' if annotate_above else 'top'
            timestamp_str = row['time'].strftime('%b %d, %Y %H:%M:%S')

            # Get the coordinates of the bar edge
            bar_edge = bar[0].get_xy()[1] + bar[0].get_height() if annotate_above else bar[0].get_xy()[1]

            ax.annotate(timestamp_str, xy=(index, bar_edge), xytext=(0, vertical_position),
                        textcoords='offset points', ha='center', va=vertical_alignment,
                        fontsize=8, arrowprops=dict(arrowstyle='-', lw=1))

            # Flip the position for the next annotation
            annotate_above = not annotate_above

        # Update the previous state
        previous_state = row['state']

    ax.axis('off')  # No axes

    # Set the limits of the plot to account for the annotations
    ax.set_ylim(-1.5, 1.5)  # Adjust as needed based on the bar_height

    return fig

def update_pie_chart(status_times, chart_placeholder):
    # Close previous figure to prevent memory leak
    plt.close('all')

    labels = ['ON', 'OFF']
    sizes = [status_times['ON'], status_times['OFF']]

    # Only generate pie chart if there is data
    if sum(sizes) > 0:
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['green', 'red'])
        ax.axis('equal')  # Equal aspect ratio ensures the pie chart is circular.
        chart_placeholder.pyplot(fig)
    else:
        chart_placeholder.text("Waiting for MQTT data...")

def main():
    st.title("MQTT Streamlit Dashboard")

    # Initialize session state variables for the second app's data
    if 'current_value' not in st.session_state:
        st.session_state['current_value'] = 0.0
    if 'status_times' not in st.session_state:
        st.session_state['status_times'] = {'ON': 0, 'OFF': 0}
    if 'device_status' not in st.session_state:
        st.session_state['device_status'] = 'OFF'  # Default status

    # Start MQTT client in a separate thread
    mqtt_thread = threading.Thread(target=run_mqtt_client)
    mqtt_thread.start()

    # Streamlit placeholders for various components
    placeholder_chart1 = st.empty()
    placeholder_current_value = st.empty()
    placeholder_status = st.empty()
    placeholder_chart2 = st.empty()

    # Main loop to update the dashboard
    while True:
        # Handle data from TOPIC1
        if data_stream:
            df = pd.DataFrame(data_stream)
            fig1 = create_chart(df, last_off_timestamp)
            if fig1:
                placeholder_chart1.pyplot(fig1)
                plt.close(fig1)

        # Handle data from TOPIC2
        if not data_queue.empty():
            payload = data_queue.get()
            try:
                st.session_state.current_value = float(payload.rstrip(' A'))
                st.session_state.device_status = "ON" if st.session_state.current_value > 1 else "OFF"
                st.session_state.status_times[st.session_state.device_status] += 1
            except ValueError:
                st.error("Invalid payload received")

            # Update current value and status text
            placeholder_current_value.text(f"Current Value: {st.session_state.current_value} A")
            placeholder_status.markdown(
                f"<h2 style='color:{'green' if st.session_state.device_status == 'ON' else 'red'};'>{st.session_state.device_status}</h2>",
                unsafe_allow_html=True)

            # Update the pie chart
            update_pie_chart(st.session_state['status_times'], placeholder_chart2)

        time.sleep(1)  # Refresh interval

if __name__ == "__main__":
    main()
