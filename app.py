# YouTube Video Summarizer
# This program gets transcripts from YouTube videos and makes summaries using AI
# Made for my programming class project

from youtube_transcript_api import YouTubeTranscriptApi
from gtts import gTTS
import google.generativeai as genai
from dotenv import load_dotenv
import os
from urllib.parse import urlparse, parse_qs

# Load the API key from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)
    print("Gemini AI is ready!")
else:
    print("Error: Need to add GEMINI_API_KEY to .env file")
    exit()

# Function to get video ID from YouTube URL
def get_video_id(url):
    parsed_url = urlparse(url)
    
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        video_id = parse_qs(parsed_url.query).get('v', [None])[0]
    elif parsed_url.hostname == 'youtu.be':
        video_id = parsed_url.path[1:]
    else:
        video_id = None
        
    return video_id

# Function to get transcript from YouTube
def get_transcript(video_id):
    try:
        api = YouTubeTranscriptApi()
        transcript_data = api.fetch(video_id, languages=['en', 'hi','fr'])
        text = " ".join([segment.text for segment in transcript_data])
        print(f"Got transcript: {len(text)} characters")
        return text
    except Exception as e:
        print(f"Couldn't get transcript: {e}")
        return None

# Functions for AI summary and notes
def generate_summary(text):
    """Generates a structured, concise summary using an improved prompt."""
    
    prompt = f"""
    You are an expert at creating highly concise and accurate summaries. Your task is to analyze the following video transcript and generate a summary that follows these strict rules:

    **Content Rules:**
    1.  **Be Extremely Concise:** The summary must be short and to the point. Extract only the most critical information.
    2.  **Maintain Accuracy:** Ensure the summary is a faithful representation of the transcript's main ideas.

    **Formatting Rules:**
    1.  **Use a numbered list (1., 2., 3., etc.) for the main topics.**
    2.  **Under each numbered point, you MAY use nested bullet points (* or -) for essential, brief details.**
    3.  **Do NOT use any Markdown headers (e.g., #, ##, ###).** The output should be a clean list.
    4.  ** make it under 150 words
    Here is the transcript:
    ---
    {text}
    ---
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        print("Making summary...")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error making summary: {e}")
        return "Sorry, couldn't make summary"

def generate_notes(text):
    """Generates concise, content-focused notes in a unique numbered format."""

    # This prompt is specifically designed to filter out fluff and use a clean format.
    """Generates concise, content-focused notes in a unique numbered format."""

    # This prompt is specifically designed to filter out fluff and use a clean format.
    # CORRECTED INDENTATION: This block is also now aligned correctly.
    prompt = f"""
You are an expert content distiller. Your task is to analyze the following transcript and produce a set of concise, high-impact notes in HINDI that focus exclusively on the core information.
* you you to give output in only english language, even if u get input trascript of any language
**Instructions:**

**1. Content Focus & Filtering:**
- **Distill the Core Message:** Extract the essential information—the "what" and the "why" of the video.
- **Ignore Conversational Filler:** You MUST completely ignore and exclude all non-essential content (introductions, calls to action like "like and subscribe," etc.).
- **Rephrase for Clarity:** Synthesize and rephrase the key points to make the notes unique and easy to understand.

**2. Formatting Rules:**
- **Use a Numbered List:** Structure the entire output as a clean, numbered list (1., 2., 3., etc.).
- **No Headers or Bullets:** You MUST NOT use any Markdown headers (#) or bullet points (*, -).
- **Use Bold for Emphasis:** Use **bold text** to highlight the most critical terms.

Here is the transcript to process:
---
{text}
---
"""
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        print("Making notes...")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error making notes: {e}")
        return "Sorry, couldn't make notes"


def text_to_audio(summary, filename="summary.mp3"):
    try:
        print("Making audio file...")
        tts = gTTS(text=summary, lang='en', slow=False)
        tts.save(filename)
        print(f"Audio saved: {filename}")
        return filename
    except Exception as e:
        print(f"Couldn't make audio: {e}")
        return None

# Main program
if __name__ == "__main__":
    print("YouTube Video Summarizer")
    print("=" * 24)
    
    yt_url = input("Enter YouTube URL: ").strip()
    
    video_id = get_video_id(yt_url)
    
    if not video_id:
        print("Invalid YouTube URL")
        print("Try: https://youtube.com/watch?v=VIDEO_ID")
        print("Or: https://youtu.be/VIDEO_ID")
    else:
        print(f"Video ID: {video_id}")
        print("Getting transcript...")
        
        transcript = get_transcript(video_id)
        
        if transcript:
            print("Got transcript!")
            print(f"Length: {len(transcript)} characters")
            
            while True:
                print("\n" + "="*30)
                print("What do you want to do?")
                print("  1. Make a summary")
                print("  2. Make notes") 
                print("  3. Make audio summary")
                print("  4. Exit")
                print("="*30)
                
                choice = input("Pick 1-4: ").strip()

                if choice == '1':
                    print("\nMaking summary...")
                    summary = generate_summary(transcript)
                    print("\n" + "="*40)
                    print("SUMMARY")
                    print("="*40)
                    print(summary)
                    print("="*40)
                    
                elif choice == '2':
                    print("\nMaking notes...")
                    notes = generate_notes(transcript)
                    print("\n" + "="*40)
                    print("NOTES")
                    print("="*40)
                    print(notes)
                    print("="*40)
                    
                elif choice == '3':
                    print("\nMaking audio summary...")
                    summary_text = generate_summary(transcript)
                    file = text_to_audio(summary_text)
                    if file:
                        print(f"Audio saved: {file}")
                        print("You can listen to it now!")
                    else:
                        print("Couldn't make audio file")
                        
                elif choice == '4':
                    print("\nThanks for using the summarizer!")
                    print("Bye!")
                    break
                    
                else:
                    print("Please pick 1, 2, 3, or 4")
        else:
            print("\nCouldn't get the transcript.")
            print("Maybe the video doesn't have captions or is private.")