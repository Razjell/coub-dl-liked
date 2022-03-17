import os
from coub_api import CoubApi
import urllib.request
import soundfile as sf

# use CoubApi
api = CoubApi()

# download videos tagged with "cats" to dir videos/
tag = 'cats' # choose whatever string of characters you want
for i in range(1000):
    try:
        likes = api.timeline.tag_feed(tag, page=i+1, order_by='newest')

        for id_ in likes.coubs:
            id = id_.id
            try:
                # use coub API to get target coub
                coub = api.coubs.get_coub(str(id))

                # get audio from coub API
                mp3_url = coub.file_versions.dict()['html5']['audio']['high']['url'].split()[0]
                mp3_fln = coub.file_versions.dict()['html5']['audio']['high']['url'].split()[0].split('/')[-1]
                video_url = coub.file_versions.dict()['html5']['video']['high']['url'].split()[0]
                video_fln = coub.file_versions.dict()['html5']['video']['high']['url'].split()[0].split('/')[-1]

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
                os.system(f'ffmpeg -i {out_video_fln_tmp} -i {mp3_fln} -c:v copy -c:a aac videos/{out_video_fln}')
                # remove temp files
                os.system(f'rm {out_video_fln_tmp} {out_wav_fln} {mp3_fln} {video_fln}')
            except: # nothing should go wrong but if it does ignore it
                pass
    except:
        pass
    