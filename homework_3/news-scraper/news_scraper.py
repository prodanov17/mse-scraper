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
        self.max_concurrent_requests = max_concurrent_requests  # Set maximum concurrent requests

    # Method to fetch the list of news links for a specific issuer
    def fetch_news_links(self, issuer):
        url = self.base_url.format(issuer=issuer)  # Format URL with the issuer
        try:
            response = requests.get(url, timeout=15)  # Send request to fetch the page
            response.raise_for_status()  # Raise an error if the response code is not successful
            page_content = response.text  # Get the HTML content of the page
            soup = BeautifulSoup(page_content, "html.parser")  # Parse the HTML using BeautifulSoup
            news_links = soup.select('#seiNetIssuerLatestNews a')  # Select all news links from the page
            return [
                {
                    "news_id": self.extract_news_id(link["href"]),  # Extract news ID from the link
                    "date": self.extract_date(
                        link.select_one("ul li:nth-child(2) h4").text
                    ) if link.select_one("ul li:nth-child(2) h4") else None,  # Extract date if available
                }
                for link in news_links if "href" in link.attrs  # Filter out links that don't have href
            ]
        except Exception as e:
            return {"error": str(e)}  # Return error message if any exception occurs

    # Helper function to extract the news ID from the link URL
    def extract_news_id(self, url):
        return url.split("/")[-1]

    # Helper function to extract date from the date string
    def extract_date(self, date_str):
        try:
            match = re.search(r"\d{1,2}/\d{1,2}/\d{4}", date_str)  # Match date in MM/DD/YYYY format
            if match:
                return datetime.strptime(match.group(), "%m/%d/%Y").date().isoformat()  # Convert to ISO format
        except Exception:
            return None  # Return None if date extraction fails

    # Method to fetch detailed news content using the news ID
    def fetch_news_content(self, news_id):
        url = self.text_url.format(news_id=news_id)  # Format URL with news ID
        try:
            response = requests.get(url, timeout=15)  # Send request to fetch news content
            if response.status_code == 200:
                data = response.json()  # Parse JSON response
                content = data.get("data", {}).get("content")  # Extract content from the JSON data
                return re.sub(r"<[^>]*>", "", content) if content else None  # Clean up HTML tags and return content
        except Exception as e:
            return {"error": str(e)}  # Return error message if any exception occurs

# Instantiate the NewsScraper object
scraper = NewsScraper()

# Helper function to analyze sentiment of news content
def analyze(news_contents):
    requests.post("http://nlp:5000/sentiment", json={"text": news_contents})  # Send the contents for sentiment analysis

# Method to analyze sentiment based on news content
def analyze_sentiment(news_contents):
    # Assuming the analyze function processes the contents and returns sentiment analysis results
    sentiment_results = analyze(news_contents)
    if sentiment_results:
        # Calculate sentiment mode and score based on results
        sentiment = statistics.mode([item['sentiment'] for item in sentiment_results])
        score = sum(item['score'] for item in sentiment_results) / len(sentiment_results) if sentiment_results else 0
        return {
            "sentiment": sentiment,
            "score": score
        }
    return {"error": "Unable to perform sentiment analysis."}

# Endpoint to fetch news links for a specific issuer
@app.route("/news/<string:issuer>", methods=["GET"])
def get_news_links(issuer):
    news_links = scraper.fetch_news_links(issuer)  # Fetch news links for the issuer
    if isinstance(news_links, dict) and "error" in news_links:
        return jsonify({"error": news_links["error"]}), 500  # Return error if fetching links fails
    return jsonify(news_links)  # Return the fetched news links as JSON

# Endpoint to fetch the content of a specific news article based on news ID
@app.route("/news/content/<string:news_id>", methods=["GET"])
def get_news_content(news_id):
    content = scraper.fetch_news_content(news_id)  # Fetch the content for the news ID
    if isinstance(content, dict) and "error" in content:
        return jsonify({"error": content["error"]}), 500  # Return error if fetching content fails
    return jsonify({"news_id": news_id, "content": content})  # Return the content as JSON

# Endpoint to fetch the sentiment of the news for a specific issuer
@app.route("/news/<string:issuer>/sentiment", methods=["GET"])
def get_news_sentiment(issuer):
    # Fetch news links for the issuer
    news_links = scraper.fetch_news_links(issuer)
    if isinstance(news_links, dict) and "error" in news_links:
        return jsonify({"error": news_links["error"]}), 500  # Return error if fetching links fails

    # Fetch content for each news item
    news_contents = []
    for news in news_links:
        content = scraper.fetch_news_content(news["news_id"])
        if content:
            news_contents.append(content)

    # Perform sentiment analysis on the news contents
    news_contents = [item[:513] for item in news_contents]  # Limit content length to 513 characters
    sentiment_data = analyze_sentiment(news_contents)

    if "error" in sentiment_data:
        return jsonify({"error": sentiment_data["error"]}), 500  # Return error if sentiment analysis fails

    return jsonify({
        "key": issuer,
        "score": sentiment_data["score"],
        "sentiment": sentiment_data["sentiment"]
    })  # Return sentiment data as JSON

# Start the Flask application
if __name__ == "__main__":
    port = os.getenv("PORT", 5000)  # Get port from environment variable or default to 5000
    app.run(debug=True, host='0.0.0.0', port=port)  # Run the app in debug mode
