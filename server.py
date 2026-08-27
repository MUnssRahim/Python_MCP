import os
from mcp.server import MCPServer
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build

# Initialize the v2 MCPServer
mcp = MCPServer("YouTube MCP Server")

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

@mcp.tool()
def search_videos(query: str, max_results: int = 5) -> str:
    """Search YouTube for videos matching a query."""
    if not YOUTUBE_API_KEY:
        return "Error: YOUTUBE_API_KEY environment variable is not configured."
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        response = youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            maxResults=max_results
        ).execute()
        
        results = []
        for item in response.get("items", []):
            title = item["snippet"]["title"]
            video_id = item["id"]["videoId"]
            results.append(f"- **{title}**: https://www.youtube.com/watch?v={video_id}")
            
        return "\n".join(results) if results else "No videos found."
    except Exception as e:
        return f"Error executing YouTube search: {str(e)}"

@mcp.tool()
def get_transcript(url: str) -> str:
    """Fetch the transcript of a YouTube video using its URL or video ID."""
    try:
        # Extract video ID from URL or bare ID
        video_id = url.split("v=")[-1].split("&")[0] if "v=" in url else url.split("/")[-1]
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry["text"] for entry in transcript_data])
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    mcp.run(transport="streamable-http", port=port, host="0.0.0.0")
