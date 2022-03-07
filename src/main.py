
import os
from dataclasses import dataclass
from typing import List

from pytube import YouTube

@dataclass
class Song:
    url: str
    keywords: List[str]
    artist_name: str
    song_name: str

def download_mp3(url: str) -> str:
    youtube = YouTube(url)
    video = youtube.streams.filter(only_audio=True).first()
    out_file = video.download(output_path='../songs')
    print(out_file)
    base, ext = os.path.splitext(out_file)
    new_file = base + '.mp3'
    new_file = new_file.replace(" ", "_")
    print(new_file)
    os.rename(out_file, new_file)
    return new_file

download_mp3("https://www.youtube.com/watch?v=wOwblaKmyVw")
# /home/will/Code/music-server/src/../songs/Mr Data does not know what that is.mp4
# /home/will/Code/music-server/src/../songs/mr_data_does_not_know_what_that_is.mp3
