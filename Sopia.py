import requests
import os
import json
import ast
import subprocess

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

API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY environment variable is not set. Please set it before running this script by using export API_KEY = 'your API key here'.")   

print("Welcome to SopiaOS! (operating script)")
print("\n")

response = requests.get(
    "https://www.googleapis.com/youtube/v3/channels",
    params={"part": "snippet, statistics, contentDetails", "forHandle": "@SorashinaSopia", "key": API_KEY},
)
with open ("channelData.json", "w", encoding="utf-8") as f:
    print(response.json(), file=f)
with open("channelData.json", "r", encoding="utf-8") as f:
    channelData = ast.literal_eval(f.read())
with open("channelData.json", "w", encoding="utf-8") as f:
    json.dump(channelData, f, ensure_ascii=False,  indent=2)
with open("channelData.json", "r", encoding="utf-8") as f:
    channelData = json.load(f)

itemsData = channelData["items"][0]
snippetData = itemsData["snippet"]

print(f'Name: {snippetData["title"]}')
print(f'Handle: {snippetData["customUrl"]}')
print(f'Day created: {snippetData["publishedAt"]}')
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
with open ("uploads.json", "w", encoding="utf-8") as f:
    print(response.json(), file=f)
with open("uploads.json", "r", encoding="utf-8") as f:
    uploads = ast.literal_eval(f.read())
with open("uploads.json", "w", encoding="utf-8") as f:
    json.dump(uploads, f, ensure_ascii=False,  indent=2)
with open("uploads.json", "r", encoding="utf-8") as f:
    uploads = json.load(f)

counter = 0
print("Newest videos:")
while counter <= 4:
    uploadItems = uploads["items"][counter]
    uploadSnippet = uploadItems["snippet"]
    resourceId = uploadSnippet["resourceId"]
    s = uploadSnippet["title"]
    title = s.removeprefix("{'").removesuffix("'}")
    print(title)
    counter += 1

videoPlayback = input("Would you like to play one of the videos on vlc? Requires yt-dlp, deno and vlc (obviously) to be installed (y/n) ")
if videoPlayback == "y":
    choice = int(input("Pick one video from 0-4: "))
    uploadItems = uploads["items"][choice]
    uploadSnippet = uploadItems["snippet"]
    resourceId = uploadSnippet["resourceId"]
    playVideo(f"https://www.youtube.com/watch?v={resourceId["videoId"]}")

response = requests.get(
    "https://www.googleapis.com/youtube/v3/videos",
    params={"part": "snippet, statistics, contentDetails", "id": resourceId["videoId"], "key": API_KEY},
)
with open ("video.json", "w", encoding="utf-8") as f:
    print(response.json(), file=f)
with open("video.json", "r", encoding="utf-8") as f:
    video = ast.literal_eval(f.read())
with open("video.json", "w", encoding="utf-8") as f:
    json.dump(video, f, ensure_ascii=False,  indent=2)
with open("video.json", "r", encoding="utf-8") as f:
    video = json.load(f)
videoData = video["items"][0]

videoSnippet = videoData["snippet"]
print("Video tags:")
for tags in videoSnippet["tags"]:
    print(f'#{tags}')
print("\n")

videoStats = videoData["statistics"]
print(f'Views: {videoStats["viewCount"]}')
print(f'Likes: {videoStats["likeCount"]}')
print(f'Comments {videoStats["commentCount"]}')