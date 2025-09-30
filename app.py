"""
YouTube Transcript Summarizer - Interactive CLI Application
==========================================================

This application extracts transcripts from YouTube videos and uses Google's Gemini AI
to generate summaries, detailed notes, and audio versions. It provides an interactive
command-line interface for users to process videos step by step.

Features:
- Extract transcripts from YouTube videos
- Generate AI-powered summaries using Google Gemini
- Create structured notes from video content  
- Convert summaries to MP3 audio files
- Interactive menu-driven interface

Dependencies:
- youtube-transcript-api: Extract transcripts from YouTube
- gtts: Google Text-to-Speech for audio generation
- google-generativeai: Google Gemini AI for text processing
- python-dotenv: Environment variable management
- urllib.parse: URL parsing utilities

Author: [Your Name]
Version: 1.0.0
"""

from youtube_transcript_api import YouTubeTranscriptApi  # YouTube transcript extraction
from gtts import gTTS                                    # Google Text-to-Speech
import google.generativeai as genai                      # Google Gemini AI
from dotenv import load_dotenv                           # Environment variables
import os                                                # Operating system interface
from urllib.parse import urlparse, parse_qs             # URL parsing utilities

# ================================
# CONFIGURATION & SETUP
# ================================

# --- Step 1: Load API key from environment ---
load_dotenv()  # Load environment variables from .env file
api_key = os.getenv("GEMINI_API_KEY")  # Get Gemini API key

# Validate API key and configure Gemini client
if api_key:
    genai.configure(api_key=api_key)  # Configure Gemini with API key
    print("Gemini AI configured successfully")
else:
    print("Error: GEMINI_API_KEY not found. Please check your .env file.")
    print("Create a .env file with: GEMINI_API_KEY=\"your_api_key_here\"")
    exit()

# ================================
# CORE UTILITY FUNCTIONS
# ================================

# --- Step 2: Extract YouTube Video ID from URL ---
def get_video_id(url):
    """
    Extract video ID from various YouTube URL formats.
    
    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtube.com/watch?v=VIDEO_ID  
    - https://youtu.be/VIDEO_ID
    
    Args:
        url (str): YouTube URL to parse
        
    Returns:
        str or None: Video ID if valid URL, None otherwise
        
    Example:
        >>> get_video_id("https://youtube.com/watch?v=dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
    """
    parsed_url = urlparse(url)
    
    # Handle youtube.com URLs (with query parameters)
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        video_id = parse_qs(parsed_url.query).get('v', [None])[0]
    # Handle youtu.be URLs (video ID in path)
    elif parsed_url.hostname == 'youtu.be':
        video_id = parsed_url.path[1:]  # Remove leading slash
    else:
        video_id = None  # Unsupported URL format
        
    return video_id

# ================================
# TRANSCRIPT PROCESSING
# ================================

# --- Step 3: Get transcript from YouTube video ---
def get_transcript(video_id):
    """
    Fetch English transcript from YouTube video using video ID.
    
    Uses the YouTube Transcript API to retrieve available English captions.
    Handles both auto-generated and manual captions.
    
    Args:
        video_id (str): YouTube video ID (11 characters)
        
    Returns:
        str or None: Complete transcript text, or None if unavailable
        
    Note:
        - Requires video to have English captions available
        - Auto-generated captions may have some inaccuracies
        - Private/restricted videos will return None
    """
    try:
        # Create YouTube Transcript API instance
        api = YouTubeTranscriptApi()
        
        # Fetch transcript data with English language preference
        transcript_data = api.fetch(video_id, languages=['en'])
        
        # Extract text from transcript segments and join into single string
        # Each segment has: {text: "...", start: float, duration: float}
        text = " ".join([segment.text for segment in transcript_data])
        print(text)
        
        print(f"Transcript fetched: {len(text)} characters")
        return text
        
    except Exception as e:
        print(f"Transcript not available or could not be fetched: {e}")
        print("Video may not have English captions or may be restricted")
        return None

# ================================
# AI CONTENT GENERATION
# ================================

# --- Step 4: AI-powered content generation functions ---
def generate_summary(text):
    """
    Generate a comprehensive summary from video transcript using Gemini AI.
    
    Creates a detailed, point-by-point summary that captures the main topics,
    arguments, and key events from the video content. Designed to provide
    a complete overview without needing to watch the original video.
    
    Args:
        text (str): Complete transcript text from YouTube video
        
    Returns:
        str: AI-generated summary in bullet-point format
        
    AI Model: gemini-2.5-flash (Google's latest fast model)
    """
    # Construct detailed prompt for comprehensive summarization
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
    
    try:
        # Initialize Gemini model (fast variant for quick responses)
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        # Generate summary using AI
        print("Generating AI summary...")
        response = model.generate_content(prompt)
        
        return response.text.strip()
        
    except Exception as e:
        print(f"Error generating summary: {e}")
        return "Summary generation failed. Please try again."

