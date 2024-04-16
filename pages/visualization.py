import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit as st
6
df = pd.read_csv("comments_filtered.csv")

def visualize_sentiments(df):
    # Filter positive sentiments and count tones
    positive_df = df[df['sentiment'] == 'positive']
    positive_tones = positive_df['tone'].value_counts().reset_index()
    positive_tones.columns = ['tone', 'count']

    # Create pie chart for positive sentiments
    positive_fig = px.pie(positive_tones, values='count', names='tone', title='Positive Sentiments by Tone')
    st.plotly_chart(positive_fig)

    # Filter negative sentiments and count tones
    negative_df = df[df['sentiment'] == 'negative']
    negative_tones = negative_df['tone'].value_counts().reset_index()
    negative_tones.columns = ['tone', 'count']

    # Create pie chart for negative sentiments
    negative_fig = px.pie(negative_tones, values='count', names='tone', title='Negative Sentiments by Tone')
    st.plotly_chart(negative_fig)

visualize_sentiments(df)