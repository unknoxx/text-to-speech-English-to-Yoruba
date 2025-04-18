from flask import Flask, request, jsonify
from flask_cors import CORS
from gtts import gTTS
import requests
import os
import base64

app = Flask(__name__)
CORS(app)

# LibreTranslate API endpoint (use a public instance or host your own)
LIBRETRANSLATE_URL = "https://translate.argosopentech.com/translate"

def translate_to_yoruba(text):
    try:
        response = requests.post(LIBRETRANSLATE_URL, json={
            "q": text,
            "source": "en",
            "target": "yo"
        })
        if response.ok:
            return response.json().get("translatedText", text)
        return text  # Fallback to original text if translation fails
    except Exception as e:
        print(f"Translation error: {e}")
        return text

@app.route('/synthesize', methods=['POST'])
def synthesize():
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return jsonify({"error": "No text provided"}), 400

    # Translate English to Yoruba
    yoruba_text = translate_to_yoruba(text)

    # Generate speech with gTTS
    try:
        tts = gTTS(text=yoruba_text, lang='yo')
        audio_file = "output.mp3"
        tts.save(audio_file)

        # Read audio file and encode to base64
        with open(audio_file, "rb") as f:
            audio_data = f.read()
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')

        # Clean up
        os.remove(audio_file)

        # Return audio as data URL
        audio_url = f"data:audio/mp3;base64,{audio_base64}"
        return jsonify({"audioUrl": audio_url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)