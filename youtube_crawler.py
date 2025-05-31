import os
import requests
from dotenv import load_dotenv
import csv
from datetime import datetime

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

def get_channel_details(channel_id):
    url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        "part": "statistics,snippet",
        "id": channel_id,
        "key": YOUTUBE_API_KEY
    }
    response = requests.get(url, params=params).json()
    items = response.get("items", [])
    if items:
        data = items[0]
        stats = data["statistics"]
        snippet = data["snippet"]
        return {
            "channel_title": snippet["title"],
            "channel_id": channel_id,
            "description": snippet.get("description", ""),
            "subscriber_count": int(stats.get("subscriberCount", 0)),
            "video_count": int(stats.get("videoCount", 0)),
            "view_count": int(stats.get("viewCount", 0)),
        }
    return None

def search_creators(query, max_results = 10):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "type": "channel",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY
    }
    response = requests.get(url, params=params).json()
    print("API response:", response)
    return response["items"]

# Compute credibility score based on channel statistics
def compute_credibility_score(stats, keywords):
    score = 0
    if stats["subscriber_count"] > 10000:
        score += 1
    if stats["view_count"] / max(stats["video_count"], 1) > 1000:
        score += 1
    if any(word in stats["description"].lower() for word in keywords):
        score += 1
    return score


## Save results to CSV
def save_to_csv(data, filename="youtube_creators.csv"):
    fieldnames = ["channel_title", "channel_id", "description",
                   "subscriber_count", "video_count", "view_count", 
                   "avg_views_last_5", "upload_per_week", "avg_like_view_ratio", "credibility_score"]
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

## Fetch recent videos from a channel
def get_recent_videos(channel_id, max_results = 5):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "channelId": channel_id,
        "order": "data",
        "maxResults": max_results,
        "type": "video",
        "key": YOUTUBE_API_KEY
    }
    response = requests.get(url, params=params).json()
    videos = response.get("items", [])
    return [video["id"]["videoId"] for video in videos]

## Fetch video statistics
def get_video_statistics(video_id):
    stats = []
    if not video_id:
        return stats
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "statistics,snippet",
        "id": ",".join(video_id),
        "key": YOUTUBE_API_KEY
    }
    response = requests.get(url, params=params).json()
    items = response.get("items", [])

    for item in items:
        stats.append({
            "title": item["snippet"]["title"],
            "views": int(item["statistics"].get("viewCount", 0)),
            "likes": int(item["statistics"].get("likeCount", 0)) if "likeCount" in item["statistics"] else 0,
            "published": item["snippet"]["publishedAt"],
        })
    return stats

## Main function
if __name__ == "__main__":
    print("Searching for personal finance YouTube creators...")
    query = input("Enter topic to search for creators (e.g. finance, AI, health): ").strip()
    keyword_input = input("Enter credibility keywords (comma-separated): ").strip()
    keywords = [k.strip().lower() for k in keyword_input.split(",") if k.strip()]

    creators = search_creators(query, max_results = 5)
    all_creator_data = []

    if not creators:
        print("No creators found.")

    # Loop through each creator and fetch details
    for c in creators:
        channel_id = c["snippet"]["channelId"]
        details = get_channel_details(channel_id)
        if details:
            # Get recent videos
            video_ids = get_recent_videos(channel_id, max_results=5)
            video_stats = get_video_statistics(video_ids)

            # Compute average views
            if video_stats:
                avg_views = sum(v["views"] for v in video_stats) / len(video_stats)
            else:
                avg_views = 0
            details["avg_views_last_5"] = round(avg_views)

            # Compute upload frequency
            if len(video_stats) >= 2:
                dates = [datetime.fromisoformat(v["published"].replace("2", "+00:00")) for v in video_stats]
                dates.sort(reverse = True)
                days_elapsed = (dates[0] - dates[-1]).days or 1
                upload_per_week = (len(dates) - 1) / days_elapsed * 7
            else:
                upload_per_week = 0
            details["upload_per_week"] = round(upload_per_week, 2)

            # Calculation of likes to views ratio
            if video_stats:
                ratios = [
                    (v["likes"] / v["views"]) * 100
                    for v in video_stats
                    if v["views"] > 0
                ]
                avg_like_view_ratio = sum(ratios) / len(ratios) if ratios else 0
            else:
                avg_like_view_ratio = 0
            details["avg_like_view_ratio"] = round(avg_like_view_ratio, 2)

            # Compute credibility score
            score = compute_credibility_score(details, keywords)
            details["credibility_score"] = score
            all_creator_data.append(details)

            # Print creator details
            print(details)
            print(f"Credibility Score: {score}/3")
            print(f"Uploads per week: {upload_per_week:.2f}")
            print(f"Average Like/View Ratio: {avg_like_view_ratio}%")
            print("-" * 40)

    save_to_csv(all_creator_data)
    print("Data saved to youtube_creators.csv")


