import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, request, jsonify
import time
import os
import json

app = Flask(__name__)

# Initialize Firebase Admin SDK
firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')  # Get encoded Firebase credentials from environment
if firebase_credentials:
    cred_dict = json.loads(firebase_credentials)  # Parse the encoded credentials JSON string
    cred = credentials.Certificate(cred_dict)
else:
    raise ValueError("Firebase credentials not found. Please set FIREBASE_CREDENTIALS environment variable.")

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://log-object-detection-default-rtdb.firebaseio.com/'
})

# Reference to the 'detection' node in Firebase
detection_ref = db.reference('detections')

# Endpoint to fetch the last entry from 'detection' child
@app.route('/api/last_detection_data', methods=['GET'])
def get_last_detection_data():
    try:
        # Retrieve all data under the 'detection' child
        detection_data = detection_ref.get()

        if detection_data:
            # Get the last entry based on the highest key (assuming UIDs are sortable)
            last_uid = max(detection_data.keys())
            last_entry = detection_data[last_uid]
            last_entry["uid"] = last_uid  # Add UID to the response
            return jsonify(last_entry), 200
        else:
            return jsonify({"message": "No data found in detection"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to store road curvature as angle
@app.route('/api/store/curvature', methods=['POST'])
def store_curvature():
    try:
        uid = request.json.get('uid')
        angle = request.json.get('angle')

        if not uid or angle is None:
            return jsonify({"error": "UID and angle are required"}), 400

        # Store the curvature angle under the specific UID with a timestamp
        detection_ref.child(uid).child('curvature_angle').set(angle)
        detection_ref.child(uid).child('timestamp').set(time.time())  # Store current timestamp
        return jsonify({"message": "Curvature angle stored successfully", "curvature_angle": angle}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to store distance from the front vehicle
@app.route('/api/store/distance', methods=['POST'])
def store_distance():
    try:
        uid = request.json.get('uid')
        distance = request.json.get('distance')

        if not uid or distance is None:
            return jsonify({"error": "UID and distance are required"}), 400

        # Store the front vehicle distance under the specific UID with a timestamp
        detection_ref.child(uid).child('front_vehicle_distance').set(distance)
        detection_ref.child(uid).child('timestamp').set(time.time())  # Store current timestamp
        return jsonify({"message": "Distance stored successfully", "front_vehicle_distance": distance}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Main entry point of the Flask app
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))  # Railway sets the PORT environment variable
    app.run(debug=True, host='0.0.0.0', port=port)
