# Use a pipeline as a high-level helper
from transformers import pipeline
import torch

print(torch.__version__)
print("CUDA available:", torch.cuda.is_available())

pipe = pipeline("text-classification", model="mrm8488/distilroberta-finetuned-financial-news-sentiment-analysis")

# Test with example financial news
example_news = [
    "Komercijalna Banka reported a surge in profits this quarter.",
    "NLB Banka faces challenges due to regulatory changes.",
    "Stopanska Banka invests in new fintech startups.",
    "Global economy sees a downturn, experts worry about emerging markets."
]

def analyze(news):
    result_list = list()
    for new in news:
        print("analyzing")
        result = pipe(new)
        print(f"News: {new}")
        print(f"Sentiment: {result[0]['label']}, Confidence: {result[0]['score']:.4f}\n")
        result_list.append({"news": new, "sentiment": result[0]['label'], "score": result[0]['score']})

    return result_list

if __name__ == "__main__":
    # Analyze sentiment for each news item
    analyze(example_news)

