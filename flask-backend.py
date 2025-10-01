"""
YouTube Transcript Summarizer - Flask API Backend
================================================

A Flask-based REST API backend for processing YouTube videos with AI-powered
summarization, note generation, and audio conversion capabilities. This API provides
JSON responses that can be easily consumed by frontend applications.

Features:
- RESTful API endpoints for video processing
- JSON response format for frontend integration
- Error handling with proper HTTP status codes
- CORS support for cross-origin requests
- Audio file serving capabilities

Endpoints:
- GET /: API information
- GET /health: Service health check
- POST /api/process: Process YouTube videos
- GET /api/audio/<filename>: Download audio files

Dependencies:
- Flask: Web framework for building APIs
- Flask-CORS: Cross-origin request handling
- All dependencies from app.py

Author: [Your Name] & [Friend's Name]
Version: 1.0.0
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import time
from datetime import datetime
from pathlib import Path
import traceback

# Import functions from the main app
from app import get_video_id, get_transcript, generate_summary, generate_notes, text_to_audio

# ================================
# FLASK APP CONFIGURATION
# ================================

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Create directory for audio files
AUDIO_DIR = Path("audio_files")
AUDIO_DIR.mkdir(exist_ok=True)

# ================================
# UTILITY FUNCTIONS
# ================================

# Create standardized JSON success response
def create_success_response(data, message="Success"):
    """Create a standardized success response"""
    return {
        "status": "success",
        "message": message,
        "timestamp": datetime.now().isoformat(),
        "data": data
    }

# Create standardized JSON error response
def create_error_response(error_message, error_code="UNKNOWN_ERROR", status_code=500):
    """Create a standardized error response"""
    return {
        "status": "error",
        "message": error_message,
        "error_code": error_code,
        "timestamp": datetime.now().isoformat()
    }, status_code

# Validate that required fields exist in request data
def validate_request_data(data, required_fields):
    """Validate that required fields are present in request data"""
    missing_fields = [field for field in required_fields if field not in data or not data[field]]
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    return True, None

# ================================
# API ENDPOINTS
# ================================

@app.route('/api/process', methods=['POST'])
def process_video():
    # Process YouTube video for transcript, summary, notes, or audio
    """
    Main endpoint for processing YouTube videos
    
    Expected JSON payload:
    {
        "url": "https://youtube.com/watch?v=VIDEO_ID",
        "operation": "summary|notes|audio|transcript",
        "audio_filename": "optional_custom_name" (only for audio operation)
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return create_error_response("No JSON data provided", "INVALID_REQUEST", 400)
        
        # Validate required fields
        is_valid, error_message = validate_request_data(data, ['url', 'operation'])
        if not is_valid:
            return create_error_response(error_message, "MISSING_FIELDS", 400)
        
        url = data['url']
        operation = data['operation'].lower()
        audio_filename = data.get('audio_filename', None)
        
        # Validate operation type
        valid_operations = ['transcript', 'summary', 'notes', 'audio']
        if operation not in valid_operations:
            return create_error_response(
                f"Invalid operation. Must be one of: {', '.join(valid_operations)}", 
                "INVALID_OPERATION", 
                400
            )
        
        # Extract video ID
        video_id = get_video_id(url)
        if not video_id:
            return create_error_response(
                "Invalid YouTube URL format", 
                "INVALID_URL", 
                400
            )
        
        # Fetch transcript
        transcript = get_transcript(video_id)
        if not transcript:
            return create_error_response(
                "Could not fetch transcript. Video may not have captions or may be restricted", 
                "TRANSCRIPT_UNAVAILABLE", 
                404
            )
        
        # Process based on operation type
        start_time = time.time()
        
        if operation == 'transcript':
            result_data = {
                "video_id": video_id,
                "transcript": transcript,
                "character_count": len(transcript),
                "processing_time": round(time.time() - start_time, 2)
            }
            return jsonify(create_success_response(result_data, "Transcript extracted successfully"))
        
        elif operation == 'summary':
            summary = generate_summary(transcript)
            if summary == "Sorry, couldn't make summary":
                return create_error_response("Summary generation failed", "SUMMARY_GENERATION_FAILED", 500)
            result_data = {
                "video_id": video_id,
                "summary": summary,
                "original_length": len(transcript),
                "summary_length": len(summary),
                "processing_time": round(time.time() - start_time, 2)
            }
            return jsonify(create_success_response(result_data, "Summary generated successfully"))
        
        elif operation == 'notes':
            notes = generate_notes(transcript)
            if notes == "Sorry, couldn't make notes":
                return create_error_response("Notes generation failed", "NOTES_GENERATION_FAILED", 500)
            result_data = {
                "video_id": video_id,
                "notes": notes,
                "original_length": len(transcript),
                "notes_length": len(notes),
                "processing_time": round(time.time() - start_time, 2)
            }
            return jsonify(create_success_response(result_data, "Notes generated successfully"))
        
        elif operation == 'audio':
            summary = generate_summary(transcript)
            if summary == "Sorry, couldn't make summary":
                return create_error_response("Summary generation failed", "SUMMARY_GENERATION_FAILED", 500)
            
            if audio_filename:
                audio_file = f"{audio_filename}.mp3"
            else:
                audio_file = f"summary_{video_id}.mp3"
            
            audio_path = AUDIO_DIR / audio_file
            result_file = text_to_audio(summary, str(audio_path))
            
            if result_file:
                file_size = audio_path.stat().st_size
                result_data = {
                    "video_id": video_id,
                    "audio_filename": audio_file,
                    "file_size_bytes": file_size,
                    "download_url": f"/api/audio/{audio_file}",
                    "summary": summary,
                    "processing_time": round(time.time() - start_time, 2)
                }
                return jsonify(create_success_response(result_data, "Audio summary generated successfully"))
            else:
                return create_error_response("Failed to generate audio file", "AUDIO_GENERATION_FAILED", 500)
    
    except Exception as e:
        print(f"Error processing video: {str(e)}")
        print(traceback.format_exc())
        return create_error_response(
            f"An unexpected error occurred: {str(e)}", 
            "INTERNAL_ERROR", 
            500
        )