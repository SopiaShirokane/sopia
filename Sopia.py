import requests
import os
import json
import ast
import subprocess
from datetime import datetime

def playVideo(url):
    result = subprocess.run(
        ["yt-dlp", "-g", url],
        capture_output=True, text=True, check=True,
    )
    if result.returncode != 0:
        print(result.stderr)
        return
    
    stream_url = result.stdout.strip().splitlines()
    cmd = ["vlc", stream_url[0]]
    if len(stream_url) > 1:
        cmd += ["--input-slave", stream_url[1]]
    subprocess.Popen(cmd)

def file(fileName):
    with open (fileName, "w", encoding="utf-8") as f:
        print(response.json(), file=f)
    with open(fileName, "r", encoding="utf-8") as f:
        fileData = ast.literal_eval(f.read())
    with open(fileName, "w", encoding="utf-8") as f:
        json.dump(fileData, f, ensure_ascii=False,  indent=2)
    with open(fileName, "r", encoding="utf-8") as f:
        fileData = json.load(f)
    return fileData

def time(timestamp):
    formattedTime = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    return formattedTime.strftime("%d/%m/%Y %H:%M")


API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY environment variable is not set. Please set it before running this script by using export API_KEY = 'your API key here'.")   

print("Welcome to SopiaOS! (operating script)")
print("\n")

response = requests.get(
    "https://www.googleapis.com/youtube/v3/channels",
    params={"part": "snippet, statistics, contentDetails", "forHandle": "@SorashinaSopia", "key": API_KEY},
)
channelData = file("channelData.json")

itemsData = channelData["items"][0]
snippetData = itemsData["snippet"]

print(f'Name: {snippetData["title"]}')
print(f'Handle: {snippetData["customUrl"]}')
print(f'Day created: {time(snippetData["publishedAt"])}')
print(f'Country: {snippetData["country"]}')
print("\n")

statistics = itemsData["statistics"]
print(f'Views: {statistics["viewCount"]}')
print(f'Subscribers: {statistics["subscriberCount"]}')
print(f'Videos: {statistics["videoCount"]}')
print("\n")

contentDetails = itemsData["contentDetails"]
relatedPlaylists = contentDetails["relatedPlaylists"]

response = requests.get(
    "https://www.googleapis.com/youtube/v3/playlistItems",
    params={"part": "snippet", "playlistId": relatedPlaylists["uploads"], "key": API_KEY},
)
uploads = file("uploads.json")

counter = 0
print("Newest videos:")
while counter <= 4:
    uploadItems = uploads["items"][counter]
    uploadSnippet = uploadItems["snippet"]
    resourceId = uploadSnippet["resourceId"]
    s = uploadSnippet["title"]
    title = s.removeprefix("{'").removesuffix("'}")
    response = requests.get(
        "https://www.googleapis.com/youtube/v3/videos",
        params={"part": "snippet, statistics, contentDetails, liveStreamingDetails", "id": resourceId["videoId"], "key": API_KEY},
    )
    video = file("video.json")
    videoData = video["items"][0]
    videoSnippet = videoData["snippet"]
    videoStats = videoData["statistics"]
    print(f'{title}     Views: {videoStats["viewCount"]}     Likes: {videoStats["likeCount"]}     Comments {videoStats["commentCount"]}')
    if videoSnippet["liveBroadcastContent"] == "upcoming":
        liveStreamingDetails = videoData["liveStreamingDetails"]
        print(f'This is an upcoming live or premier video, please come back later at {time(liveStreamingDetails["scheduledStartTime"])}')
    print("\n")
    counter += 1

videoPlayback = input("Would you like to play one of the videos on vlc? Requires yt-dlp, deno and vlc (obviously) to be installed (y/n) ")
if videoPlayback == "y":
    choice = int(input("Pick one video from 0-4: "))
    uploadItems = uploads["items"][choice]
    uploadSnippet = uploadItems["snippet"]
    resourceId = uploadSnippet["resourceId"]
    response = requests.get(
        "https://www.googleapis.com/youtube/v3/videos",
        params={"part": "snippet, statistics, contentDetails, liveStreamingDetails", "id": resourceId["videoId"], "key": API_KEY},
    )
    video = file("video.json")
    playVideo(f"https://www.youtube.com/watch?v={resourceId["videoId"]}")
