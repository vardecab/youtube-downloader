# ==================================== #
#          youtube-downloader          #
# ==================================== #

# ------------ import libs ----------- #

# core ↓
import yt_dlp  # download YouTube videos # NOTE: https://github.com/ytdl-org/youtube-dl/issues/30102#issuecomment-943849906

# integrations ↓
import pyperclip # take data from user's clipboard
from pushbullet import Pushbullet # use Pushbullet API
from raindropiopy import API, Collection, CollectionRef, Raindrop # use Raindrop API

# notifications ↓
from sys import platform  # check platform (Windows/macOS)
if platform == "darwin":
    import pync  # macOS notifications
elif platform == 'win32':
    from plyer import notification  # Windows notification

# other ↓
import time  # calculate script's run time
from inputimeout import inputimeout, TimeoutOccurred # input timeout
from termcolor import colored # colored output in terminal 
import sys # take arguments from console
from itertools import chain # remove list nesting

# certificate problem solution ↓
# NOTE: fix certificate issue -> https://stackoverflow.com/questions/28282797/feedparser-parse-ssl-certificate-verify-failed
if platform == 'darwin':  # check if user is using macOS
    import ssl
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

# --------- start + run time --------- #

startTime = time.time()  # run time start
print("Starting the script...")  # status

# ---------- fun begins here --------- #

# ---------- other functions --------- #

# show notifications
def sendNotification(kind, title, channel): # kind = music/video
    try: 
        if platform == "darwin": # if macOS
            iconDownload = "icons/download.png" # use like this, direct doesn't work for some reason
            pync.notify(f'{title} by {channel} downloaded. Enjoy the {kind}!', title='youtube-downloader', contentImage=iconDownload)
        elif platform == "win32": # if Windows
            notification.notify(
                title='youtube-downloader',
                message=f'{title} by {channel} downloaded. Enjoy the {kind}!',
                app_icon='icons/download.ico')
    except: 
        print("Error in notifications!") # status

# remove nestings in lists
def listFlatter(list):
    URLs = [] # create a new list
    for item in list: # iterate through the list
        if isinstance(item, list):
            URLs.extend(listFlatter(item)) 
        else:
            URLs.append(item)
    return URLs
        
# ----- function for downloading ----- #

# save video's URL in a file so we don't download it in future 
def saveURLtoFile(videoURL):
    with open('videoURLs.txt', 'a') as readFile:
        print(colored("Saving YouTube URL in a .txt file...", 'green')) # status
        readFile.write(f"{videoURL}\n")

# check if we already downloaded that file
def checker(videoURL):
    
    videoURL = videoURL.strip() # remove whitespaces
    
    # check if videoURL already in a file, if yes then break and terminate the script, if not continue with the code
    with open('videoURLs.txt', 'r') as readFile:
        print(colored(f"Checking if we already downloaded this video: {videoURL}", 'green')) # status
        if videoURL not in readFile.read(): # can use
            return 700700 # random status code
        else: # already downloaded
            return 100100 # random status code
            
