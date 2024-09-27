import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, request, jsonify
import time
import os
import json
import logging

# Initialize Flask app
app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize Firebase Admin SDK
firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')  # Get encoded Firebase credentials from environment
if firebase_credentials:
    try:
        cred_dict = json.loads(firebase_credentials)  # Parse the encoded credentials JSON string
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            'databaseURL': os.getenv('FIREBASE_DATABASE_URL')  # Set the database URL via environment variable
        })
        logging.info("Firebase initialized successfully.")
    except Exception as e:
        logging.error(f"Error initializing Firebase: {e}")
        raise ValueError("Invalid Firebase credentials or initialization issue.")
else:
    raise ValueError("Firebase credentials not found. Please set the FIREBASE_CREDENTIALS environment variable.")

# Reference to the 'detection' node in Firebase
detection_ref = db.reference('CAMERA ON')

# Helper function for input validation
def validate_input(data, required_fields):
    """Validates the input data based on required fields."""
    missing_fields = [field for field in required_fields if data.get(field) is None]
    if missing_fields:
        return False, f"Missing fields: {', '.join(missing_fields)}"
    return True, None

# Endpoint to fetch the last entry from 'detection' child
@app.route('/api/last_detection_data', methods=['GET'])
def get_last_detection_data():
    try:
        # Retrieve all data under the 'detection' node
        detection_data = detection_ref.get()

        if detection_data:
            # Get the last entry based on the highest key (assuming UIDs are sortable)
            last_uid = max(detection_data.keys())
            last_entry = detection_data[last_uid]
            last_entry["uid"] = last_uid  # Add UID to the response
            return jsonify({"status": "success", "data": last_entry}), 200
        else:
            return jsonify({"status": "error", "message": "No data found in detection"}), 404

    except Exception as e:
        logging.error(f"Error retrieving data: {e}")
        return jsonify({"status": "error", "message": "Server error occurred"}), 500

# Endpoint to store road curvature as angle
@app.route('/api/store/curvature', methods=['POST'])
def store_curvature():
    try:
        data = request.json
        # Validate input
        is_valid, error_message = validate_input(data, ['uid', 'angle'])
        if not is_valid:
            return jsonify({"status": "error", "message": error_message}), 400

        uid = data['uid']
        angle = data['angle']

        # Store the curvature angle under the specific UID with a timestamp
        detection_ref.child(uid).child('curvature_angle').set(angle)
        detection_ref.child(uid).child('timestamp').set(time.time())  # Store current timestamp
        return jsonify({"status": "success", "message": "Curvature angle stored successfully", "curvature_angle": angle}), 200

    except Exception as e:
        logging.error(f"Error storing curvature angle: {e}")
        return jsonify({"status": "error", "message": "Server error occurred"}), 500

# Endpoint to store distance from the front vehicle
@app.route('/api/store/distance', methods=['POST'])
def store_distance():
    try:
        data = request.json
        # Validate input
        is_valid, error_message = validate_input(data, ['uid', 'distance'])
        if not is_valid:
            return jsonify({"status": "error", "message": error_message}), 400

        uid = data['uid']
        distance = data['distance']

        # Store the front vehicle distance under the specific UID with a timestamp
        detection_ref.child(uid).child('front_vehicle_distance').set(distance)
        detection_ref.child(uid).child('timestamp').set(time.time())  # Store current timestamp
        return jsonify({"status": "success", "message": "Distance stored successfully", "front_vehicle_distance": distance}), 200

    except Exception as e:
        logging.error(f"Error storing distance: {e}")
        return jsonify({"status": "error", "message": "Server error occurred"}), 500

# Main entry point of the Flask app
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))  # Railway sets the PORT environment variable
    app.run(debug=False, host='0.0.0.0', port=port)
