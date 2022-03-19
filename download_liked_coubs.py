import os
from coub_api import CoubApi
import urllib
import soundfile as sf
import pandas as pd

# use CoubApi
api = CoubApi()

# https://coub.com/api/v2/users/me

""" Couldnt get it to work with my access token
os.environ.get("your access token can be found in above link")
api.authenticate("your access token can be found in above link")
api.timeline.me_liked()
"""
# the last line gives me HTTPError: 403 Client Error: Forbidden for url: https://coub.com/api/v2/timeline/likes?page=1&per_page=10&access_token=....
# if somebody can fix the above that would be ideal... 
# but I didn't have time to do it so did it manually with steps below

# 1. go to https://coub.com/api/v2/timeline/likes?page=1&per_page=25
# 2. copy each page (e.g., page=1,page=2,page=...) from above to mylikes.txt file as a new line (I put 2 pages of my old likes as demo)
# 3. run code below

with open('./mylikes.txt', encoding="utf8") as f:
    likes = f.readlines()

# awkwardly find IDs from the coub api data structure... 
ALL_IDs = []
for i in range(len(likes)):
    print(i)
    for j  in likes[i].split(':'):
        if j.split(',')[0].isnumeric():
            try:
                if j.split(',')[1] == '"type"': # this should filter your liked video IDs only
                    ALL_IDs.append(j.split(',')[0])
            except:
                pass
# save IDs as .csv - might be useful to save if the above takes a long time 
pd.DataFrame(ALL_IDs).to_csv('ALL_IDs.csv')

# load up IDs
ALL_IDs = pd.read_csv('./ALL_IDs.csv') 

# filter short IDs which are not actually videos
IDs = []
for i in ALL_IDs.to_numpy()[:,1]: # use 1st col
    if i not in IDs and len(str(i)) >= 8: # >= IDs len 8 and 9 are the ones with my liked videos
        IDs.append(i)

# download liked videos to dir videos/
with_watermarks = True
for id in IDs:
    try:
        # use coub API to get target coub
        coub = api.coubs.get_coub(str(id))
        
        # get audio from coub API
        mp3_url = coub.file_versions.dict()['html5']['audio']['high']['url'].split()[0]
        mp3_fln = coub.file_versions.dict()['html5']['audio']['high']['url'].split()[0].split('/')[-1]
        if with_watermarks:
            # mp4 download link with watermarks
            video_url = coub.file_versions.dict()['html5']['video']['high']['url'].split()[0]
            video_fln = coub.file_versions.dict()['html5']['video']['high']['url'].split()[0].split('/')[-1]
        else:
            # try geting videos without watermarks but video quality is lower
            urllib.request.urlretrieve(f'https://coub.com/api/v2/coubs/{id}/segments', 'segments.txt')
            with open('./segments.txt', encoding="utf8") as f:
                seg = f.readlines()
            # choose first mp4 download link 
            video_url = seg[0].split()[0].split('"cutter_ios":')[1].split('"')[1]
            video_fln = video_url.split('/')[-1]

        # download mp3 and mp4 files from coub.com
        urllib.request.urlretrieve(mp3_url, mp3_fln)	
        urllib.request.urlretrieve(video_url, video_fln) 

        # filenames
        out_video_fln = f'{id}.mp4'
        out_video_fln_tmp = f'{id}_tmp.mp4'
        out_wav_fln = f'{id}.wav'

        # convert mp3 to wav
        os.system(f'ffmpeg -i {mp3_fln} -vn -acodec pcm_s16le -ac 2 -ar 44100 -f wav {out_wav_fln}')
        # read wav and get file len in seconds
        x, sr = sf.read(f'{out_wav_fln}')
        wav_len = len(x)/sr
        # loop video to duration of file len
        os.system(f'ffmpeg -stream_loop -1 -t {wav_len} -i {video_fln} -c copy {out_video_fln_tmp}')
        # combine MP3 with looped video
        os.system(f'ffmpeg -i {out_video_fln_tmp} -i {mp3_fln} -c:a aac -map 0:v:0 -map 1:a:0 videos/{out_video_fln}')
        # remove temp files
        os.system(f'rm {out_video_fln_tmp} {out_wav_fln} {mp3_fln} {video_fln} segments.txt')
    except: # nothing should go wrong but if it does ignore it
        pass
