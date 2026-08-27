import os
from mcp.server import MCPServer
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build

mcp = MCPServer("YouTube MCP Server")

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")

@mcp.tool()
def search_videos(query: str, max_results: int = 5) -> str:
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
            videoId = item["id"]["videoId"]
            results.append(f"- **{title}**: https://www.youtube.com/watch?v={videoId}")
        return "\n".join(results) if results else "No videos found."
    except Exception as e:
        return f"Error executing YouTube search: {str(e)}"

@mcp.tool()
def get_transcript(url: str) -> str:
    try:
        videoId = url.split("v=")[-1].split("&")[0] if "v=" in url else url.split("/")[-1]
        apiInstance = YouTubeTranscriptApi()
        fetchedTranscript = apiInstance.fetch(videoId)
        transcriptData = fetchedTranscript.to_raw_data()
        return " ".join([entry["text"] for entry in transcriptData])
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"

@mcp.tool()
def get_video_details(url: str) -> str:
    if not YOUTUBE_API_KEY:
        return "Error: YOUTUBE_API_KEY environment variable is not configured."
    try:
        videoId = url.split("v=")[-1].split("&")[0] if "v=" in url else url.split("/")[-1]
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        response = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=videoId
        ).execute()
        items = response.get("items", [])
        if not items:
            return "Video not found."
        item = items[0]
        snippet = item.get("snippet", {})
        statistics = item.get("statistics", {})
        contentDetails = item.get("contentDetails", {})
        title = snippet.get("title", "")
        channelTitle = snippet.get("channelTitle", "")
        publishedAt = snippet.get("publishedAt", "")
        views = statistics.get("viewCount", "N/A")
        likes = statistics.get("likeCount", "N/A")
        duration = contentDetails.get("duration", "N/A")
        return f"Title: {title}\nChannel: {channelTitle}\nPublished: {publishedAt}\nViews: {views}\nLikes: {likes}\nDuration: {duration}"
    except Exception as e:
        return f"Error fetching video details: {str(e)}"

@mcp.tool()
def get_channel_info(channel_id: str) -> str:
    if not YOUTUBE_API_KEY:
        return "Error: YOUTUBE_API_KEY environment variable is not configured."
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        response = youtube.channels().list(
            part="snippet,statistics",
            id=channel_id
        ).execute()
        items = response.get("items", [])
        if not items:
            return "Channel not found."
        item = items[0]
        snippet = item.get("snippet", {})
        statistics = item.get("statistics", {})
        title = snippet.get("title", "")
        description = snippet.get("description", "")
        subscribers = statistics.get("subscriberCount", "N/A")
        totalVideos = statistics.get("videoCount", "N/A")
        totalViews = statistics.get("viewCount", "N/A")
        return f"Channel: {title}\nSubscribers: {subscribers}\nTotal Videos: {totalVideos}\nTotal Views: {totalViews}\nDescription: {description[:300]}..."
    except Exception as e:
        return f"Error fetching channel info: {str(e)}"

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    mcp.run(transport="streamable-http", port=port, host="0.0.0.0")
