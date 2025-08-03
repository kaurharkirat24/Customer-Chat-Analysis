import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import streamlit as st

def sentiment_to_color(sentiment):
    if sentiment in ['happy', 'positive']:
        return 'green'
    elif sentiment in ['angry', 'negative']:
        return 'red'
    else:
        return 'yellow'

def plot_sentiment_over_time(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    sentiment_score = df.groupby(df['timestamp'].dt.date)['sentiment'].apply(
        lambda x: (x == 'happy').sum() - (x == 'angry').sum()
    )
    colors = []
    for date in sentiment_score.index:
        day_sents = df[df['timestamp'].dt.date == date]['sentiment']
        if (day_sents == 'happy').sum() > (day_sents == 'angry').sum():
            colors.append('green')
        elif (day_sents == 'angry').sum() > (day_sents == 'happy').sum():
            colors.append('red')
        else:
            colors.append('yellow')
    plt.figure(figsize=(10, 5))
    plt.scatter(sentiment_score.index, sentiment_score.values, color=colors, s=50)
    plt.plot(sentiment_score.index, sentiment_score.values, color='gray', alpha=0.5)
    plt.xlabel('Date')
    plt.ylabel('Sentiment Score')
    plt.title('Sentiment Over Time with Sentiment Direction Colors')
    plt.grid(True)

    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Positive', markerfacecolor='green', markersize=8),
        Line2D([0], [0], marker='o', color='w', label='Neutral', markerfacecolor='yellow', markersize=8),
        Line2D([0], [0], marker='o', color='w', label='Negative', markerfacecolor='red', markersize=8)
    ]
    plt.legend(handles=legend_elements, title='Sentiment Direction')
    plt.tight_layout()
    st.pyplot(plt)

def plot_chat_volume(df, by='day'):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    if by == 'day':
        data = df.groupby(df['timestamp'].dt.date)['message'].count()
        x_label = 'Date'
    elif by == 'hour':
        data = df.groupby(df['timestamp'].dt.hour)['message'].count()
        x_label = 'Hour of Day'
    else:
        return
    plt.figure(figsize=(12,6))
    data.plot(kind='bar', color='skyblue')
    plt.xlabel(x_label)
    plt.ylabel('Number of Messages')
    plt.title('Chat Volume by ' + ('Day' if by == 'day' else 'Hour'))
    plt.grid(axis='y')
    plt.tight_layout()
    st.pyplot(plt)

def scatter_sentiment_volume(sentiment_df):
    """
    Scatter plot of Sentiment Score vs. Date,
    colored by sentiment label and sized by chat volume.
    Sentiment_df should have columns: 'date', 'sentiment_score', 'sentiment_label', 'chat_volume'
    """
    color_map = {'positive': 'green', 'neutral': 'yellow', 'negative': 'red'}
    colors = sentiment_df['sentiment_label'].map(color_map)
    sizes = sentiment_df['chat_volume']  # Adjust scaling as needed for better visuals

    plt.figure(figsize=(10, 5))
    plt.scatter(
        sentiment_df['date'],
        sentiment_df['sentiment_score'],
        c=colors,
        s=sizes,
        alpha=0.7,
        edgecolors='k'
    )
    plt.title('Sentiment and Chat Volume Over Time')
    plt.xlabel('Date')
    plt.ylabel('Sentiment Score')
    plt.grid(True)

    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Positive', markerfacecolor='green', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='Neutral', markerfacecolor='yellow', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='Negative', markerfacecolor='red', markersize=10)
    ]
    plt.legend(handles=legend_elements, title='Sentiment Direction', loc='upper left')
    plt.tight_layout()
    st.pyplot(plt)
