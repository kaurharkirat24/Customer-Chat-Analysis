import streamlit as st
import pandas as pd
from helpers.data_loader import load_chat_file
from helpers.summarizer import summarize_conversation
from helpers.sentiment import get_sentiment, aggregate_sentiment
from helpers.faq_extractor import extract_faq, find_common_issues
from helpers.toxicity import flag_toxic
from helpers.visualize import plot_sentiment_over_time, plot_chat_volume
from helpers.classifiers import classify_message
from helpers.tone import analyze_tone

st.set_page_config("Customer Chat Log Analyzer", layout="wide")
st.title("Customer Chat Log Analyzer 🗨️")

uploaded_file = st.sidebar.file_uploader("Upload chat log (.csv, .json, .txt)", type=["csv", "json", "txt"])

if uploaded_file:
    df = load_chat_file(uploaded_file)
    if 'message' not in df.columns or 'user' not in df.columns:
        st.error("Uploaded file must contain at least 'user' and 'message' columns.")
        st.stop()

    df['sentiment'] = df['message'].apply(get_sentiment)
    df['is_toxic'] = df['message'].apply(flag_toxic)
    df['classification'] = df['message'].apply(classify_message)
    df['tone'] = df['message'].apply(analyze_tone)

    st.sidebar.markdown(f"**Total chats:** {df.shape[0]}")
    st.sidebar.markdown(f"**Unique users:** {df['user'].nunique()}")

    if st.sidebar.checkbox("Show sample data"):
        st.write(df.head())

    long_conv = "\n".join(df['message'].tolist())

    if st.button("Summarize Conversation"):
        with st.spinner("Generating summary..."):
            summary = summarize_conversation(long_conv)
        st.subheader("Conversation Summary")
        st.info(summary)

    st.subheader("Frequently Asked Questions (FAQs)")
    for q, count in extract_faq(df):
        st.markdown(f"- {q} ({count} times)")

    st.subheader("Common Customer Issues")
    for iss, count in find_common_issues(df):
        st.markdown(f"- {iss} ({count} times)")

    st.subheader("Sentiment Over Time")
    plot_sentiment_over_time(df)
    st.subheader("Chat Volume by Day")
    plot_chat_volume(df, by='day')

    st.subheader("Toxic Messages (Flagged)")
    toxic_msgs = df[df['is_toxic']]
    st.write(toxic_msgs[['timestamp', 'user', 'message']])

    st.subheader("Message Classification")
    st.write(df[['timestamp', 'user', 'message', 'classification']])

    st.subheader("Tone Analysis")
    st.write(df[['timestamp', 'user', 'message', 'tone']])

    st.subheader("Sentiment Aggregates by User")
    sentiment_agg = aggregate_sentiment(df)
    st.write(sentiment_agg)

else:
    st.info("Please upload a chat log to start analysis.")

st.markdown("---")
st.caption("Empowering support teams with actionable chat insights.")
