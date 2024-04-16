import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import os
from youtube_transcript_api import YouTubeTranscriptApi 
from datapreprocessing import preprocess_comments
from datapreprocessing import video_comments
load_dotenv()
import pandas as pd
import json
import plotly.express as px
import re

summary = ""

json_prompt = """
 DONT MENTION ```json at the start or ``` at the end
This is how you used respond in JSON ,
{
   "context": "YOUR_CONTEXT_HERE",
    "positiveReplies" : [
    "REPLY 1",
    "REPLY 2"
    ],
    "negativeReplies" : [
    "REPLY 1",
    "REPLY 2"
    ]
}
STRICTLY FOLLOW THIS, DO NOT MENTION "```json" at the start or "```" at the end .
"""

json_prompt_2 = """
 DONT MENTION ```json at the start or ``` at the end
This is how you used respond in JSON ,
{
    "positive": [
    "@user1",
    "@user2"
    ],
    "negative": [
    "@user3",
    "@user4"
    ]
}
STRICTLY FOLLOW THIS, DO NOT MENTION "```json" at the start or "```" at the end .
"""


genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
prompt=f""" 
Given the transcript of a video, write a concise and accurate context for the video. Additionally, identify what kind of replies could be considered positive or negative based on the context. In this context,
when analyzing viewer feedback, consider it positive if the comments align with the video content or support the speaker’s narrative, even if they share negative personal experiences. However, treat feedback as negative if viewers express disagreement with the content, derive no value from the video, or share experiences that contradict the speaker’s perspective or the video’s context. Your analysis should reflect the sentiment of the feedback based on its contribution to the discourse surrounding the video content.
YOU MUST ANSWER ONLY IN JSON, Variable names for positive replies and negative replies should like positiveReplies, negativeReplies , 
 Here is the transcript
 {json_prompt}
"""

#Getting the transcript from youtube videos
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript=""
        for i in transcript_text:
            transcript += " " + i["text"]
        return transcript

    except Exception as e:
        raise e

def generate_gemini_summary(prompt):
    model=genai.GenerativeModel("gemini-pro")
    generation_config = genai.GenerationConfig(
        temperature=0,
        top_k=3
    )
    safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT : HarmBlockThreshold.BLOCK_NONE
    }
    response=model.generate_content(prompt,safety_settings=safety_settings,generation_config=generation_config)
    return response.text


#generating summarize from the transcript 
def generate_gemini_content(prompt,transcript_text):
    model=genai.GenerativeModel("gemini-1.5-pro-latest")
    generation_config = genai.GenerationConfig(
        temperature=0,
        top_k=3
    )
    safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT : HarmBlockThreshold.BLOCK_NONE
    }
    response=model.generate_content(prompt+transcript_text,safety_settings=safety_settings,generation_config=generation_config)
    
    return response.text[7:-3]
    
def sentiment(positive_replies , negative_replies):
    # Read the CSV file
    df = pd.read_csv('comments_filtered.csv')

    # Loop through the entire CSV file taking 100 rows each time
    for i in range(0, len(df), 50):
        # Convert the rows into a string
        comments = df.iloc[i:i+50].to_string(index=False)

        prompt = f"""
        You are an AI model who speaks only in JSON and designed to analyze the sentiment of user comments and categorize them as either positive or negative. Your task is to process a set of comments and output the results in a structured JSON format. The JSON output should contain two keys: ‘positive’ and ‘negative’. The values for these keys should be lists containing only the userIDs of the commenters, not the comments themselves.
        Here are some example comments that have been categorized as positive: {positive_replies}. And here are some that have been categorized as negative: {negative_replies}. These examples are provided for context and should not be used to influence your analysis.
        Please analyze the following comments and categorize them as either ‘Positive’ or ‘Negative’ based on their sentiment. Note that you will receive more comments for analysis, so don’t assume that this is the complete set. Avoid considering emojis in comments which would something like :happy_face:, avoid those completely just sentiment using the texts only.
        
        {json_prompt_2}      
        Comments: {comments}
        """

        sentiments_json = generate_gemini_summary(prompt)

        # Parse the JSON string into a dictionary
        sentiments = json.loads(sentiments_json)

        # Extract positive and negative usernames
        positive_users = sentiments["positive"]
        negative_users = sentiments["negative"]

        def categorize_sentiment(user_id):
            if user_id in positive_users:
                print(user_id)
                return "positive"
            elif user_id in negative_users:
                return "negative"
            else:
                return None

        # Apply the function to the "User ID" column of the current batch
        df.loc[i:i+50, "sentiment"] = df.loc[i:i+50, "User ID"].apply(categorize_sentiment)

    # Save the DataFrame back to the CSV file after processing all batches
    df.to_csv('comments_filtered.csv', index=False)

def process_replies(summary):
    data = json.loads(summary)
    # Join the positive replies into a single string
    positive_replies = '\n'.join(data['positiveReplies'])
    # Join the negative replies into a single string
    negative_replies = '\n'.join(data['negativeReplies'])
    return positive_replies, negative_replies


def visualize_sentiments(df):
    sentiment_counts = df["sentiment"].value_counts().reset_index()
    sentiment_counts.columns = ['sentiment', 'count']
    fig = px.pie(sentiment_counts, values='count', names='sentiment')
    st.plotly_chart(fig)



# App UI
st.title("Content Analysis using Gemini AI")
youtube_link = st.text_input("Enter the YouTube URL: ")
if youtube_link:
    video_id = youtube_link.split("=")[1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
if st.button("Get Detailed Notes "):
    with st.spinner("Loading"):
        transcript_text=extract_transcript_details(youtube_link)
        if transcript_text:
            summary=generate_gemini_content(transcript_text,prompt)
            st.write(summary)
        video_comments(video_id,os.getenv("YOUTUBE_API_KEY"))
        preprocess_comments('comments.csv', 'comments_filtered.csv')
        positive_replies,negative_replies=process_replies(summary)
        sentiment(positive_replies,negative_replies)
        df = pd.read_csv("comments_filtered.csv")
        st.subheader("Sentiment Distribution")
        visualize_sentiments(df)
        st.balloons()
        



