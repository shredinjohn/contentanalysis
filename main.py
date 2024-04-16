import streamlit as st
import webbrowser
from app import extract_transcript_details,generate_gemini_content,video_comments,preprocess_comments,sentiment
from pages.visualization import visualize_sentiments
import os
import pandas as pd

st.set_page_config(page_title="Ai Content Analyzer", page_icon=":robot_face:", layout="wide")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)
# App UI
title_col1,title_col2 = st.columns([0.85,0.15])
with title_col1:
    st.title("Content Analysis using Gemini AI")
with title_col2:
    st.write("  ")
    st.write("  ")
    st.toggle("Notebook Mode")

col1,col2 = st.columns(2)
    
with col1:
    youtube_link = st.text_input("Enter the YouTube URL: ")
    if youtube_link:
        video_id = youtube_link.split("=")[1]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width="auto")
        
with col2:
    st.markdown("""
    ### How to Use This App?

    1. **Find the video on YouTube** that you want to analyze the content of.
    2. **Copy the video URL** which contains the YouTube ID. It should look like this: https://www.youtube.com/watch?v=V6DJYGn2SFk
    3. **Click on "Run Analysis"** 🔁

    **Note:** If you encounter an error such as "Transcript not found" or "Transcript disabled", you may need to upload the transcript of the video. To do this, click on the link below to generate the transcript for the video.
    """)

    if st.button("Generate Transcript"):
        webbrowser.open('http://www.google.com')

    fl = st.file_uploader("🗃️ Upload the Transcript",type=("txt"))    
    if fl is not None:
        filename = fl.name
        st.write(filename)

if st.button("Run Analysis 🔁"):
    
    with st.spinner("Loading"):
        transcript_text=extract_transcript_details(youtube_link)
        if transcript_text:
            summary=generate_gemini_content(transcript_text)
            st.write(summary)
        video_comments(video_id,os.getenv("YOUTUBE_API_KEY"))
        preprocess_comments('comments.csv', 'comments_filtered.csv')
        sentiment(summary)
        st.subheader("Sentiment Distribution")
        st.switch_page("pages/visualization.py")
    

