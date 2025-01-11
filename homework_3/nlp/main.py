import os

from flask import Flask, request, jsonify
from transformers import pipeline
import torch

app = Flask(__name__)

# Print CUDA availability
print(torch.__version__)
print("CUDA available:", torch.cuda.is_available())

# Initialize the sentiment analysis pipeline
pipe = pipeline("text-classification", model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")

def analyze(news):
    result_list = []
    for new in news:
        result = pipe(new)
        result_list.append({
            "news": new,
            "sentiment": result[0]['label'],
            "score": result[0]['score']
        })
    return result_list

@app.route("/analyze-sentiment", methods=["POST"])
def analyze_sentiment():
    try:
        # Extract data from the request
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Please provide a 'text' field in JSON payload"}), 400

        # Ensure the input is a list
        text = data["text"]
        if not isinstance(text, list):
            text = [text]

        # Perform sentiment analysis
        result = analyze(text)
        return jsonify({"results": result}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = os.getenv("PORT", 5000)
    app.run(debug=True, host='0.0.0.0', port=port)
