import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit as st
from main import youtube_link,summary
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
load_dotenv()

df = pd.read_csv("comments_filtered.csv")

# Build the YouTube service
youtube = build('youtube', 'v3', developerKey='YOUTUBE_API_KEY')


video_id = youtube_link.split("=")[-1]

# Create an HTML iframe for the YouTube video
youtube_embed_url = f"https://www.youtube.com/embed/{video_id}"
youtube_iframe = f"""
<iframe width="560" height="315" src="{youtube_embed_url}" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>
"""

# Layout
top_col1, top_col2 = st.columns([0.9, 0.1])

with top_col1:
    st.title("Content Analysis Report")

with top_col2:
    st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)
    st.write(" ")
    if st.button("Home 🏠"):
        st.switch_page("main.py")

video_col1, video_col2, video_col3 = st.columns([0.4, 0.4, 0.2])

# Display video in column 1
with video_col1:
    st.video("https://www.youtube.com/watch?v=fZCzSbGHhXM")

# Display summary in column 2
with video_col2:
    st.write("This is the context for the video")

# Display subscriber count and like count in column 3
with video_col3:
    # Since we're not using the YouTube Data API, we can't get real-time data
    # You would need to manually update these values
    subscriber_count = "N/A"  # Replace with the actual subscriber count
    likes = "N/A"  # Replace with the actual like count
    st.metric(label='Subscriber Count', value=subscriber_count, delta_color='normal')
    st.metric(label='Likes', value=likes, delta_color='normal')


def visualize_sentiments(df):
    # Filter positive sentiments and count tones
    positive_df = df[df['sentiment'] == 'positive']
    positive_tones = positive_df['tone'].value_counts().reset_index()
    positive_tones.columns = ['tone', 'count']

    # Create pie chart for positive sentiments
    positive_fig = px.pie(positive_tones, values='count', names='tone', title='Positive Sentiments')

    # Create two columns in Streamlit with sizes 30% and 70%
    col1, col2 = st.columns([0.3, 0.7])

    # Display the pie chart in the left column with reduced size
    col1.plotly_chart(positive_fig, use_container_width=True)

    # Create a dropdown in the right column for selecting a tone, with 'All' as the default selection
    selected_tone = col2.selectbox('Select a tone', ['All'] + list(positive_tones['tone'].unique()), index=0)

    # Filter the DataFrame based on the selected tone, or show all tones if 'All' is selected
    if selected_tone == 'All':
        filtered_df = positive_df
    else:
        filtered_df = positive_df[positive_df['tone'] == selected_tone]

    # Display the filtered DataFrame in the right column
    col2.dataframe(filtered_df)

    negative_df = df[df['sentiment'] == 'negative']
    negative_tones = negative_df['tone'].value_counts().reset_index()
    negative_tones.columns = ['tone', 'count']

    # Create pie chart for negative sentiments
    negative_fig = px.pie(negative_tones, values='count', names='tone', title='Negative Sentiments')

    # Create two more columns in Streamlit with sizes 30% and 70%
    col3, col4 = st.columns([0.3, 0.7])

    # Display the pie chart in the left column with reduced size
    col3.plotly_chart(negative_fig, use_container_width=True)

    # Create a dropdown in the right column for selecting a tone, with 'All' as the default selection
    selected_tone = col4.selectbox('Select a tone', ['All'] + list(negative_tones['tone'].unique()), index=0)

    # Filter the DataFrame based on the selected tone, or show all tones if 'All' is selected
    if selected_tone == 'All':
        filtered_df = negative_df
    else:
        filtered_df = negative_df[negative_df['tone'] == selected_tone]

    # Display the filtered DataFrame in the right column
    col4.dataframe(filtered_df)

    

visualize_sentiments(df)