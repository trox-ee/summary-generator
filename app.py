
from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import re
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")

def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def get_transcript(video_id):
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join([t["text"] for t in transcript])

def summarize_text(text):
    if len(text) > 4000:
        text = text[:4000]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes videos."},
            {"role": "user", "content": f"Summarize this video transcript:\n{text}"}
        ]
    )
    return response["choices"][0]["message"]["content"]

@app.route("/summarize", methods=["POST"])
def summarize():
    data = request.get_json()
    url = data.get("url")
    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({"summary": "Invalid YouTube URL."}), 400

    try:
        transcript = get_transcript(video_id)
        summary = summarize_text(transcript)
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"summary": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
