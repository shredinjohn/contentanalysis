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

summary = ""

json_prompt = """

This is how you used respond in JSON ,
{
   "context": "YOUR_CONTEXT_HERE",
}

"""

json_prompt_2 = """
This is how you used respond in JSON ,
{
    "positive": [
        {"user": "@user1", "tone": "happy"},
        {"user": "@user2", "tone": "appreciating"}
    ],
    "negative": [
        {"user": "@user3", "tone": "sad"},
        {"user": "@user4", "tone": "angry"}
    ]
}
"""

prompt=f""" 
    Given the transcript of a video, write a concise and accurate context for the video. In this context,
    when analyzing viewer feedback, consider it positive if the comments align with the video content or support the speaker’s narrative, even if they share negative personal experiences. However, treat feedback as negative if viewers express disagreement with the content, derive no value from the video, or share experiences that contradict the speaker’s perspective or the video’s context. Your analysis should reflect the sentiment of the feedback based on its contribution to the discourse surrounding the video content.
    write it in about 120-150 words ONLY.
    YOU MUST ANSWER ONLY IN JSON,
    Here is the transcript
    {json_prompt}
"""

prompt2="""
    You are an AI content summarizer. Your role is to analyze the provided data about viewer comments and determine whether the sentiment towards the video is positive or negative. Based on this data, you generate a concise summary. This summary aids the content creator in quickly understanding the viewers’ feelings about their video.
    Dont mention the overall sentiment title and tell the video is positive or negative .The user just needs the summary of it with detailed points for both positive and negative and no need of sub heading like postive points or negative points ,  i just need points thats all and mention all every single one suggestion (like technical diffculty, video on something , etc ... ) summarized at the bottom of the overall summary.
"""

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

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
        temperature=0.2,  
        max_output_tokens=2048
    )
    safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT : HarmBlockThreshold.BLOCK_NONE
    }

    
    response=model.generate_content(prompt,safety_settings=safety_settings,generation_config=generation_config)
    # Remove specified strings from the response text
    cleaned_text = response.text.replace('```json', '').replace('```', '')
    
    return cleaned_text


#generating summarize from the transcript 
def generate_gemini_content(transcript_text):
    model=genai.GenerativeModel("gemini-1.5-pro-latest")
    generation_config = genai.GenerationConfig(
        temperature=0
    )
    safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT : HarmBlockThreshold.BLOCK_NONE
    }
    response=model.generate_content(prompt+transcript_text,safety_settings=safety_settings,generation_config=generation_config)
    print(response.text)
    return response.text[7:-5]

#generating summarize from the positive and negative comments 
def generate_gemini_sentiment_summary(df):
    model=genai.GenerativeModel("gemini-1.5-pro-latest")
    generation_config = genai.GenerationConfig(
        temperature=0
    )
    safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT : HarmBlockThreshold.BLOCK_NONE
    }
    response=model.generate_content(prompt2+df,safety_settings=safety_settings,generation_config=generation_config)
    print(response.text)
    return response.text
    
def sentiment(summary):
    # Read the CSV file
    df = pd.read_csv('comments_filtered.csv')
    
    my_bar = st.progress(0)

    # Loop through the entire CSV file taking 80 rows each time
    for i in range(0, len(df), 80):
        my_bar.progress(i / len(df))

        # Convert the rows into a string
        comments = df.iloc[i:i+80].to_string(index=False)

        prompt = f"""
        You are an AI model who speaks only in JSON and designed to analyze the sentiment of user comments and categorize them as either positive or negative. Your task is to process a set of comments and output the results in a structured JSON format. The JSON output should contain two keys: ‘positive’ and ‘negative’. The values for these keys should be lists containing only the userIDs of the commenters, not the comments themselves.
        Here is the context of the video , {summary} In this context,
        when analyzing viewer feedback, consider it positive if the comments align with the video content or support the speaker’s narrative, even if they share negative personal experiences. However, treat feedback as negative if viewers express disagreement with the content, derive no value from the video, or share experiences that contradict the speaker’s perspective or the video’s context. Your analysis should reflect the sentiment of the feedback based on its contribution to the discourse surrounding the video content.
        Please analyze the following comments and categorize them as either ‘Positive’ or ‘Negative’ based on their sentiment and also analyze the tone well enough according to the given context. 

        Here are some tones that you are required to use
        Positive Tones: Joyful, Excited, Confident, Surprised, Peaceful, Loving, Hopeful, Optimistic, Amused, Content, Proud, Grateful, Appreciative, Ecstatic
        Negative Tones: Sad, Angry, Fearful, Pessimistic, Frustrated, Anxious, Disappointed, Gloomy, Depressed, Irritated, Resentful, Envious, Bitter, Worried
        BUT USE ONLY MAX OF 5-7 tones. DONT use more than 7 tones.
        {json_prompt_2}      
        Comments: {comments}
        """

        sentiments_json = generate_gemini_summary(prompt)
        print(sentiments_json)

        # Parse the JSON string into a dictionary
        sentiments = json.loads(sentiments_json)

        # Extract positive and negative usernames and tones
        positive_users = [entry["user"] for entry in sentiments["positive"]]
        positive_tones = [entry["tone"].lower() for entry in sentiments["positive"]]
        negative_users = [entry["user"] for entry in sentiments["negative"]]
        negative_tones = [entry["tone"].lower() for entry in sentiments["negative"]]

        def categorize_sentiment(user_id):
            if user_id in positive_users:
                index = positive_users.index(user_id)
                return "positive", positive_tones[index]
            elif user_id in negative_users:
                index = negative_users.index(user_id)
                return "negative", negative_tones[index]
            else:
                return None, None

        # Apply the function to the "User ID" column of the current batch
        df.loc[i:i+80, "sentiment"], df.loc[i:i+80, "tone"] = zip(*df.loc[i:i+80, "User ID"].apply(categorize_sentiment))

    my_bar.progress(1.0)
    # Save the DataFrame back to the CSV file after processing all batches
    df.to_csv('comments_filtered.csv', index=False)




        



