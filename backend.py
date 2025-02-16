from flask import Flask
from flask_socketio import SocketIO, emit
import joblib
import pandas as pd

# Load the trained model
model = joblib.load("lgt_model.pkl")

# Initialize Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

label_mapping = {
    0: 'malicious packet', 
    1: 'normal packet', 
    
}

@socketio.on('data_point')
def handle_data_point(data):
    try:
        print(f"Received data point: {data}")  # Ensure data is being received
        data_point=data['key']
        host_name=data['Host_name']
        # Convert received data to a DataFrame
        data_point = pd.DataFrame([data_point])  # Expecting a single data point as a dictionary

        print(f"Converted DataFrame: {data_point}")
        data_point = data_point.iloc[:, :-1]  # Remove 'label' column for prediction
        # Make prediction
        prediction = model.predict(data_point)
        print(f"Prediction result: {prediction}")

        predicted_label=label_mapping[int(prediction[0])]
        # Prepare the response
        response = {
            "input_data": data_point.to_dict(orient="records"),
            "prediction": predicted_label,
            "host_name":host_name
        }

        # Print the response before emitting
        print(f"Emitting response: {response}")

        # Send the prediction result to the frontend
        emit('prediction_result', response, broadcast=True)
    except Exception as e:
        emit('error', {"error": str(e)})

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)
