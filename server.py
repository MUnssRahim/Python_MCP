import os
from mcp.server import MCPServer
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp

mcp = MCPServer("YouTube MCP Server")

@mcp.tool()
def search_videos(query: str, max_results: int = 5) -> str:
    """Search YouTube for videos matching a query."""
    try:
        ydl_opts = {
            'extract_flat': True,
            'max_downloads': max_results,
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
            entries = info.get('entries', [])
            results = []
            for entry in entries:
                title = entry.get('title')
                video_id = entry.get('id')
                if title and video_id:
                    results.append(f"- **{title}**: https://www.youtube.com/watch?v={video_id}")
            return "\n".join(results) if results else "No videos found."
    except Exception as e:
        return f"Error executing YouTube search: {str(e)}"

@mcp.tool()
def get_transcript(url: str) -> str:
    """Fetch the transcript of a YouTube video using its URL or video ID."""
    try:
        video_id = url.split("v=")[-1].split("&")[0] if "v=" in url else url.split("/")[-1]
        api_instance = YouTubeTranscriptApi()
        fetched_transcript = api_instance.fetch(video_id)
        transcript_data = fetched_transcript.to_raw_data()
        return " ".join([entry["text"] for entry in transcript_data])
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"

@mcp.tool()
def get_video_details(url: str) -> str:
    """Fetch metadata and statistics for a YouTube video."""
    try:
        ydl_opts = {'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'N/A')
            channel = info.get('uploader', 'N/A')
            views = info.get('view_count', 'N/A')
            likes = info.get('like_count', 'N/A')
            duration = info.get('duration_string', 'N/A')
            upload_date = info.get('upload_date', 'N/A')
            return f"Title: {title}\nChannel: {channel}\nPublished: {upload_date}\nViews: {views}\nLikes: {likes}\nDuration: {duration}"
    except Exception as e:
        return f"Error fetching video details: {str(e)}"

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    mcp.run(transport="streamable-http", port=port, host="0.0.0.0")
