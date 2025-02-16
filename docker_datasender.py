import os
import time
import pandas as pd
import socketio

# Initialize the Socket.IO client
sio = socketio.Client()

@sio.event
def connect():
    print("Connected to the server")

# Event when an error occurs
@sio.event
def connect_error(data):
    print(f"Connection failed: {data}")

# Event when disconnected from server
@sio.event
def disconnect():
    print("Disconnected from server")

# Connect to the server
sio.connect('http://host.docker.internal:5000')

# Read the file path from the environment variable FILE_PATH
file_path = os.getenv('FILE_PATH')

if not file_path:
    print("Error: The FILE_PATH environment variable is not set.")
    sio.disconnect()
    exit(1)

# Load the data from the CSV file
data = pd.read_csv(file_path)
container_path = os.getenv('CONTAINER_NAME')
# Iterate through the rows and send data points to the server
for _, row in data.iterrows():
    df = row.to_dict()
    sio.emit('data_point', {'key':df,'Host_name':container_path})  # Send the data point to the server
    print(f"Sent data point: {df}")
    time.sleep(4)  # Delay of 4 seconds

# Disconnect after sending all data
sio.disconnect()
