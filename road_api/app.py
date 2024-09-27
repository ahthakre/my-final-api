from flask import Flask, request, jsonify, render_template, redirect, url_for
import time
import os
import json
import logging

# Initialize Flask app
app = Flask(__name__, template_folder='_pycache_')

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s')

# Ensure Firebase credentials are provided as an environment variable
firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')
if not firebase_credentials:
    logging.error("Firebase credentials not found. Ensure FIREBASE_CREDENTIALS is set.")
    raise ValueError("Firebase credentials not found. Please set FIREBASE_CREDENTIALS environment variable.")

try:
    # Parse the encoded credentials JSON string
    cred_dict = json.loads(firebase_credentials)
    cred = credentials.Certificate(cred_dict)
    # Initialize Firebase Admin SDK with the given credentials
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://log-object-detection-default-rtdb.firebaseio.com/'
    })
    logging.info("Firebase Admin SDK initialized successfully.")
except Exception as e:
    logging.error(f"Failed to initialize Firebase Admin SDK: {e}")
    raise

# Reference to the 'CAMERA ON' node in Firebase
detection_ref = db.reference('CAMERA ON')

# Helper function to validate request data
def validate_request_data(data, required_fields):
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return False, {"error": f"Missing required fields: {', '.join(missing_fields)}"}, 400
    return True, None, None

# Route to render the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint to fetch the last entry from 'detection' node (used by frontend)
@app.route('/api/last_detection_data', methods=['GET'])
def get_last_detection_data():
    try:
        detection_data = detection_ref.get()

        if detection_data:
            # Get the last entry by sorting keys
            last_uid = max(detection_data.keys())
            last_entry = detection_data[last_uid]
            last_entry["uid"] = last_uid
            logging.info(f"Retrieved last detection data for UID: {last_uid}")
            return jsonify(last_entry), 200
        else:
            logging.warning("No data found in 'detection'.")
            return jsonify({"message": "No data found in detection"}), 404

    except Exception as e:
        logging.error(f"Error fetching last detection data: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# Endpoint to store road curvature angle
@app.route('/api/store/curvature', methods=['POST'])
def store_curvature():
    try:
        data = request.json
        valid, error_response, status = validate_request_data(data, ['uid', 'angle'])
        if not valid:
            return jsonify(error_response), status

        uid = data['uid']
        angle = data['angle']
        timestamp = time.time()

        # Store curvature angle and timestamp
        detection_ref.child(uid).update({'curvature_angle': angle, 'timestamp': timestamp})
        logging.info(f"Stored curvature angle: {angle} for UID: {uid}")

        return jsonify({"message": "Curvature angle stored successfully", "curvature_angle": angle}), 200

    except Exception as e:
        logging.error(f"Error storing curvature angle: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# Endpoint to store distance from the front vehicle
@app.route('/api/store/distance', methods=['POST'])
def store_distance():
    try:
        data = request.json
        valid, error_response, status = validate_request_data(data, ['uid', 'distance'])
        if not valid:
            return jsonify(error_response), status

        uid = data['uid']
        distance = data['distance']
        timestamp = time.time()

        # Store distance and timestamp
        detection_ref.child(uid).update({'front_vehicle_distance': distance, 'timestamp': timestamp})
        logging.info(f"Stored front vehicle distance: {distance} for UID: {uid}")

        return jsonify({"message": "Distance stored successfully", "front_vehicle_distance": distance}), 200

    except Exception as e:
        logging.error(f"Error storing front vehicle distance: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# Main entry point of the Flask app
if __name__ == '__main__':
    # Run Flask app with better error handling and logging
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False)
