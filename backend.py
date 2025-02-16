from flask import Flask
from flask_socketio import SocketIO, emit
import joblib
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load the trained model
model = joblib.load("lgt_model.pkl")

# Initialize Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

label_mapping = {
    0: 'malicious packet',
    1: 'normal packet',
}

# Store edge node statuses
edge_node_status = {}

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
        server.set_debuglevel(1)  # Enable debug output
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        text = msg.as_string()
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, text)
        server.quit()
        print(f"Email sent successfully to {RECIPIENT_EMAIL}")
    except Exception as e:
        print(f"Error sending email: {e}")

@socketio.on('data_point')
def handle_data_point(data):
    try:
        print(f"Received data point: {data}")
        data_point = data['key']
        host_name = data['Host_name']

        # Convert received data to DataFrame
        data_point = pd.DataFrame([data_point])

        print(f"Converted DataFrame: {data_point}")
        data_point = data_point.iloc[:, :-1]  # Remove 'label' column for prediction

        # Make prediction
        prediction = model.predict(data_point)
        print(f"Prediction result: {prediction}")

        predicted_label = label_mapping[int(prediction[0])]

        # Update edge node status
        edge_node_status[host_name] = {
            "input_data": data_point.to_dict(orient="records"),
            "prediction": predicted_label
        }

        # Print the updated statuses
        print(f"Updated edge node status: {edge_node_status}")

        # If malicious packet detected, send email notification
        if predicted_label == 'malicious packet':
            subject = "Malicious Packet Detected"
            body = f"Malicious packet detected from edge node: {host_name}\n\nData:\n{data_point}"
            send_email(subject, body)

        # Send updated status of all edge nodes
        emit('all_edge_nodes_status', edge_node_status, broadcast=True)

    except Exception as e:
        emit('error', {"error": str(e)})

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0",port=5000)