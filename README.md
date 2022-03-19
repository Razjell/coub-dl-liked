# coub-dl-liked
Download your liked videos from coub.com. Download mp3 and mp4 files and combine them together using `ffmpeg`. All videos will be looped to the length of the audio file.

### Dependencies
```Python
coub_api 
ffmpeg 
soundfile 
pandas
```

### Usage `download_liked_coubs.py`
1. go to https://coub.com/api/v2/timeline/likes?page=1&per_page=25
2. copy each page (e.g., page=1,page=2,page=...) from above to `mylikes.txt` file as a new line (I put 2 pages of my old likes as demo)
3. run the script

All video loops should be downloaded to `/videos` directory.

### Usage `download_tag_feed.py`
1. change `tag = 'cats'` to whatever tag you want to download from Coubs timeline
2. run the script

All video loops should be downloaded to `/videos` directory.

### Options
Both scripts have an option for downloading coubs without the watermark but if the option is selected then the video quality is lower.