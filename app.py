from youtube_transcript_api import YouTubeTranscriptApi
from gtts import gTTS
import google.generativeai as genai
from dotenv import load_dotenv
import os
from urllib.parse import urlparse, parse_qs

# --- Step 1: Load API key ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# --- Step 2: Extract YouTube Video ID from URL ---
def get_video_id(url):
    """Parses a YouTube URL to extract the video ID."""
    parsed_url = urlparse(url)
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        return parse_qs(parsed_url.query).get('v', [None])[0]
    elif parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    else:
        return None

# --- Step 3: Get transcript (Corrected and more robust method) ---
def get_transcript(video_id):
    """Fetches the transcript for a given video ID."""
    try:
        # Create API instance and fetch transcript directly
        api = YouTubeTranscriptApi()
        transcript_data = api.fetch(video_id, languages=['en'])
        
        # Join the text segments from FetchedTranscriptSnippet objects
        text = " ".join([segment.text for segment in transcript_data])
        return text
    except Exception as e:
        print(f"Transcript not available or could not be fetched: {e}")
        return None

# --- Step 4: Summarize text with Gemini ---
def summarize_text(text):
    """Summarizes the given text using the Gemini API."""
    prompt = f"""
    You are an expert at creating detailed, easy-to-read summaries from video transcripts.
    Your task is to analyze the following transcript and create a comprehensive summary in a point-by-point format.

    Please follow these instructions:
    1.  Identify all the main topics, arguments, and key events discussed in the video.
    2.  For each topic or event, create a clear and descriptive bullet point.
    3.  Explain each point in detail, ensuring that the summary captures the full context and all significant information.
    4.  The goal is to provide a complete overview that allows someone to understand the video's content without having to watch it.

    Here is the transcript:
    ---
    {text}
    ---
    """
    model = genai.GenerativeModel('gemini-2.5-flash') # Using the latest available model
    response = model.generate_content(prompt)
    return response.text.strip()

# --- Step 5: Convert summary to audio ---
def text_to_audio(summary, filename="summary.mp3"):
    """Converts the summary text to an MP3 audio file."""
    try:
        tts = gTTS(summary)
        tts.save(filename)
        return filename
    except Exception as e:
        print(f"Could not save audio file: {e}")
        return None

# --- Step 6: Main execution block ---
if __name__ == "__main__":
    yt_url = input("Enter YouTube URL: ").strip()
    video_id = get_video_id(yt_url)

    if not video_id:
        print("Invalid or unsupported YouTube URL.")
    else:
        transcript = get_transcript(video_id)
        
        if transcript:
            print("\nTranscript fetched successfully. Now summarizing...")
            summary = summarize_text(transcript)
            print("\n--- Video Summary ---\n")
            print(summary)

            # Optional: Save audio
            choice = input("\nDo you want an audio summary? (y/n): ").strip().lower()
            if choice == 'y':
                file = text_to_audio(summary)
                if file:
                    print(f"Audio summary saved as {file}")
        else:
            print("\nCould not generate a summary because the transcript is unavailable.")