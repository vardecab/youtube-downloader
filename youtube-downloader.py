# ==================================== #
#          youtube-downloader          #
# ==================================== #

# ------------ import libs ----------- #

# core ↓
import yt_dlp  # download YouTube videos # NOTE: https://github.com/ytdl-org/youtube-dl/issues/30102#issuecomment-943849906

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
import pyperclip # take data from user's clipboard
from pushbullet import Pushbullet # use Pushbullet API
import sys # take arguments from console

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

# -- function to show notifications -- #

# show notifications
def sendNotification(kind, title, channel): # kind = music/video
    try: 
        if kind == 'nothing':
        # TODO: remove entirely? 
            if platform == "win32": # if Windows
                notification.notify(
                    title='youtube-downloader',
                    message=f'{kind.capitalize()} new to download.',
                    # app_icon='icons/no_updates.ico'
                    app_icon=None,
                    app_name=None)
    # TODO: macOS
        else:
            if platform == "darwin": # if macOS
                pync.notify(f'{kind} downloaded. Enjoy!', title='youtube-downloader', subtitle='',
                            open="", sound="", contentImage="icons/download.png")
            elif platform == "win32": # if Windows
                notification.notify(
                    title='youtube-downloader',
                    message=f'{title} by {channel} downloaded. Enjoy the {kind}!',
                    app_icon='icons/download.ico')
    except: 
        print("Error in notifications.") # status
        
# ----- function for downloading ----- #

# check if we already downloaded that file
# TODO: if check from Pushbullet is positive we should look at clipboard next instead of terminating the script
def checker(videoURL):
    
    videoURL = videoURL.strip() # remove whitespaces
    
    # check if videoURL already in a file, if yes then break and terminate the script, if not continue with the code
    with open('videoURLs.txt', 'r') as readFile:
        print(colored(f"Checking if we already downloaded this video: {videoURL}", 'green')) # status
        if videoURL not in readFile.read():
            # # save videoURL in a .txt file
            # with open('videoURLs.txt', 'a') as readFile:
            #     print(colored("New URL, great! Saving YouTube URL in a .txt file...", 'green')) # status
            #     readFile.write(f"{videoURL}\n")
            return videoURL # URL not in a file, let's use it
        else: 
            # print(colored('File already downloaded, enjoy!', 'green')) # status
            # sendNotification("nothing", 0, 0) # send notification saying we don't have new videos # FIX: plyer throws error
            
            # TODO: if check from Pushbullet is positive we should look at clipboard next instead of terminating the script
            return 100 # random success code
            # sys.exit() # close the script

# download file ¯\_(ツ)_/¯
def downloadFile(videoURL, kind):
    
    videoURL = videoURL.strip() # remove whitespaces

    # if we want to download a video
    if kind == 'video':
        # different location for different OSes
        if platform == "win32": # Windows
            downloadPath = r'C:/Users/x/Videos/YouTube Downloads' # download location
        elif platform == "darwin": # macOS 
            downloadPath = r'/Users/q/Videos/YouTube Downloads/' # download location
        
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
            
            # save newly downloaded video's URL in a file so we don't download it in future 
            with open('videoURLs.txt', 'a') as readFile:
                print(colored("New URL, great! Saving YouTube URL in a .txt file...", 'green')) # status
                readFile.write(f"{videoURL}\n")
                
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

# take YouTube URL (if it exists) from user's clipboard
def takeFromClipboard():    
    
    clipboardData = pyperclip.paste() # take last item in user's clipboard

    print(colored("Checking the clipboard...", 'green')) # status
    
    if "youtube.com" in clipboardData or "youtu.be" in clipboardData: # check if user has what we need
        print(colored("YouTube URL found in the clipboard!", 'green')) # status
        # checker(clipboardData) # check if we already downloaded that file
        if checker(clipboardData) == 100:
            print(colored("Already downloaded! XYZ", 'green')) # status
        else: 
            return clipboardData # return so we can use it
    else: # if not
        print(colored(f"No YouTube URLs in the clipboard.", 'red')) # status
        return 7 # return random number ¯\_(ツ)_/¯
    
