import streamlit as st
import webbrowser
from app import extract_transcript_details,generate_gemini_content,video_comments,preprocess_comments,sentiment
import os

summary=""
context=""

st.set_page_config(page_title="Ai Content Analyzer", page_icon=":robot_face:", layout="wide")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)
# App UI
title_col1,title_col2 = st.columns([0.85,0.15])
col1,col2 = st.columns(2)

with title_col1:
    st.title("Content Analysis using Gemini AI")
with title_col2:
    st.write("  ")
    st.write("  ")
    if st.toggle("Custom Context"):
        custom=True
    else:
        custom=False
    
with col1:
    youtube_link = st.text_input("Enter the YouTube URL: ")
    if youtube_link:
        video_id = youtube_link.split("=")[-1]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width="auto")

        with open('youtube_link.txt', 'w') as file:
            file.write(youtube_link)

with col2:
    if custom:
        with st.spinner("Loading"):
            st.markdown("""
            **How to use Custom Context:**
            1. **Identify the specific video**: Determine which video you want to analyze using the custom context.
            2. **Describe the context**: Write a detailed description of the context for the selected video. This should include any relevant information that will aid in the analysis of the video.
            3. **Review your description**: After writing the description, review it to ensure that it accurately represents the context of the video.
            4. **Click 'Run Analysis'**: Click 'Run Analysis' after finalizing the description to start video analysis based on the provided context.
                    """)
            context = st.text_area(label="Custom Context",placeholder="Enter your custom context here :",height=150)
    else:
        st.markdown("""
        ### How to Use This App?

        1. **Find the video on YouTube** that you want to analyze the content of.
        2. **Copy the video URL** which contains the YouTube ID. It should look like this: https://www.youtube.com/watch?v=V6DJYGn2SFk
        3. **Click on "Run Analysis"** 🔁

        **Note:** If you encounter an error such as "Transcript not found" or "Transcript disabled", you may need to upload the transcript of the video. To do this, click on the link below to generate the transcript for the video.
        """)

        if st.button("Generate Transcript"):
            webbrowser.open('https://colab.research.google.com/drive/1KKKMx6gCYw5gJWnXDCK-RjQXKkx5cFz-?usp=sharing')

        fl = st.file_uploader("🗃️ Upload the Transcript",type=("txt"))    
        if fl is not None:
            filename = fl.name
            st.write(filename)
            isFile = True
        else:
            isFile = False


def get_youtube_link():
    return youtube_link


if st.button("Run Analysis 🔁"):
    if not custom:
        with st.spinner("Loading : Generating Context"):
            if isFile:
                with open(filename, 'r') as file:
                    file_content = file.read()
                    summary = generate_gemini_content(file_content)
            else:
                transcript_text=extract_transcript_details(youtube_link)
                if transcript_text:
                    summary=generate_gemini_content(transcript_text)
                    st.write(summary)
            with open('youtube_link.txt', 'a') as file:
                file.write("\n" + summary)
    else:
        summary = generate_gemini_content(context)
    with st.spinner("Loading : Downloading and Preprocessing Comments"):
        video_comments(video_id,os.getenv("YOUTUBE_API_KEY"))
        preprocess_comments('comments.csv', 'comments_filtered.csv')
    with st.spinner("Loading : Analyzing the comments"):
        if custom:
            sentiment(context)
        else:
            sentiment(summary)
        st.subheader("Sentiment Distribution")
        st.switch_page("pages/visualization.py")
    

