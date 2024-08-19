from transformers import pipeline

pipe = pipeline("sentiment-analysis")

def detect_sentiment(text):
    result = pipe(text)[0]
    label = result['label']
    score = result['score']
    
    print(f"Sentiment Label: {label}, Sentiment Score: {score}")  # Debugging output
    
    # Return label and score
    return score, label
