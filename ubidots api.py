from flask import Flask, request, jsonify
import requests
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)


UBIDOTS_TOKEN = "BBUS-qI1FWHJLau7saemIUOBscnuZRf1CFV"
UBIDOTS_DEVICE = "Esp32_Dht-Pir"
UBIDOTS_URL = f"https://industrial.api.ubidots.com/api/v1.6/devices/{UBIDOTS_DEVICE}/"

MONGO_URI = "mongodb+srv://AiRen:ai@cluster0.s6f6g.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client.get_database("sensor_database")
sensor_collection = db.get_collection("sensor_data")

def send_to_ubidots(suhu, kelembapan, gerakan):
    headers = {
        "Content-Type": "application/json",
        "X-Auth-Token": UBIDOTS_TOKEN
    }
    
    data = {
        "suhu": suhu,
        "kelembapan": kelembapan,
        "gerakan": gerakan
    }
    
    response = requests.post(UBIDOTS_URL, json=data, headers=headers)
    return response.status_code, response.text

@app.route('/sensor', methods=['POST'])
def receive_sensor_data():
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"status": "error", "message": "Invalid JSON"}), 400

        suhu = data.get("suhu")
        kelembapan = data.get("kelembapan")
        gerakan = data.get("gerakan")
        waktu = datetime.now()

        if suhu is None or kelembapan is None or gerakan is None:
            return jsonify({"status": "error", "message": "Missing fields"}), 400

        sensor_data = {
            "suhu": suhu,
            "kelembapan": kelembapan,
            "gerakan": gerakan,
            "waktu": waktu
        }
        inserted = sensor_collection.insert_one(sensor_data)
        
        status_code, ubidots_response = send_to_ubidots(suhu, kelembapan, gerakan)

        return jsonify({
            "status": "success",
            "message": "Data diterima",
            "mongodb_id": str(inserted.inserted_id),
            "ubidots_status": status_code,
            "ubidots_response": ubidots_response
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
