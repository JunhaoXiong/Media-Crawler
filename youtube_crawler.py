import os
import requests
from dotenv import load_dotenv
import csv

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

def compute_credibility_score(stats):
    keywords = ["finance", "investing", "wealth", "money", "stock"]
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
                   "subscriber_count", "video_count", "view_count", "credibility_score"]
    
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

## Main function
if __name__ == "__main__":
    print("Searching for personal finance YouTube creators...")
    creators = search_creators("personal finance", max_results = 5)
    all_creator_data = []

    if not creators:
        print("No creators found.")
    for c in creators:
        channel_id = c["snippet"]["channelId"]
        details = get_channel_details(channel_id)
        if details:
            score = compute_credibility_score(details)
            details["credibility_score"] = score
            all_creator_data.append(details)
            print(details)
            print(f"Credibility Score: {score}/3")
            print("-" * 40)

    save_to_csv(all_creator_data)
    print("Data saved to youtube_creators.csv")
