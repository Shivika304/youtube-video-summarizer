import { useState } from "react";
import { FileText, Sparkles, BookOpen, Loader2, ExternalLink, Copy, Download, Check } from "lucide-react";
import "./App.css";

interface VideoInfo {
  title: string;
  thumbnail: string;
  videoId: string;
}

interface ProcessResponse {
  transcript?: string;
  length?: number;
  summary?: string;
  original_length?: number;
  summary_length?: number;
  notes?: string;
}

const App = () => {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [videoInfo, setVideoInfo] = useState<VideoInfo | null>(null);
  const [result, setResult] = useState<{
    type: string;
    data: ProcessResponse;
  } | null>(null);
  const [copied, setCopied] = useState(false);
  const [message, setMessage] = useState("");

  // Extract video ID from YouTube URL
  const extractVideoId = (url: string): string | null => {
    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/,
      /^([a-zA-Z0-9_-]{11})$/,
    ];

    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match) {
        return match[1];
      }
    }
    return null;
  };

  // Get video info
  const getVideoInfo = async (videoUrl: string): Promise<VideoInfo> => {
    const videoId = extractVideoId(videoUrl);
    if (!videoId) {
      throw new Error('Invalid YouTube URL');
    }

    try {
      const response = await fetch(
        `https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=${videoId}&format=json`
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch video info');
      }

      const data = await response.json();
      
      return {
        title: data.title,
        thumbnail: `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`,
        videoId,
      };
    } catch (error) {
      throw new Error('Could not fetch video information');
    }
  };

  // Process video
  const processVideo = async (operation: 'transcript' | 'summary' | 'notes'): Promise<ProcessResponse> => {
    const response = await fetch('http://localhost:8000/api/process', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url, operation }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ error: 'Failed to process video' }));
      throw new Error(error.error || 'Failed to process video');
    }

    const result = await response.json();
    if (result.success) {
      return result.data;  // Extract data from Flask response
    } else {
        throw new Error(result.error || 'Processing failed');
      }
  };

  // Handle URL change
  const handleUrlChange = async (value: string) => {
    setUrl(value);
    setResult(null);

    if (value.includes('youtube.com') || value.includes('youtu.be')) {
      try {
        const info = await getVideoInfo(value);
        setVideoInfo(info);
      } catch (error) {
        setVideoInfo(null);
      }
    } else {
      setVideoInfo(null);
    }
  };

  // Handle process
  const handleProcess = async (operation: 'transcript' | 'summary' | 'notes') => {
    if (!url.trim()) {
      setMessage("Please enter a YouTube URL");
      setTimeout(() => setMessage(""), 3000);
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const data = await processVideo(operation);
      setResult({ type: operation, data });
      setMessage(`${operation.charAt(0).toUpperCase() + operation.slice(1)} generated successfully!`);
      setTimeout(() => setMessage(""), 3000);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Failed to process video");
      setTimeout(() => setMessage(""), 3000);
    } finally {
      setLoading(false);
    }
  };

  // Copy to clipboard
  const handleCopy = async (content: string) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setMessage("Copied to clipboard!");
      setTimeout(() => {
        setCopied(false);
        setMessage("");
      }, 2000);
    } catch (error) {
      setMessage("Failed to copy");
      setTimeout(() => setMessage(""), 3000);
    }
  };

  // Download file
  const handleDownload = (content: string, title: string) => {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${title.toLowerCase().replace(/\s+/g, '-')}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    setMessage("Downloaded successfully!");
    setTimeout(() => setMessage(""), 3000);
  };

  // Get result content
  const getResultContent = () => {
    if (!result) return null;

    const { type, data } = result;

    if (type === 'transcript' && data.transcript) {
      return {
        title: 'Transcript',
        content: data.transcript,
        metadata: { length: data.length },
      };
    }

    if (type === 'summary' && data.summary) {
      return {
        title: 'Summary',
        content: data.summary,
        metadata: {
          original_length: data.original_length,
          summary_length: data.summary_length,
        },
      };
    }

    if (type === 'notes' && data.notes) {
      return {
        title: 'Notes',
        content: data.notes,
        metadata: undefined,
      };
    }

    return null;
  };

  const resultContent = getResultContent();

  return (
    <div className="app">
      <div className="container">
        {/* Header */}
        <div className="header">
          <h1 className="title">YouTube Video Summarizer</h1>
          <p className="subtitle">
            Transform any YouTube video into transcripts, summaries, or study notes instantly
          </p>
        </div>

        {/* Message */}
        {message && (
          <div className={`message ${message.includes('Failed') || message.includes('error') ? 'error' : 'success'}`}>
            {message}
          </div>
        )}

        {/* Video Preview */}
        {videoInfo && !loading && !result && (
          <div className="video-preview">
            <div 
              onClick={() => window.open(`https://www.youtube.com/watch?v=${videoInfo.videoId}`, '_blank')}
              className="video-card"
            >
              <div className="video-thumbnail">
                <img src={videoInfo.thumbnail} alt={videoInfo.title} />
                <div className="external-link">
                  <ExternalLink size={24} />
                </div>
              </div>
              <div className="video-title">
                <h3>{videoInfo.title}</h3>
              </div>
            </div>
          </div>
        )}

        {/* Input Section */}
        <div className="input-section">
          <div className="input-card">
            <label htmlFor="youtube-url">YouTube URL</label>
            <input
              id="youtube-url"
              type="text"
              placeholder="https://www.youtube.com/watch?v=..."
              value={url}
              onChange={(e) => handleUrlChange(e.target.value)}
              className="url-input"
            />

            {/* Action Buttons */}
            <div className="button-grid">
              <button
                onClick={() => handleProcess('transcript')}
                disabled={loading || !url}
                className="btn btn-purple"
              >
                <FileText size={20} />
                Get Transcript
              </button>
              <button
                onClick={() => handleProcess('summary')}
                disabled={loading || !url}
                className="btn btn-pink"
              >
                <Sparkles size={20} />
                Get Summary
              </button>
              <button
                onClick={() => handleProcess('notes')}
                disabled={loading || !url}
                className="btn btn-green"
              >
                <BookOpen size={20} />
                Get Notes
              </button>
            </div>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="loading">
            <Loader2 className="spinner" size={64} />
            <p>Processing your video...</p>
          </div>
        )}

        {/* Results */}
        {resultContent && !loading && (
          <div className="result-card">
            <div className="result-header">
              <h2>{resultContent.title}</h2>
              <div className="result-actions">
                <button
                  onClick={() => handleCopy(resultContent.content)}
                  className="action-btn"
                  title="Copy to clipboard"
                >
                  {copied ? <Check size={20} /> : <Copy size={20} />}
                </button>
                <button
                  onClick={() => handleDownload(resultContent.content, resultContent.title)}
                  className="action-btn"
                  title="Download as text file"
                >
                  <Download size={20} />
                </button>
              </div>
            </div>
            
            {resultContent.metadata && (
              <div className="metadata">
                {resultContent.metadata.length && (
                  <span>Length: {resultContent.metadata.length.toLocaleString()} characters</span>
                )}
                {resultContent.metadata.original_length && (
                  <>
                    <span>Original: {resultContent.metadata.original_length.toLocaleString()} chars</span>
                    <span>Summary: {resultContent.metadata.summary_length?.toLocaleString()} chars</span>
                  </>
                )}
              </div>
            )}
            
            <div className="content">
              {resultContent.content}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default App;
