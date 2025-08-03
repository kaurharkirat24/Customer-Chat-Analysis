from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

def get_sentiment(message):
    scores = sia.polarity_scores(message)
    compound = scores["compound"]
    if compound >= 0.5:
        return "happy"
    elif compound <= -0.5:
        return "angry"
    else:
        return "neutral"

def aggregate_sentiment(df):
    # Returns stats per user
    if 'user' not in df.columns or 'sentiment' not in df.columns:
        return None
    return df.groupby('user')['sentiment'].value_counts().unstack().fillna(0)
