import os
from flask import Flask, request, jsonify
from transformers import pipeline
import torch

# Initialize Flask application
app = Flask(__name__)

# Print the version of PyTorch and whether CUDA (GPU support) is available
print(torch.__version__)
print("CUDA available:", torch.cuda.is_available())

# Initialize the sentiment analysis pipeline with a pre-trained model
pipe = pipeline("text-classification", model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")


# Function to perform sentiment analysis on a list of news articles
def analyze(news):
    result_list = []  # List to store sentiment analysis results
    for new in news:
        result = pipe(new)  # Perform sentiment analysis using the pipeline
        result_list.append({
            "news": new,  # Original news text
            "sentiment": result[0]['label'],  # Sentiment label (positive/negative)
            "score": result[0]['score']  # Confidence score of the sentiment prediction
        })
    return result_list


# Route to analyze the sentiment of a list of news articles
@app.route("/analyze-sentiment", methods=["POST"])
def analyze_sentiment():
    try:
        # Extract the JSON data from the request
        data = request.get_json()

        # Check if 'text' field is present in the request data
        if not data or "text" not in data:
            return jsonify({"error": "Please provide a 'text' field in JSON payload"}), 400

        # Ensure the 'text' field is a list, convert it if necessary
        text = data["text"]
        if not isinstance(text, list):
            text = [text]

        # Perform sentiment analysis on the provided texts
        result = analyze(text)
        return jsonify({"results": result}), 200  # Return the analysis results as JSON

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500  # Return error if any exception occurs


# Run the Flask application
if __name__ == "__main__":
    port = os.getenv("PORT", 5000)  # Get the port number from environment variable or default to 5000
    app.run(debug=True, host='0.0.0.0', port=port)  # Start the Flask app in debug mode
