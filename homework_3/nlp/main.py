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

def analyze(sentence):
    result = pipe(sentence)[0]  # Analyze a single sentence
    return {"sentence": sentence, "sentiment": result['label'], "score": result['score']}

@app.route("/sentiment", methods=["POST"])
def analyze_sentiment():
    try:
        # Extract data from the request
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Please provide a 'text' field in JSON payload"}), 400

        # Get the sentence
        text = data["text"]
        if not isinstance(text, str):
            return jsonify({"error": "'text' field must be a single string"}), 400

        # Perform sentiment analysis
        result = analyze(text)
        return jsonify(result), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = os.getenv("PORT", 5000)
    app.run(debug=True, host='0.0.0.0', port=port)
