import streamlit as st
import paho.mqtt.client as mqtt
import json
import threading
import datetime
import pandas as pd
import time
import matplotlib.pyplot as plt

# MQTT Broker settings
broker_address = "broker.hivemq.com"  # Replace with your MQTT broker address
broker_port = 1883  # Replace with your MQTT broker port
topic = "processed/home/arduino/state"  # Processed data topic

# Data storage
data_stream = []  # List to store the data
last_off_timestamp = None  # Variable to store the timestamp of the last 'OFF' state

# The MQTT client callback for when a message is received
def on_message(client, userdata, msg):
    global data_stream, last_off_timestamp
    payload = json.loads(msg.payload.decode())
    payload_time = datetime.datetime.strptime(payload['time'], '%Y-%m-%d %H:%M:%S')

    # Append new data
    data_stream.append({
        'time': payload_time,
        'state': payload['state']
    })

    # Clean up data older than 3 hours
    cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=3)
    data_stream = [data for data in data_stream if data['time'] > cutoff_time]

    # Handle 'OFF' timestamp logic
    if payload['state'] == 'OFF' and last_off_timestamp is None:
        last_off_timestamp = payload_time
    elif payload['state'] == 'ON':
        last_off_timestamp = None

# Function to create and run MQTT client in a separate thread
def run_mqtt_client():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(broker_address, broker_port, 60)
    client.subscribe(topic)
    client.loop_start()


# Function to create the chart using matplotlib
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


# Streamlit app
def main():
    st.title("Real-time MQTT Data Visualization")

    # Start MQTT client in a separate thread
    mqtt_thread = threading.Thread(target=run_mqtt_client)
    mqtt_thread.start()

    placeholder = st.empty()
    while True:
        if data_stream:  # Check if data_stream is not empty
            # Convert the data_stream to DataFrame
            df = pd.DataFrame(data_stream)
            # Generate and display the chart
            fig = create_chart(df, last_off_timestamp)
            if fig:
                placeholder.pyplot(fig)
                plt.close(fig)  # Close the figure to prevent memory issues

        time.sleep(1)  # Update interval

if __name__ == "__main__":
    main()