# download file ¯\_(ツ)_/¯
def downloadFile(videoURL, kind):
    
    videoURL = videoURL.strip() # remove whitespaces

    # if we want to download a video
    if kind == 'video':
        # different location for different OSes
        if platform == "win32": # Windows
            downloadPath = r'C:/Users/x/Videos/YouTube Downloads' # download location
        elif platform == "darwin": # macOS 
            downloadPath = r'/Users/q/Movies/YouTube Downloads' # download location
        
        #  parameters for the downloader if we're downloading a video
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
            # 'outtmpl': downloadPath + r'/%(title)s.%(ext)s',
            'outtmpl': downloadPath + r'/%(uploader)s/%(title)s.%(ext)s',

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
    
    # if we want to download music (extracted from a video)
    elif kind == 'music':
        # different location for different OSes
        if platform == "win32": # Windows
            downloadPath = r'C:/Users/x/Downloads/' # download location
        elif platform == "darwin": # macOS 
            downloadPath = r'/Users/q/Downloads' # download location
        
        # parameters for the downloader if we're downloading music
        optionalParameters = {
            'quiet': True, # don't throw status messages in the console
            'format': 'bestaudio/best', # download with best audio
            'outtmpl': downloadPath + r'/%(title)s.%(ext)s', # download location + name of the file
            'postprocessors': [{
                # extract music from video
                'key': 'FFmpegExtractAudio', # extract audio from the video file
                'preferredcodec': 'mp3', # codec
                'preferredquality': '320', # 320 kbps quality 
            }],
        }

    try:
        with yt_dlp.YoutubeDL(optionalParameters) as YouTubeDownloader: # take custom settings for the downloader (`optionalParameters`) and then download the file 
            
            getMetadata(videoURL) # get stuff like video title, channel name
            
            if kind == 'video': # if we want to download a video
                print(colored(f"Downloading '{videoTitle}' by {channelName} from YouTube...", 'green'))  # status
            elif kind == 'music': # if we want to download music (extracted from a video)
                print(colored(f"Downloading '{videoTitle}' by {channelName} from YouTube and then doing some magic to extract the music. It can take a while...", 'green')) # status
                
            YouTubeDownloader.download([videoURL])  # now download the file
            
            sendNotification(kind, videoTitle, channelName) # send notification to user
            
            print(colored(f"'{videoTitle}' by {channelName} downloaded. Enjoy the {kind}!", 'green'))  # status
            
            saveURLtoFile(videoURL) # save video URL to file so it doesn't get downloaded on the next run
                
    except:  # Internet down, wrong URL
        # status
        print(colored(f"Can't download the file. Check your internet connection and video's URL ({videoURL}), then try again. Closing...", 'red'))
    
# ------ playing with arguments ------ #

# get stuff like video title, channel name
def getMetadata(videoURL):
    
    global videoTitle, channelName # `global` so it can be used anywhere in the code without `return`
    
    optionalParameters = {'quiet': True} # don't throw status messages in the console
    
    with yt_dlp.YoutubeDL(optionalParameters) as YouTubeDownloader: # take custom settings for the downloader (`optionalParameters`) and then use the file 
        videoMetadata = YouTubeDownloader.extract_info(videoURL, download=False) # get the metadata of the video but don't download the file
        videoTitle = videoMetadata.get('title', 'None') # get the video title
        if len(videoTitle) > 25: # check if title is long
            videoTitle = f'{videoTitle[:25]}...' # truncate to 25 chars so it's not too long + add '...' to indicate the title is longer
        channelName = videoMetadata.get('uploader', 'None') # get channel name
        
    # no `return` because we are using global variables  

# ----- get links from sources/platforms ----- #

# take YouTube URL (if it exists) from user's clipboard
def takeFromClipboard():    
    
    clipboardData = pyperclip.paste() # take last copied item from the clipboard

    print(colored("Checking the clipboard...", 'green')) # status
    
    if "youtube.com" in clipboardData or "youtu.be" in clipboardData: # check if copied item is a YouTube URL
        print(colored("YouTube URL found in the clipboard!", 'green')) # status
        videoURL = clipboardData # change variable name 
        if checker(videoURL) == 700700: # can use
            print(colored(f"New video!", 'green')) # status
            return videoURL 
        else: # already downloaded
            print(colored(f"This video is already downloaded.", 'red')) # status
    else: # no YouTube URL in the clipboard
        print(colored(f"No YouTube URLs in the clipboard.", 'red')) # status
    
