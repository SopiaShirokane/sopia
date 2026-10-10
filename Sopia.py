import requests
import os
import json
import ast
import subprocess
from datetime import datetime
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import yt_dlp
from io import BytesIO
from PIL import Image, ImageTk


API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY environment variable is not set. Please set it before running this script by using export API_KEY = 'your API key here'.")   

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

def file(fileName, apiResponse):
    with open (fileName, "w", encoding="utf-8") as f:
        print(apiResponse.json(), file=f)
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

def starting_script():
    response = requests.get(
        "https://www.googleapis.com/youtube/v3/channels",
        params={"part": "snippet, statistics, contentDetails", "forHandle": "@SorashinaSopia", "key": API_KEY},
    )
    channelData = file("channelData.json", response)
    itemsData = channelData["items"][0]
    snippetData = itemsData["snippet"]
    statistics = itemsData["statistics"]
    thumbnailUrl = snippetData["thumbnails"]["high"]["url"]
    imageData = requests.get(thumbnailUrl).content
    img = Image.open(BytesIO(imageData)).resize((175, 175))
    photo = ImageTk.PhotoImage(img)

    spaceTopLabel.config(text=" ")
    spaceLeftLabel.config(text="    ")
    titleLabel.config(text="Welcome to SopiaOS! (operating script)")
    nameLabel.config(text=f'Name: {snippetData["title"]}')
    handleLabel.config(text=f'Handle: {snippetData["customUrl"]}')
    createdLabel.config(text=f'Day created: {time(snippetData["publishedAt"])}')
    countryLabel.config(text=f'Country: {snippetData.get("country", "Not set")}')
    viewsLabel.config(text=f'Views: {statistics["viewCount"]}')
    subsLabel.config(text=f'Subscribers: {statistics["subscriberCount"]}')
    videosLabel.config(text=f'Videos: {statistics["videoCount"]}')
    imageLabel.config(image=photo)
    imageLabel.image = photo

    contentDetails = itemsData["contentDetails"]
    relatedPlaylists = contentDetails["relatedPlaylists"]
    response = requests.get(
    "https://www.googleapis.com/youtube/v3/playlistItems",
    params={"part": "snippet", "playlistId": relatedPlaylists["uploads"], "key": API_KEY},
    )
    uploads = file("uploads.json", response)
    
    counter = 0
    uploadsList = [
        "Lastest videos:"
        "\n"
    ]
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
        video = file("video.json", response)
        videoData = video["items"][0]
        videoSnippet = videoData["snippet"]
        videoStats = videoData["statistics"]
        uploadsList.append(f'{title}     Views: {videoStats["viewCount"]}     Likes: {videoStats["likeCount"]}     Comments {videoStats["commentCount"]}')
        if videoSnippet["liveBroadcastContent"] == "upcoming":
            liveStreamingDetails = videoData["liveStreamingDetails"]
            uploadsList.append(f'This is an upcoming live or premier video, please come back later at {time(liveStreamingDetails["scheduledStartTime"])}')
        counter += 1
        uploadsList.append("\n")
    uploadsLabel.config(text="\n".join(uploadsList), compound="left")
        


root = ttk.Window(title="SopiaOS", themename="cyborg", size=(1920, 1080))

row = ttk.Frame(root)
row.pack(anchor="nw")
spaceTopLabel = ttk.Label(row)
spaceLeftLabel = ttk.Label(row)
spaceTopLabel.grid(row=0, column=0, sticky="w")
spaceLeftLabel.grid(row=0, column=0, sticky="w")
imageLabel = ttk.Label(row)
imageLabel.grid(row=1, column=1, rowspan=8, sticky="n", padx=(0,10))
titleLabel = ttk.Label(row, font=("Noto Sans", 14, "bold"))
nameLabel = ttk.Label(row)
handleLabel = ttk.Label(row)
createdLabel = ttk.Label(row)
countryLabel = ttk.Label(row)
viewsLabel = ttk.Label(row, bootstyle=INFO)
subsLabel = ttk.Label(row, bootstyle=SUCCESS)
videosLabel = ttk.Label(row)
uploadsLabel = ttk.Label(row)
uploadsLabel.grid(row=10, column=2, sticky="w")

button1 = ttk.Button()

for i, lbl in enumerate([titleLabel, nameLabel, handleLabel, createdLabel, countryLabel, viewsLabel, subsLabel, videosLabel]):
    lbl.grid(row=i+1, column=2, sticky="w")

root.after(100, starting_script)
root.mainloop()


print("Welcome to SopiaOS! (operating script)")
print("\n")

response = requests.get(
    "https://www.googleapis.com/youtube/v3/channels",
    params={"part": "snippet, statistics, contentDetails", "forHandle": "@SorashinaSopia", "key": API_KEY},
)
channelData = file("channelData.json", response)

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
uploads = file("uploads.json", response)

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
    video = file("video.json", response)
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
    video = file("video.json", response)
    playVideo(f"https://www.youtube.com/watch?v={resourceId["videoId"]}")
