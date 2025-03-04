from flask import Flask
from flask_socketio import SocketIO, emit
import joblib
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

# Load the trained model
model = joblib.load("gaussian_nb_model.pkl")

# Initialize Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

label_mapping = {
    0: 'normal packet',
    1: 'malicious packet',
}

# Store edge node statuses and last active time
edge_node_status = {}

# Timeout duration in seconds (30s to mark as stopped)
TIMEOUT_DURATION = 10

# Email configuration
SENDER_EMAIL = "sumanthbs10603@gmail.com"
SENDER_PASSWORD = "kowi ydfk ceeu hmio"
RECIPIENT_EMAIL = "kushalr073@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Function to send email
def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Set up the server and send the email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        print(f"✅ Email sent successfully to {RECIPIENT_EMAIL}")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

@socketio.on('data_point')
def handle_data_point(data):
    try:
        print(f"📥 Received data point: {data}")
        data_point = data['key']
        host_name = data['Host_name']

        # Convert received data to DataFrame
        data_point = pd.DataFrame([data_point])

        print(f"🔍 Converted DataFrame: {data_point}")

        # Select only required features (5,6,19,20)
        selected_features = data_point.iloc[:, [5, 6, 19, 20]].copy()

        # Rename columns
        selected_features.columns = ['src_bytes', 'dest_bytes', 'count', 'srv_count']

        print(f"📊 Selected Features: {selected_features}")

        # Make prediction
        prediction = model.predict(data_point)
        print(f"🔮 Prediction result: {prediction}")
        
        predicted_label = label_mapping[int(prediction[0])]

        # ✅ Update edge node status and last active time
        edge_node_status[host_name] = {
            "input_data": selected_features.to_dict(orient="records"),  # Send only selected features
            "prediction": predicted_label,
            "last_active": time.time(),  # Store timestamp of last received data
            "status": "active"  # Mark as active
        }

        print(f"📡 Updated edge node status: {edge_node_status}")

        # ✅ Send email **only** for malicious packets
        if predicted_label == 'malicious packet':
            subject = "🚨 Malicious Packet Detected"
            body = f"⚠️ Warning: A malicious packet was detected from edge node: {host_name}\n\nData:\n{selected_features}"
            send_email(subject, body)
            print("🚨 Email sent for malicious packet.")
        else:
            print("✅ Normal packet detected. No email triggered.")

        # Emit the updated status to frontend
        emit('all_edge_nodes_status', edge_node_status, broadcast=True)

    except Exception as e:
        print(f"❌ Error processing data: {e}")
        emit('error', {"error": str(e)})

# Background task to monitor inactive nodes
def check_inactive_nodes():
    while True:
        current_time = time.time()
        for host_name in list(edge_node_status.keys()):  # Use list() to avoid runtime errors
            last_active = edge_node_status[host_name].get("last_active", current_time)
            if (current_time - last_active) > TIMEOUT_DURATION:
                edge_node_status[host_name]["status"] = "stopped"  # Mark as stopped
        socketio.emit('all_edge_nodes_status', edge_node_status)  # Send updated data
        time.sleep(10)  # Check every 10 seconds

# Start the background thread for inactive node detection
import threading
threading.Thread(target=check_inactive_nodes, daemon=True).start()

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)
