"""
YouTube Video Summarizer - Simple Flask API
===========================================

A Flask API that processes YouTube videos.
Made for my programming class project.

What it does:
- Takes a YouTube URL
- Gets the transcript 
- Makes a summary or notes

How to use:
Send POST request to /api/process with:
{
  "url": "https://youtube.com/watch?v=VIDEO_ID",
  "operation": "summary" (or "notes", "transcript")
}

"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import time

# Import my functions
from app import get_video_id, get_transcript, generate_summary, generate_notes

# Setup Flask
app = Flask(__name__)
CORS(app)  # Allow frontend to connect

# Helper functions
def make_success_response(data, message="Success"):
    """Make a simple success response"""
    return {
        "success": True,
        "message": message,
        "data": data
    }

def make_error_response(message, status_code=400):
    """Make a simple error response"""
    return {
        "success": False,
        "error": message
    }, status_code

def check_required_fields(data, required_fields):
    """Check if required fields exist"""
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"Missing: {field}"
    return True, None

# Routes

@app.route('/', methods=['GET'])
def home():
    """Show what this API does"""
    info = {
        "name": "YouTube Video Summarizer",
        "description": "Simple API to summarize YouTube videos",
        "how_to_use": "Send POST to /api/process with url and operation",
        "operations": ["transcript", "summary", "notes"]
    }
    return jsonify(make_success_response(info, "API is working!"))

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check"""
    return jsonify(make_success_response({"status": "healthy"}, "All good!"))

@app.route('/api/process', methods=['POST'])
def process_video():
    """Process YouTube videos - main function"""
    try:
        # Get the data from request
        data = request.get_json()
        
        if not data:
            return make_error_response("No data provided", 400)
        
        # Check if we have url and operation
        is_valid, error_message = check_required_fields(data, ['url', 'operation'])
        if not is_valid:
            return make_error_response(error_message, 400)
        
        url = data['url']
        operation = data['operation'].lower()
        
        # Check if operation is valid
        if operation not in ['transcript', 'summary', 'notes']:
            return make_error_response("Operation must be: transcript, summary, or notes", 400)
        
        # Get video ID from URL
        video_id = get_video_id(url)
        if not video_id:
            return make_error_response("Invalid YouTube URL", 400)
        
        # Get transcript
        transcript = get_transcript(video_id)
        if not transcript:
            return make_error_response("Could not get transcript - video might not have captions", 404)
        
        # Process based on what user wants
        start_time = time.time()
        
        if operation == 'transcript':
            result = {
                "video_id": video_id,
                "transcript": transcript,
                "length": len(transcript),
                "time_taken": round(time.time() - start_time, 2)
            }
            return jsonify(make_success_response(result, "Got transcript!"))
        
        elif operation == 'summary':
            summary = generate_summary(transcript)
            if summary == "Sorry, couldn't make summary":
                return make_error_response("Summary failed", 500)
            
            result = {
                "video_id": video_id,
                "summary": summary,
                "original_length": len(transcript),
                "summary_length": len(summary),
                "time_taken": round(time.time() - start_time, 2)
            }
            return jsonify(make_success_response(result, "Made summary!"))
        
        elif operation == 'notes':
            notes = generate_notes(transcript)
            if notes == "Sorry, couldn't make notes":
                return make_error_response("Notes failed", 500)
            
            result = {
                "video_id": video_id,
                "notes": notes,
                "time_taken": round(time.time() - start_time, 2)
            }
            return jsonify(make_success_response(result, "Made notes!"))
    
    except Exception as e:
        print(f"Error: {e}")
        return make_error_response(f"Something went wrong: {str(e)}", 500)



# Error handlers
@app.errorhandler(404)
def not_found(error):
    return make_error_response("Page not found", 404)

@app.errorhandler(500)
def server_error(error):
    return make_error_response("Server error", 500)

# Run the app
if __name__ == '__main__':
    print("🚀 Starting YouTube Video Summarizer!")
    print("📝 What it does:")
    print("   - GET transcript from YouTube videos")
    print("   - MAKE summaries and notes with AI") 
    print("🌐 API running at: http://localhost:8000")
    print("📖 Test it: Go to http://localhost:8000 in your browser")
    
    app.run(host='0.0.0.0', port=8000, debug=True)