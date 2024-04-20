import streamlit as st
import os
import pandas as pd
import plotly.express as px
import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from app import generate_gemini_sentiment_summary
load_dotenv()

st.set_page_config(layout="wide")

df = pd.read_csv("comments_filtered.csv")
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY') 

youtube_link=""
video_context=""

# Read the link from the text file
if os.path.isfile('youtube_link.txt'):
    with open('youtube_link.txt', 'r') as file:
        youtube_link = file.readline().strip()

# Build the YouTube service
youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)


video_id = youtube_link.split("=")[-1]

try:
    video_response = youtube.videos().list(
        part='snippet,statistics',
        id=video_id
    ).execute()
    video_details = video_response['items'][0]

    likes = video_details['statistics'].get('likeCount', 'N/A')
except HttpError as e:
    st.error(f"An HTTP error occurred: {e}")
    st.stop()

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
    if youtube_link:
        st.video(youtube_link)

with open('youtube_link.txt', 'r') as file:
    lines = file.readlines()  # Read all lines into a list
    video_context = ""
    if len(lines) > 1:  # Ensure there's more than one line
        for line in lines[1:]:  # Start from the second line
            video_context += line.strip() + " "  # Append each line, stripping whitespace and adding a space

with video_col2:
    with video_col2:
        st.markdown(f"**Context of the given video**:    {video_context[15:-4]}", unsafe_allow_html=True)

# Display subscriber count and like count in column 3
with video_col3:
    # Count the number of positive and negative comments
    sentiment_counts = df['sentiment'].value_counts()
    positive_comments = sentiment_counts.get('positive', 0)
    negative_comments = sentiment_counts.get('negative', 0)

    # Calculate the total number of comments
    total_comments = len(df)

    # Calculate percentages
    positive_percentage = (positive_comments / total_comments) * 100 if total_comments else 0
    negative_percentage = (negative_comments / total_comments) * 100 if total_comments else 0

    # Now you can use positive_comments, negative_comments, positive_percentage, and negative_percentage as needed
    st.metric(label='Likes', value=likes, delta_color='normal')
    st.metric(label='Positive Comments %', value=f"{positive_percentage:.2f}%", delta_color='inverse')
    st.metric(label='Negative Comments %', value=f"{negative_percentage:.2f}%", delta_color='off')

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
    
    with st.spinner("Loading"):
        # Filter rows with positive sentiment
        positive_comments_df = df[df['sentiment'] == 'positive']
        # Concatenate all positive comments into a single string
        positive_comments_string = ' '.join(positive_comments_df['Comment'].astype(str))
        st.write(generate_gemini_sentiment_summary(positive_comments_string))


    negative_df = df[df['sentiment'] == 'negative']
    negative_tones = negative_df['tone'].value_counts().reset_index()
    negative_tones.columns = ['tone', 'count']

    # Create pie chart for negative sentiments
    negative_fig = px.pie(negative_tones, values='count', names='tone', title='Negative Sentiments')

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

    with st.spinner("Loading"):
        # Filter rows with negative sentiment
        negative_comments_df = df[df['sentiment'] == 'negative']
        # Concatenate all negative comments into a single string
        negative_comments_string = ' '.join(negative_comments_df['Comment'].astype(str))
        st.write(generate_gemini_sentiment_summary(negative_comments_string))

   
visualize_sentiments(df)