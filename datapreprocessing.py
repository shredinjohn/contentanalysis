import csv
import html
import emoji
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup
import pandas as pd


def video_comments(video_id,api_key):
    # Create youtube resource object
    youtube = build('youtube', 'v3', developerKey=api_key)

    # Open a CSV file for writing
    with open('comments.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Write the header row
        writer.writerow(['User ID', 'Comment', 'Replies'])

        # Start with the first page of comments
        next_page_token = None

        try:
            while True:
                # Retrieve youtube video results
                video_response = youtube.commentThreads().list(
                    part='snippet,replies',
                    videoId=video_id,
                    maxResults=100, # You can set the maximum number of comments to retrieve
                    pageToken=next_page_token
                ).execute()

                # Collect all comments in a batch
                batch_comments = []

                # Extract required info from each result object
                for item in video_response['items']:
                    # Extracting comments
                    comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                    # Remove HTML tags and emojis
                    comment = html.unescape(comment) # Convert HTML entities to characters
                    comment = emoji.demojize(comment) # Remove emojis
                    comment = html.unescape(comment) # Convert HTML entities back to characters
                    # Remove HTML tags using BeautifulSoup
                    soup = BeautifulSoup(comment, "html.parser")
                    comment = soup.get_text()

                    # Extracting username
                    username = item['snippet']['topLevelComment']['snippet']['authorDisplayName']

                    # Extract replies (if any)
                    replies = [reply['snippet']['textDisplay'] for reply in item['replies']['comments']] if 'replies' in item else []

                    # Remove HTML tags and emojis from replies using BeautifulSoup
                    replies = [html.unescape(emoji.demojize(html.unescape(reply))) for reply in replies]
                    replies = [BeautifulSoup(reply, "html.parser").get_text() for reply in replies]

                    # Add the comment and its replies to the batch
                    batch_comments.append([username, comment, ' | '.join(replies)])

                # Write the batch of comments to the CSV file
                writer.writerows(batch_comments)

                # Check if there's a next page of comments
                if 'nextPageToken' in video_response:
                    next_page_token = video_response['nextPageToken']
                else:
                    break # No more pages, exit the loop

        except HttpError as e:
            print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        except KeyError as e:
            print(f"A key error occurred: {e}")

# Enter video id
video_id = "fNCuVpWqAr0"

def preprocess_comments(input_file, output_file):
    # Load the CSV file into a DataFrame
    df = pd.read_csv(input_file)

    # Create a mask to identify rows where the "Comment" or "Replies" column does not contain the specified text
    mask = ~(df['Comment'].str.contains('Below text is already commented') | df['Replies'].str.contains('Below text is already commented'))

    # Apply the mask to the DataFrame to filter out the rows with the unwanted text
    filtered_df = df.loc[mask]

    # Remove repeated comments from the same user
    df = df.drop_duplicates(subset=['User ID', 'Comment', 'Replies'])

    # Save the filtered DataFrame back to a CSV file
    filtered_df.to_csv(output_file, index=False)

