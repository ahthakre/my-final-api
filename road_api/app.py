import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, request, jsonify

app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate(r'C:\Users\ES\OneDrive\Desktop\ADAS\log-object-detection-firebase-adminsdk-svcpu-2a933d9402.json')  # Replace with your Firebase JSON path
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://log-object-detection-default-rtdb.firebaseio.com/'  # Replace with your Firebase Realtime Database URL
})

# Reference to the 'detection' node in Firebase
detection_ref = db.reference('detections')

# Endpoint to fetch all UIDs and corresponding data from 'detection' child
@app.route('/api/detection_data', methods=['GET'])
def get_detection_data():
    try:
        # Retrieve all data under the 'detection' child
        detection_data = detection_ref.get()

        if detection_data:
            return jsonify(detection_data), 200
        else:
            return jsonify({"message": "No data found in detection"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to store road curvature as angle
@app.route('/api/store/curvature', methods=['POST'])
def store_curvature():
    try:
        uid = request.json.get('uid')  # Accept UID in the request
        angle = request.json.get('angle')

        if not uid or angle is None:
            return jsonify({"error": "UID and angle are required"}), 400

        # Store the curvature angle under the specific UID
        detection_ref.child(uid).child('curvature_angle').set(angle)
        return jsonify({"message": "Curvature angle stored successfully", "curvature_angle": angle}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to store distance from the front vehicle
@app.route('/api/store/distance', methods=['POST'])
def store_distance():
    try:
        uid = request.json.get('uid')  # Accept UID in the request
        distance = request.json.get('distance')

        if not uid or distance is None:
            return jsonify({"error": "UID and distance are required"}), 400

        # Store the front vehicle distance under the specific UID
        detection_ref.child(uid).child('front_vehicle_distance').set(distance)
        return jsonify({"message": "Distance stored successfully", "front_vehicle_distance": distance}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Main entry point of the Flask app
if __name__ == '__main__':
    app.run(debug=True)
