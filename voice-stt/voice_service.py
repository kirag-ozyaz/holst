from flask import Flask, request, jsonify
from flask_cors import CORS
import vosk
import json
import os
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Initialize Vosk model (assuming model is downloaded locally)
MODEL_PATH = "model"
if not os.path.exists(MODEL_PATH):
    print("Vosk model not found. Please download a Russian model.")
    model = None
else:
    model = vosk.Model(MODEL_PATH)

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if not model:
        return jsonify({"error": "Vosk model not loaded"}), 500

    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']

    # Save audio temporarily
    temp_path = f"temp_{os.getpid()}.wav"
    audio_file.save(temp_path)

    try:
        # Initialize recognizer
        rec = vosk.KaldiRecognizer(model, 16000)

        # Read and process audio
        with open(temp_path, "rb") as f:
            data = f.read()

        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get("text", "")
        else:
            result = json.loads(rec.PartialResult())
            text = result.get("partial", "")

        # Clean up
        os.remove(temp_path)

        return jsonify({"text": text})

    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)