# take URL from a message sent via Pushbullet 
def takeFromPushbullet(): 
    
    # load API key from a .txt file
    with open('./api/pushbulletAPIkey.txt', 'r') as pushbulletAPIkey:
        print(colored(f"Taking Pushbullet API key...", 'green')) # status
        pushbulletAPIkey = pushbulletAPIkey.read().strip() # take value of the key as variable

    pushbullet = Pushbullet(pushbulletAPIkey) # initialize a Pushbullet object with API key

    print(colored(f"Getting latest pushes from the Pushbullet API...", 'green')) # status
    pushes = pushbullet.get_pushes(limit=5) # retrieve a dictionary of most recent pushes from the API; without `limit` it takes 25 most recent pushes
    print(colored(f"Looking for a YouTube URL...", 'green')) # status
    # go through the dictionary

    # TODO — go through all pushes instead of stopping on the latest, ie. if there are 5 pushes and 3 of them contain YouTube link => download function should run on all 3 of these instead of the newest
    # TODO — add all of the them to a list and then go through the list in the downloader
    for push in pushes:  
        if 'url' in push:
            pushURL = push.get('url') # get the URL from the dictionary
            if pushURL is None: # if there is no URL in the dictionary 
                print(colored("No YouTube URLs in latest Pushbullet messages.", 'red'))
                return 4 # return random number ¿\_(ツ)_/¿
            elif 'youtube.com' in pushURL or 'youtu.be' in pushURL: # but if there is a YouTube URL in the latest pushes then use it
                print(colored("Found a YouTube URL!", 'green')) # status
                # checker(pushURL) # check if we already downloaded that file
                
                # TODO: if 100 then move to clipboard, if false download
                if checker(pushURL) == 100: 
                    print(colored("Already downloaded! XYZ", 'green')) # status
                else:
                    return pushURL # give it back to the main function 
                    # takeFromClipboard()
        else: 
            print(colored("No YouTube URLs in latest Pushbullet messages.", 'red'))
            return 4 # return random number ¿\_(ツ)_/¿  
    
# get the URL & arguments from the user if we don't have them (likely scenario if launched from .exe vs as a script in Terminal)
def helpTheUser(videoURL=None): # make a default so it doesn't crash if we call it without a parameter 
    
    # -------------- get URL ------------- #
    
    if videoURL is not None: # if we pass a parameter then we are good 
        videoURL = videoURL
    else: # but if we don't pass a parameter then we need to get it 
        clipboardData = takeFromClipboard() # let's take what's in clipboard
        if not clipboardData == 7: # ok, looks like a YouTube URL, let's use it
            print(colored(f"Taking URL from clipboard: {clipboardData} ", 'green')) # status
            videoURL = clipboardData # use URL from clipboard as our video
        else: # no YouTube URL in user's clipboard, let's ask for it
            # print(colored("Couldn't find YouTube URL in clipboard.", 'red')) # status
            pushbulletData = takeFromPushbullet() # let's take what was sent via Pushbullet
            if (not pushbulletData == 4) and (pushbulletData != None): # ok, looks like a YouTube URL, let's use it
                print(colored(f"Taking URL from Pushbullet: {pushbulletData} ", 'green')) # status
                videoURL = pushbulletData # use URL from Pushbullet as our video
            else: # if Pushbullet messages are useless then look at the clipboard
                
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
                        # sendNotification("nothing", 0, 0) # send notification saying we don't have new videos # FIX: plyer throws error
                        quit() # close the script

                if counter == 3: # if user had their 3 chances already
                    print(colored("Duh... Couldn't get the URL, closing...", 'red')) # status
                    quit() # close the script
                else: # success, we have the correct URL
                    print(colored(f"Got it! The YouTube video URL is: {videoURL}", 'green')) # status
        
    # ---------- get parameters ---------- #
    
    try: # `try` in case something goes wrong 
        getMetadata(videoURL) # get stuff like video title, channel name
        
        userChoice = inputimeout(colored(f"Do you want to download '{videoTitle}' by {channelName} (v; default after 15 secs) or extract the music (m)?\n", 'blue'), timeout=15) # ask user, give them 15 seconds to decide 
    except TimeoutOccurred: # time ran out
        userChoice = "v" # default = video
        
    if userChoice == "v": 
        downloadFile(videoURL, 'video') # download video
    elif userChoice == "m": 
        downloadFile(videoURL, 'music') # download music
    elif userChoice == "c" or userChoice == "e": # finish the script
        print("Ok, bye!") # status
        sys.exit() # close the script
    else: 
        print("Ok, bye!") # status
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