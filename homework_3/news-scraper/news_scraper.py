import os

from flask import Flask, jsonify, request
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import statistics

# Initialize Flask application
app = Flask(__name__)

# Define the NewsScraper class to handle fetching news and analyzing sentiment
class NewsScraper:
    def __init__(self, max_concurrent_requests=10):
        # Base URL for fetching news links and content URL for fetching detailed news content
        self.base_url = "https://www.mse.mk/en/symbol/{issuer}"
        self.text_url = "https://api.seinet.com.mk/public/documents/single/{news_id}"
        self.max_concurrent_requests = max_concurrent_requests

    # Method to fetch the list of news links for a specific issuer
    def fetch_news_links(self, issuer):
        url = self.base_url.format(issuer=issuer)
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            page_content = response.text
            soup = BeautifulSoup(page_content, "html.parser")
            news_links = soup.select('#seiNetIssuerLatestNews a')
            return [
                {
                    "news_id": self.extract_news_id(link["href"]),
                    "date": self.extract_date(
                        link.select_one("ul li:nth-child(2) h4").text
                    ) if link.select_one("ul li:nth-child(2) h4") else None,
                }
                for link in news_links if "href" in link.attrs
            ]
        except Exception as e:
            return {"error": str(e)}

    def extract_news_id(self, url):
        return url.split("/")[-1]

    def extract_date(self, date_str):
        try:
            match = re.search(r"\d{1,2}/\d{1,2}/\d{4}", date_str)
            if match:
                return datetime.strptime(match.group(), "%m/%d/%Y").date().isoformat()
        except Exception:
            return None

    def fetch_news_content(self, news_id):
        url = self.text_url.format(news_id=news_id)
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                content = data.get("data", {}).get("content")
                return re.sub(r"<[^>]*>", "", content) if content else None
        except Exception as e:
            return {"error": str(e)}

# Instantiate the NewsScraper object
scraper = NewsScraper()

# Helper function to analyze sentiment of news content
def analyze(news_contents):
    # Send the request with the list of news contents
    response = requests.post("http://nlp:5000/sentiment", json={"text": news_contents})

    # If the request was successful, return the response in JSON format (the sentiment analysis results)
    if response.status_code == 200:
        return response.json()  # This will be an array of results
    else:
        return {"error": "Failed to analyze sentiment", "status_code": response.status_code}
# Method to analyze sentiment based on news content
def analyze_sentiment(news_contents):
    # Assuming the analyze function processes the contents and returns sentiment analysis results
    sentiment_results = analyze(news_contents)
    if sentiment_results:
        sentiment = statistics.mode([item['sentiment'] for item in sentiment_results])
        score = sum(item['score'] for item in sentiment_results) / len(sentiment_results) if sentiment_results else 0
        return {
            "sentiment": sentiment,
            "score": score
        }
    return {"error": "Unable to perform sentiment analysis."}

@app.route("/news/<string:issuer>", methods=["GET"])
def get_news_links(issuer):
    news_links = scraper.fetch_news_links(issuer)
    if isinstance(news_links, dict) and "error" in news_links:
        return jsonify({"error": news_links["error"]}), 500
    return jsonify(news_links)

@app.route("/news/content/<string:news_id>", methods=["GET"])
def get_news_content(news_id):
    content = scraper.fetch_news_content(news_id)
    if isinstance(content, dict) and "error" in content:
        return jsonify({"error": content["error"]}), 500
    return jsonify({"news_id": news_id, "content": content})

# Endpoint to fetch the sentiment of the news for a specific issuer
@app.route("/news/<string:issuer>/sentiment", methods=["GET"])
def get_news_sentiment(issuer):
    # Fetch news links for the issuer
    news_links = scraper.fetch_news_links(issuer)
    if isinstance(news_links, dict) and "error" in news_links:
        return jsonify({"error": news_links["error"]}), 500

    # Fetch content for each news item
    news_contents = []
    for news in news_links:
        content = scraper.fetch_news_content(news["news_id"])
        if content:
            news_contents.append(content)

    # Perform sentiment analysis on the news contents
    news_contents = [item[:513] for item in news_contents]
    sentiment_data = analyze_sentiment(news_contents)

    if "error" in sentiment_data:
        return jsonify({"error": sentiment_data["error"]}), 500

    return jsonify({
        "key": issuer,
        "score": sentiment_data["score"],
        "sentiment": sentiment_data["sentiment"]
    })

# Start the Flask application
if __name__ == "__main__":
    port = os.getenv("PORT", 5000)
    app.run(debug=True, host='0.0.0.0', port=port)