def generate_notes(text):
    """
    Generate structured, hierarchical notes from video transcript using Gemini AI.
    
    Creates organized study notes with main sections, bullet points, and sub-points.
    Perfect for academic content, tutorials, or any educational videos where
    detailed note-taking is valuable.
    
    Args:
        text (str): Complete transcript text from YouTube video
        
    Returns:
        str: AI-generated structured notes with headings and bullet points
        
    Format: Hierarchical structure with headings, bullets, and sub-bullets
    """
    # Construct prompt for structured note generation
    prompt = f"""
    You are a meticulous note-taker. Your task is to convert the following video transcript into a structured, hierarchical set of notes.

    Please follow these instructions:
    1.  Identify the main sections or topics of the video. Use these as top-level headings.
    2.  Under each heading, use bullet points or numbered lists to capture key details, facts, examples, and arguments.
    3.  Use sub-bullets for finer details where necessary to create a clear structure.
    4.  Focus on capturing information accurately and concisely. The goal is to create a comprehensive study guide from the video.

    Here is the transcript:
    ---
    {text}
    ---
    """
    
    try:
        # Initialize Gemini model for note generation
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Generate structured notes using AI
        print("Generating structured notes...")
        response = model.generate_content(prompt)
        
        return response.text.strip()
        
    except Exception as e:
        print(f"Error generating notes: {e}")
        return "Notes generation failed. Please try again."

# ================================
# AUDIO GENERATION
# ================================

# --- Step 5: Convert text to audio ---
def text_to_audio(summary, filename="summary.mp3"):
    """
    Convert text to MP3 audio file using Google Text-to-Speech.
    
    Creates an audio version of the text content, useful for listening
    to summaries while commuting, exercising, or multitasking.
    
    Args:
        summary (str): Text content to convert to speech
        filename (str): Output filename for the MP3 file
        
    Returns:
        str or None: Filename if successful, None if failed
        
    Audio Settings:
        - Language: English (default)
        - Format: MP3
        - Quality: Standard Google TTS quality
    """
    try:
        print(f"Converting text to speech...")
        
        # Initialize Google Text-to-Speech with default English language
        tts = gTTS(text=summary, lang='en', slow=False)
        
        # Save audio to specified filename
        tts.save(filename)
        
        print(f"Audio saved as: {filename}")
        return filename
        
    except Exception as e:
        print(f"Could not save audio file: {e}")
        print("Check internet connection and try again")
        return None

# ================================
# INTERACTIVE USER INTERFACE
# ================================

# --- Step 6: Main execution block with interactive menu ---
if __name__ == "__main__":
    """
    Main interactive application flow.
    
    Process:
    1. Get YouTube URL from user
    2. Extract video ID and fetch transcript  
    3. Present menu of processing options
    4. Generate requested content using AI
    5. Display results or save audio files
    """
    
    print("YouTube Transcript Summarizer")
    print("=" * 40)
    
    # Step 1: Get YouTube URL from user
    yt_url = input("Enter YouTube URL: ").strip()
    
    # Step 2: Extract video ID and validate URL
    video_id = get_video_id(yt_url)
    
    if not video_id:
        print("Invalid or unsupported YouTube URL.")
        print("Supported formats:")
        print("   - https://youtube.com/watch?v=VIDEO_ID")
        print("   - https://youtu.be/VIDEO_ID")
    else:
        print(f"Valid video ID: {video_id}")
        print("\nFetching transcript...")
        
        # Step 3: Fetch transcript from YouTube
        transcript = get_transcript(video_id)
        
        if transcript:
            print("Transcript fetched successfully.")
            print(f"Transcript length: {len(transcript)} characters")
            
            # Step 4: Interactive menu loop
            while True:
                print("\n" + "="*40)
                print("What would you like to do?")
                print("  1. Create a written summary")
                print("  2. Create detailed notes") 
                print("  3. Create an audio summary")
                print("  4. Exit")
                print("="*40)
                
                choice = input("Enter your choice (1-4): ").strip()

                if choice == '1':
                    print("\nGenerating summary...")
                    summary = generate_summary(transcript)
                    print("\n" + "="*50)
                    print("VIDEO SUMMARY")
                    print("="*50)
                    print(summary)
                    print("="*50)
                    
                elif choice == '2':
                    print("\nGenerating notes...")
                    notes = generate_notes(transcript)
                    print("\n" + "="*50)
                    print("DETAILED NOTES")
                    print("="*50)
                    print(notes)
                    print("="*50)
                    
                elif choice == '3':
                    print("\nGenerating audio summary...")
                    summary_text = generate_summary(transcript)
                    file = text_to_audio(summary_text)
                    if file:
                        print(f"Audio summary saved as: {file}")
                        print("You can now listen to your summary!")
                    else:
                        print("Failed to create audio file")
                        
                elif choice == '4':
                    print("\nThank you for using YouTube Transcript Summarizer!")
                    print("Exiting application...")
                    break
                    
                else:
                    print("Invalid choice. Please enter a number between 1 and 4.")
        else:
            print("\nCould not process the video because the transcript is unavailable.")
            print("Possible reasons:")
            print("   - Video doesn't have English captions")
            print("   - Video is private or restricted")
            print("   - Video is age-restricted")
            print("   - Network connectivity issues")

