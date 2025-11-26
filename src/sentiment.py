import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

def _ensure_lexicon_downloaded():
    """
    Checks if the VADER lexicon is present, downloads it if not.
    """
    try:
        nltk.data.find('sentiment/vader_lexicon.zip')
    except LookupError:
        print("Downloading VADER lexicon...")
        nltk.download('vader_lexicon', quiet=True)

def analyze_sentiment(text):
    """
    Analyzes a text string and returns the compound sentiment score.
    
    Args:
        text (str): The headline to analyze.
        
    Returns:
        float: Compound score between -1 (negative) and 1 (positive).
    """
    # 1. Safety check: If text is empty or None, return neutral (0.0)
    if not text or not isinstance(text, str):
        return 0.0

    # 2. Ensure resources are available
    _ensure_lexicon_downloaded()

    # 3. Initialize Analyzer
    vader = SentimentIntensityAnalyzer()

    # 4. Calculate scores
    # Returns dict like: {'neg': 0.0, 'neu': 0.5, 'pos': 0.5, 'compound': 0.3}
    scores = vader.polarity_scores(text)

    # 5. Return only the compound score
    return scores['compound']

# --- Test Block ---
if __name__ == "__main__":
    # Test with a few examples
    examples = [
        "Tesla stock crashes after CEO tweet",  # Should be negative
        "Apple reports record breaking profits", # Should be positive
        "Fed announces interest rate decision"   # Should be neutral
    ]
    
    print("--- Sentiment Tests ---")
    for ex in examples:
        score = analyze_sentiment(ex)
        print(f"Text: '{ex}'\nScore: {score}\n")