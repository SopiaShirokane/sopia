import requests
import os
import json
import ast
import subprocess
from datetime import datetime
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from io import BytesIO
from PIL import Image, ImageTk


API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY environment variable is not set. Please set it before running this script by using export API_KEY='your API key here'.")   

def plaympv(url):
    try:
        subprocess.Popen(["mpv", url])    
    except FileNotFoundError:
        print("mpv is not installed or not on PATH")
        return

def time(timestamp):
    formattedTime = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    return formattedTime.strftime("%d/%m/%Y %H:%M")

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
    

def thumbnailImg(snippet):
    thumbnail = snippet["thumbnails"]["maxres"]["url"]
    image = requests.get(thumbnail).content
    img = Image.open(BytesIO(image)).resize((256, 144))
    return ImageTk.PhotoImage(img)

def thumbnailTitle(upload, value):
    uploadsList = []
    uploadItems = upload["items"][value]
    uploadSnippet = uploadItems["snippet"]
    resourceId = uploadSnippet["resourceId"]
    s = uploadSnippet["title"]
    title = s.removeprefix("{'").removesuffix("'}")
    response = requests.get(
        "https://www.googleapis.com/youtube/v3/videos",
        params={"part": "snippet, statistics, contentDetails", "id": resourceId["videoId"], "key": API_KEY},
    )
    video = file("video.json", response)
    videoData = video["items"][0]
    videoSnippet = videoData["snippet"]
    videoStats = videoData["statistics"]
    uploadsList.append(f'{title}')
    uploadsList.append(f'   Views: {videoStats["viewCount"]}')
    uploadsList.append(f'   Likes: {videoStats.get("likeCount", "N/A")}')
    uploadsList.append(f'   Comments: {videoStats.get("commentCount", "N/A")}')
    uploadsList.append(f'   Release date: {time(videoSnippet["publishedAt"])}')
    link = f'https://www.youtube.com/watch?v={videoData["id"]}'
    return uploadsList, thumbnailImg(videoSnippet), link

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
    thumb1, img1, link1 = thumbnailTitle(uploads, 0)
    thumb2, img2, link2 = thumbnailTitle(uploads, 1)
    thumb3, img3, link3 = thumbnailTitle(uploads, 2)
    thumb4, img4, link4 = thumbnailTitle(uploads, 3)
    thumb5, img5, link5 = thumbnailTitle(uploads, 4)

    thumbnailsTitle.config(text="\nLatest videos:")    
    thumbnail1.config(image=img1, text="\n".join(thumb1), compound="left", cursor="hand2")
    thumbnail1.bind("<Button-1>", lambda event: plaympv(link1))
    thumbnail1.image = img1
    thumbnail2.config(image=img2, text="\n".join(thumb2), compound="left", cursor="hand2")
    thumbnail2.bind("<Button-1>", lambda event: plaympv(link2))    
    thumbnail2.image = img2
    thumbnail3.config(image=img3, text="\n".join(thumb3), compound="left", cursor="hand2")
    thumbnail3.bind("<Button-1>", lambda event: plaympv(link3))
    thumbnail3.image = img3
    thumbnail4.config(image=img4, text="\n".join(thumb4), compound="left", cursor="hand2")
    thumbnail4.bind("<Button-1>", lambda event: plaympv(link4))
    thumbnail4.image = img4
    thumbnail5.config(image=img5, text="\n".join(thumb5), compound="left", cursor="hand2")
    thumbnail5.bind("<Button-1>", lambda event: plaympv(link5))
    thumbnail5.image = img5


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
thumbnailsTitle = ttk.Label(row)
thumbnailsTitle.grid(row=9, column=2, sticky="w")
thumbnail1 = ttk.Label(row)
thumbnail1.grid(row=10, column=2, rowspan=8, sticky="w", padx=(0,10))
thumbnail2 = ttk.Label(row)
thumbnail2.grid(row=20, column=2, rowspan=8, sticky="w", padx=(0,10))
thumbnail3 = ttk.Label(row)
thumbnail3.grid(row=30, column=2, rowspan=8, sticky="w", padx=(0,10))
thumbnail4 = ttk.Label(row)
thumbnail4.grid(row=40, column=2, rowspan=8, sticky="w", padx=(0,10))
thumbnail5 = ttk.Label(row)
thumbnail5.grid(row=50, column=2, rowspan=8, sticky="w", padx=(0,10))

for i, lbl in enumerate([titleLabel, nameLabel, handleLabel, createdLabel, countryLabel, viewsLabel, subsLabel, videosLabel]):
    lbl.grid(row=i+1, column=2, sticky="w")

root.after(100, starting_script)
root.mainloop()
