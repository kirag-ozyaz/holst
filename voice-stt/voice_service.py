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
    temp_path = os.path.join("temp", f"temp_{os.getpid()}.wav")
    Path("temp").mkdir(exist_ok=True)
    audio_file.save(temp_path)

    try:
        # Initialize recognizer
        rec = vosk.KaldiRecognizer(model, 16000)

        # Read and process audio in chunks
        with open(temp_path, "rb") as f:
            data = f.read()

        # Process in 4000 byte chunks (100ms at 16kHz, 16-bit)
        chunk_size = 4000
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            rec.AcceptWaveform(chunk)

        result = json.loads(rec.FinalResult())
        text = result.get("text", "")

        return jsonify({"text": text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)