# take URLs from messages (pushes) sent via Pushbullet 
def takeFromPushbullet(): 
    
    # ------ get the messages/pushes ----- #
    
    # load API key from a .txt file
    with open('./api/PushbulletAPIkey.txt', 'r') as PushbulletAPIkey:
        print(colored(f"Taking Pushbullet API key...", 'green')) # status
        PushbulletAPIkey = PushbulletAPIkey.read().strip() # take value of the key as variable

    pushbullet = Pushbullet(PushbulletAPIkey) # initialize a Pushbullet object with API key

    print(colored(f"Getting latest pushes from the Pushbullet API...", 'green')) # status
    pushLimit = 10 
    pushes = pushbullet.get_pushes(limit=pushLimit) # retrieve a dictionary of most recent pushes from the API; without `limit` it takes 25 most recent pushes
    
    print(colored(f"Looking for a YouTube URL in the last {pushLimit} pushes...", 'green')) # status
    
    # ----- go through the dictionary ---- #
    
    PushbulletURLs = [] # create a list to store URLs
    
    for push in pushes:  
        if 'url' in push:
            pushURL = push.get('url') # get the URL from the dictionary
            if pushURL is None: # if there is no URL in the dictionary 
                print(colored("No YouTube URLs in latest Pushbullet messages.", 'red')) # status
            elif 'youtube.com' in pushURL or 'youtu.be' in pushURL: # but if there is a YouTube URL in the latest pushes then use it
                print(colored("Found a YouTube URL!", 'green')) # status
                PushbulletURLs.append(pushURL) # add URL to the list
        
    # ---- check if already downloaded --- #
    
    PushbulletURLsChecked = [] # new list for checked URLs
    if len(PushbulletURLs) != 0: # if not empty
        for videoURL in PushbulletURLs:
            if checker(videoURL) == 700700: # if this link hasn't been downloaded before
                print(colored(f"New video!", 'green')) # status
                PushbulletURLsChecked.append(videoURL) # add to the list
            else: # already downloaded
                print(colored(f"This video is already downloaded.", 'red')) # status
    else: # no good URLs
        print(colored(f"No YouTube URLs in Pushbullet.", 'red')) # status
                
    return PushbulletURLsChecked
    
# take URLs from bookmarks in Raindrop (Unsorted collection)
def takeFromRaindrop():
    
    # load API key from a .txt file
    with open('./api/RaindropAPIkey.txt', 'r') as RaindropAPIkey:
        print(colored(f"Taking Raindrop API key...", 'green')) # status
        RaindropAPIkey = RaindropAPIkey.read().strip() # take value of the key as variable
    
    # look for bookmarks with YouTube videos to download
    with API(RaindropAPIkey) as RaindropAPI:
        print(colored(f"Looking for Raindrop bookmarks to download...", 'green')) # status
        
        RaindropURLs = [] # create a new list
        
        for item in Raindrop.search(RaindropAPI, collection=CollectionRef.Unsorted): # check bookmarks in Unsorted collection
            if ('youtube' in item.link or 'youtu.be' in item.link): # look for YouTube links
                print(colored("Found a YouTube URL!", 'green')) # status
                RaindropURLs.append(item.link) # add to list
            else:
                print(colored("No YouTube URLs in Raindrop.", 'red')) # status

        RaindropURLsCleaned = [str(url) for url in RaindropURLs] # clean the list from unnecessary characters 
    
        # ---- check if already downloaded --- #
    
        RaindropURLsChecked = [] # create a new list 
        if len(RaindropURLsCleaned) != 0: # if not empty
            for videoURL in RaindropURLsCleaned:
                if checker(videoURL) == 700700: # if this link hasn't been downloaded before
                    print(colored(f"New video!", 'green')) # status
                    RaindropURLsChecked.append(videoURL) # add to the list
                else: # already downloaded
                    print(colored(f"This video is already downloaded.", 'red')) # status
        else: # no good URLs
            print(colored(f"No YouTube URLs in Raindrop.", 'red')) # status
                    
        # return RaindropURLsChecked
        return RaindropURLsChecked
    
