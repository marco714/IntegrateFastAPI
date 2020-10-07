from googleapiclient.discovery import build
from dataclasses import dataclass, field
from fastapi import FastAPI, Query, Request
from pydantic import BaseModel
from typing import List
from datetime import timedelta
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import pprint
import re


templates = Jinja2Templates(directory="templates")
app = FastAPI()

# Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/static/img", StaticFiles(directory="static"), name="img")

# CORS / Middle Ware
origins = [
    "http://127.0.0.1:5000",
    "http://127.0.0.1:8000",
    "http://localhost:5000",
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@dataclass
class YoutubeAPI:

    serviceName:str
    version:str
    api_key:str
    youtube: object = field(init=False)

    def __post_init__(self):

        self.youtube = build(self.serviceName, self.version, developerKey=self.api_key)


@app.get("/")
async def index(request:Request):

    return templates.TemplateResponse("get_playlist.html", {
        "request":request
    })

@app.get("/vid_details")
async def playlist_video(request:Request):

    return templates.TemplateResponse("video_details.html", {
        "request":request
    })

@app.get("/playlist_duration")
async def playlist_duration(request:Request):
    
    return templates.TemplateResponse("get_duration.html", {
        "request":request
    })

    
@app.get("/get_details")
async def get_details(service_name: str = Query(...), version: str = Query(...), api_key: str = Query(..., max_length=39)):
     
    youtube_service = YoutubeAPI(service_name, version, api_key)
    youtube = youtube_service.youtube

    request = youtube.channels().list(
        part='contentDetails, statistics',
        forUsername='schafer5'
    )

    response = request.execute()

    return {"channel_id":response['items'][0]['id'], "subscriberCount":response['items'][0]['statistics']['subscriberCount'], "videoCount": response['items'][0]['statistics']['videoCount']}


@app.get("/get_playlist")
async def get_playlist(service_name: str = Query(...), version: str = Query(...), api_key: str = Query(..., max_length=39)):
     
    youtube_service = YoutubeAPI(service_name, version, api_key)
    youtube = youtube_service.youtube

    pl_request = youtube.playlists().list(
        part='contentDetails, snippet',
        channelId="UCCezIgC97PvUuR4_gbFUs5g"
    )


    pl_response = pl_request.execute()
    # print(f"I am here {pl_response}")

    titles = dict()
    title = dict()

    for item in pl_response['items']:
        

        title[item['snippet']['title']] = {
            "PlayList_Id":item['id'],
            "channelTitles":item['snippet']['channelTitle'],
            "publishedAt":item['snippet']['publishedAt'].split("T")[0],
            "thumbnail":item['snippet']['thumbnails']['default']['url'],
            "Description":item['snippet']['description']
        }


        titles.update(title)

    return {"Response":titles}


@app.put("/video_details")
async def video_details(service_name: str = Query(...), version: str = Query(...), api_key: str = Query(..., max_length=39)):
     
    youtube_service = YoutubeAPI(service_name, version, api_key)
    youtube = youtube_service.youtube

    nextPageToken = None

    while True:
        request = youtube.playlistItems().list(
            part='contentDetails, snippet',
            playlistId='PL-osiE80TeTvipOqomVEeZ1HRrcEvtZB_',
            maxResults=50,
            pageToken=nextPageToken
        )

        response = request.execute()
        

        videos = dict()
        video = dict()
        print(f" Hello{response}")
        count = 1
        for item in response['items']:

            video[f'Video{count}'] = {
                "Title":item['snippet']['title'],
                "videoId":item['contentDetails']['videoId'],
                "videoPublishedAt":item['contentDetails']['videoPublishedAt'].split("T")[0],
                "Thumbnail":item['snippet']['thumbnails']['medium']['url']
            }
            # print(item)

            count += 1
            videos.update(video)

        nextPageToken = response.get('nextPageToken')
        print(nextPageToken)

        if not nextPageToken:
            break

    return {"Response":videos}



class videoList(BaseModel):
    videos: List[str]


@app.put("/get_duration")
async def get_duration(videos: videoList, service_name: str = Query(...), version: str = Query(...), api_key: str = Query(..., max_length=39)):
    
    minutes_pattern = re.compile(r'(\d+)M')
    seconds_pattern = re.compile(r'(\d+)S')
    hours_pattern = re.compile(r'(\d+)H')

    total_second = 0

    videoList = list()
    for vid in videos.videos:
        videoList.append(vid)

    youtube_service = YoutubeAPI(service_name, version, api_key)
    youtube = youtube_service.youtube

    print(','.join(videoList))

    request = youtube.videos().list(
        part="contentDetails",
        id=','.join(videoList)
    )

    response = request.execute()

    for item in response['items']:
        duration = item['contentDetails']['duration']

        hours = hours_pattern.search(duration)
        minutes = minutes_pattern.search(duration)
        seconds = seconds_pattern.search(duration)

        minutes = int(minutes.group(1)) if minutes else 0
        seconds = int(seconds.group(1)) if seconds else 0
        hours = int(hours.group(1)) if hours else 0
        
        video_seconds = timedelta(
            hours=hours,
            minutes=minutes,
            seconds=seconds
        ).total_seconds()

        total_second += video_seconds

        print(video_seconds)
        print()
    
    print(f"I am here {total_second}")
    
    total_second = int(total_second)
    minutes, seconds = divmod(total_second, 60)
    hours, minutes = divmod(minutes, 60)


    return {"Hours":hours, "Minutes":minutes, "Seconds":seconds}


@app.get("/get_the_page")
def get_the_page():

    return {"Message":"I am here"}

if __name__ == "__main__":

    uvicorn.run("yt:app", host="127.0.0.1", port=5000)

