# youtube-downloader

![Actively Maintained](https://img.shields.io/badge/Maintenance%20Level-Actively%20Maintained-green.svg)
<br>
![](https://img.shields.io/badge/platform-Windows-blue)

<!-- >Experimenting a bit with downloading videos and music from YouTube. -->
>Experimenting a bit with downloading videos and music from YouTube. On demand or automatically using URL from clipboard or Pushbullet.

<!-- ## Screenshots -->

<!-- ### Windows -->

<!-- ![1]() -->

<!-- ### macOS -->
<!-- ![1]() -->
<!-- ![2]() -->

<!-- ## How to use

1.
2.
3. -->

## Release History

- 0.12.1: Fix for not saving URL in local file after downloading.
- 0.12: Added option to skip downloading but saving URL in the file.
- 0.11: Rewrote Pushbullet and clipboard parts to make it simpler + handle multiple downloads at once.
- 0.10.1: Removed `nothing` notification.
- 0.10: Added checks to see if video was already downloaded; added new notification type if there is nothing to download.
- 0.9: Taking video URL from a Pushbullet message; fixed a loop; added an option to terminate the script; fixed `youtube` -> `youtube.com` to avoid issues with paths in clipboard.
- 0.8: Simplified code by merging `downloadVideo()` & `downloadMusic()` functions into one: `downloadFile()`.
- 0.7: Simplified code by adding `getMetadata()` function; when taking URL from user's clipboard show `videoTitle` & `channelName` so user knows what's gonna be downloaded.
- 0.6: Added `videoTitle` and `channelName` to notifications.
- 0.5: Taking video URL from clipboard if there is one.
- 0.4: Started integration w/ my other project: [web-youtube-downloader](https://github.com/vardecab/web-youtube-downloader); new videos will be downloaded to folders named after YouTube's channel name.
- 0.3: Added colored output in terminal.
- 0.2: Added Windows and macOS notifications; fixed script not working when URL had whitespaces.
- 0.1: Initial, fully functioning release.

<!-- <details> -->

<!-- <summary>
Click to see all updates < 1.0.0
</summary> -->

<!-- - 0.2: 
- 0.1: Initial release.
</details> -->

<!-- <br> -->

## Versioning

Using [SemVer](http://semver.org/).

## License

![](https://img.shields.io/github/license/vardecab/youtube-downloader)

## Acknowledgements

- [yt-dlp](https://pypi.org/project/yt-dlp/) to download videos
- [ChatGPT](https://chat.openai.com/chat) for brainstorming
- [plyer](https://pypi.org/project/plyer/) for notifications on Windows
- [pync](https://github.com/SeTeM/pync) for notifications on macOS
- [pyperclip](https://pypi.org/project/pyperclip/) to use user's clipboard
- [termcolor](https://pypi.org/project/termcolor/) to have colors in terminal
- [inputimeout ](https://pypi.org/project/inputimeout/) to auto-advance without user's input
- [Flaticon](https://www.flaticon.com) for icons
- [Pushbullet API](https://www.pushbullet.com)

## Contributing

![](https://img.shields.io/github/issues/vardecab/youtube-downloader)

If you found a bug or want to propose a feature, feel free to visit [the Issues page](https://github.com/vardecab/youtube-downloader/issues).
