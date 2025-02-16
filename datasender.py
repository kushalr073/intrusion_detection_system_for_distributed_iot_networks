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
sio.connect('http://localhost:5000')

# Path to the file containing 1000 data points
file_path = "apple.csv"

# Load the data from the CSV file
data = pd.read_csv(file_path)

# Create WebSocket connection to the backend
# ws = create_connection("ws://localhost:5000/socket.io/?transport=websocket")

for _, row in data.iterrows():
    df = row.to_dict()
    sio.emit('data_point', df)  # Send the data point to the server
    print(f"Sent data point: {df}")
    time.sleep(10)  # Delay of 2 seconds

# Disconnect after sending all data
sio.disconnect()
