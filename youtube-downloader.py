# ==================================== #
#          youtube-downloader          #
# ==================================== #

# ------------ import libs ----------- #

# core ↓
import yt_dlp  # download YouTube videos # NOTE: https://github.com/ytdl-org/youtube-dl/issues/30102#issuecomment-943849906
import sys # take arguments from console

# other ↓
import time  # calculate script's run time

# certificate problem solution ↓
# NOTE: fix certificate issue -> https://stackoverflow.com/questions/28282797/feedparser-parse-ssl-certificate-verify-failed
import platform # check what OS user is using 
if platform == 'darwin':  # check if user is using macOS
    import ssl
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

# --------- start + run time --------- #

startTime = time.time()  # run time start
print("Starting the script...")  # status

# ---------- fun begins here --------- #

# ----- functions for downloading ---- #

# download video
def downloadVideo(videoURL):

    # different location for different OSes
    if platform.system() == 'Windows': # Windows
        downloadPath = r'C:/Users/x/Videos/TV Shows/Downloaded from YouTube' # download location
    # elif platform.system() == 'Darwin': # macOS 
    #     downloadPath = r'/Users/q/Downloads/Downloaded from YouTube/' # download location

    #  parameters for the downloader
    optionalParameters = {

        # format: max 1080p; .mp4 instead of default .webm # NOTE: ChatGPT
        'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/mp4',

        # download with better speed # NOTE: ChatGPT
        'external_downloader': 'aria2c',
        # param definitions ↓
        'external_downloader_args': ['-x', '16', '-s', '16', '-k', '100M'],
        # `-s 16`: This option specifies the number of segments to split the download into. A higher number can improve download speed, but may cause the server to block the download. In this case, it is set to 16 segments.
        # `-k 100M`: This option sets the maximum size of each segment to 100 megabytes (MB). This can also help improve download speed, as the downloader will download smaller chunks of the file at a time.

        'quiet': True,  # don't throw status messages in the console

        # download location + name of the file
        'outtmpl': downloadPath + r'/%(title)s.%(ext)s',

        # SponsorBlock
        'sponsorblock_remove': True,
        'postprocessors': [{
            'key': 'SponsorBlock',
            'categories': ['sponsor', 'selfpromo', 'interaction'] # segments that have to be removed
        }, {
            'key': 'ModifyChapters',
            'remove_sponsor_segments': ['sponsor', 'selfpromo', 'interaction'] # segments that have to be removed
        }]
    }

    try:
        with yt_dlp.YoutubeDL(optionalParameters) as YouTubeDownloader:
            # videoInfo = YouTubeDownloader.extract_info(videoURL, download=False) # get info (title, metadata, etc.) about the video without downloading

            print("Downloading the video from YouTube...")  # status
            YouTubeDownloader.download(videoURL)  # now download the video
            print("Video downloaded.")  # status
            # TODO: how to check if downloading or already on disk?
    except:  # Internet down, wrong URL
        # status
        print(f"Can't download the video. Check your internet connection and video's URL ({videoURL}), then try again. Closing...")
        
# download music
def downloadMusic(videoURL):
    
    # NOTE: ffmpeg (+ffprobe) must be downloaded from https://www.gyan.dev/ffmpeg/builds/ and added to PATH
    
    # different location for different OSes
    if platform.system() == 'Windows': # Windows
        downloadPath = r'C:/Users/x/Downloads/' # download location
    # elif platform.system() == 'Darwin': # macOS 
        # downloadPath = r'/Users/q/Downloads/Downloaded from YouTube/' # download location
    
    # parameters for the downloader
    optionalParameters = {
        'quiet': True, # don't throw status messages in the console
        'format': 'bestaudio/best',
        'outtmpl': downloadPath + r'/%(title)s.%(ext)s', # download location + name of the file
        'postprocessors': [{
            # extract music from video
            'key': 'FFmpegExtractAudio', # extract audio from the video file
            'preferredcodec': 'mp3', # codec
            'preferredquality': '320', # 320 kbps
        }],
    }
    try:
        with yt_dlp.YoutubeDL(optionalParameters) as YouTubeDownloader:
            print("Downloading the video from YouTube and then doing some magic to extract the music. It can take a while...") # status
            YouTubeDownloader.download(videoURL) # now download the music
            print("Music extracted and file saved. Enjoy!") # status
    except: # Internet down, wrong URL
        # status
        print(f"Can't download the music. Check your internet connection and video's URL ({videoURL}), then try again. Closing...")
            
# ------ playing with arguments ------ #

# get the URL & arguments if we don't have them (likely scenario if launched from .exe vs as a script in Terminal)
def helpTheUser(videoURL=None): # make a default so it doesn't crash if we call it without a parameter 
    
    # -------------- get URL ------------- #
    
    if videoURL is not None: # if we pass a parameter then we are good 
        videoURL = videoURL
    else: # but if we don't pass a parameter then we need to get it 
        print("Paste YouTube video URL: ")
        videoURL = input() # ask user for URL
        
    counter = 1 # reset the counter
    # check if URL is a YouTube URL and give user 3 chances to put a correct URL
    while (
        "youtube" not in videoURL
        and "youtu.be" not in videoURL
        and counter < 3
    ):
        print("That URL is not a YouTube one. Try again...")
        videoURL = input() # ask user for URL
        counter += 1 # increase the counter
    if counter == 3: # if user still can't paste a YouTube URL then close the script
        print("Duh...")
        exit()
    
    # ---------- get parameters ---------- #
    
    print("Do you want to download the video (v) or extract the music (m)?")
    userChoice = input() # ask user
    if userChoice == "v": 
        downloadVideo(videoURL) # download video
    elif userChoice == "m": 
        downloadMusic(videoURL) # download music
    else: 
        exit()
        
# ---------- launch and see ---------- #

try: 
    if len(sys.argv) == 1:
        print("No video URL found at launch.")
        helpTheUser() # we don't have anything so let's call the function and get the URL and arguments 
    elif len(sys.argv) == 2:
        print("Arguments were not passed.")
        helpTheUser(sys.argv[1]) # send what we have ie. URL to function and get the rest ie. arguments 
    elif len(sys.argv) == 3: # we have everything so let's go; 3=2 so 2 arguments, eg. m URL => m for music and URL = YouTube URL; eg. `python youtube-downloader.py m "https://youtube.com/XXXXXX"`
        # "decode" the arguments
        if sys.argv[1] == "v": # video
            downloadVideo((sys.argv[2])) # pass URL from console to function
        elif sys.argv[1] == "m": # music 
            downloadMusic((sys.argv[2])) # pass URL from console to function
except: 
    print('Something went wrong...')
    print('Closing...')
    exit()

# ----------- fun ends here ---------- #

# ------------- run time ------------- #

endTime = time.time()  # run time end
totalRunTime = round(endTime-startTime, 2)
print(f"Total script run time: {totalRunTime} seconds. That's {round(totalRunTime/60,2)} minutes.")