# get the URL & arguments from the user if we don't have them (likely scenario if launched from .exe vs as a script in Terminal)
def helpTheUser(videoURL=None): # make a default so it doesn't crash if we call it without a parameter 
    
    # ------ build list and download ----- #
    
    URLsList = [] # create a new list to store URLs
    
    URLsList.append(takeFromPushbullet()) # add URLs from Pushbullet
    URLsList = list(chain(*URLsList)) # remove nested list from Pushbullet
    
    URLsList.append(takeFromRaindrop())
    
    clipboardData = takeFromClipboard()
    if clipboardData is not None: 
        URLsList.append(clipboardData) # add URLs from the clipboard
        
    # remove nestings & empty lists from the master list
    # print(URLsList) # debug
    # print(len(URLsList)) # debug
    URLsList = list(filter(None, URLsList)) # remove empty lists
    # print(URLsList) # debug
    # print(len(URLsList)) # debug
    URLsList = [item for sublist in URLsList for item in (sublist if isinstance(sublist, list) and len(sublist) > 0 else [sublist])] # remove nestings

    URLs = URLsList
        
    # -------- ask user for a link ------- #

    if len(URLs) <= 0: # if empty -> ask user
        counter = 0 # reset the counter
        while counter < 3: # give user 3 chances to paste a YouTube URL
            try:
                videoURL = inputimeout(colored("Paste YouTube video URL: ", 'blue'), timeout=15) # give user 15 seconds to paste a YouTube URL, otherwise close script
                if "youtube.com" in videoURL or "youtu.be" in videoURL: # if it's a correct URL skip to the main function
                    break # continue the script with that URL
                else: # invalid URL
                    print(colored("That URL is not a YouTube one. Try again.", 'red'))
                    counter += 1 # increase the counter
            except TimeoutOccurred: # time
                print(colored("Time's up! Closing...", 'red')) # status
                if platform == "darwin": # if macOS
                    # iconDownload = "icons/download.png" # use like this, direct doesn't work for some reason
                    pync.notify(f'Nothing new to download.', title='youtube-downloader', contentImage="") # debug
                quit() # close the script

        if counter == 3: # if user had their 3 chances already
            print(colored("Duh... Couldn't get the URL, closing...", 'red')) # status
            quit() # close the script
        else: # success, we have the correct URL
            print(colored(f"Got it! The YouTube video URL is: {videoURL}", 'green')) # status
            downloadFile(videoURL, "video") # assuming it's a video; no better idea now
            # TODO ^

    # ---------- get parameters ---------- #
    
    else: # if we have something nice in URLs list -> use it to download files 
        for videoURL in URLs:
            try: # `try` in case something goes wrong
                getMetadata(videoURL) # get stuff like video title, channel name
                
                userChoice = inputimeout(colored(f"Do you want to download '{videoTitle}' by {channelName} (v; default after 15 secs), extract the music (m), skip (x) or exit (e)?\n", 'blue'), timeout=15) # ask user, give them 15 seconds to decide 
            except TimeoutOccurred: # time ran out
                userChoice = "v" # default = video
                
            if userChoice == "v": 
                downloadFile(videoURL, 'video') # download video
            elif userChoice == "m": 
                downloadFile(videoURL, 'music') # download music
            elif userChoice == "x" or userChoice == "s": # skip
                print("Skipping...")
                saveURLtoFile(videoURL) # save video URL to file so it doesn't get downloaded on the next run
            elif userChoice == "c" or userChoice == "e": # finish the script
                print("Ok, bye!") # status
                sys.exit() # close the script
            else: 
                print("Unsupported command, bye!") # status
                sys.exit() # close the script
        
# ---------- launch and see ---------- #

if __name__ == "__main__": # code below only executed when launched directly, code above runs all the time when eg. imported to other .py file

    # launch looking for arguments 
# try:
    if len(sys.argv) == 1:
        print(colored("No video URL argument found at launch.", 'red'))
        result = helpTheUser() # we don't have anything so let's call the function and get the URL and arguments 
    elif len(sys.argv) == 2:
        print(colored("v/m argument was not passed.", 'red'))
        result= helpTheUser(sys.argv[1]) # send what we have ie. URL to function and get the rest ie. arguments 
    elif len(sys.argv) == 3: # we have everything so let's go; 3=2 so 2 arguments, eg. m URL => m for music and URL = YouTube URL; eg. `python youtube-downloader.py m "https://youtube.com/XXXXXX"`
        # "decode" the arguments
        if sys.argv[1] == "v": # video
            downloadFile((sys.argv[2])) # pass URL from console to function
        elif sys.argv[1] == "m": # music 
            downloadFile((sys.argv[2])) # pass URL from console to function
            
# ----------- fun ends here ---------- #

# ------------- run time ------------- #

endTime = time.time()  # run time end
totalRunTime = round(endTime-startTime, 2) # round to 0.xx
print(f"Total script run time: {totalRunTime} seconds. That's {round(totalRunTime/60,2)} minutes.") # status