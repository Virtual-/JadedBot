### Installation.

The easiest time you'll have installing this bot is in a UNIX like environment such a Linux/BSD.

You made need sudo access for pip3 access aswell as ffmpeg installed on your system if you want to play music over voice channels.

```
$ git clone https://github.com/Virtual-/JadedBot
$ cd JadedBot
$ pip3 install -r requirements.txt
$ touch configfile
```

Notice at the end we created a configfile. This is the file that will hold the settings we need in order for the bot to work properly so edit the file and input the following:

```
[JadedBot]
TOKEN = DISCORDTOKENHERE
REDDIT_ID = REDDITTOKENHERE
REDDIT_SECRET = REDDITSECRETHERE
```

These entries in the file need to be filled, the top `TOKEN` is your discord API key. The following two are only necessary if you want reddit functionality. If you want that follow this [guide](https://praw.readthedocs.io/en/latest/getting_started/authentication.html).

Start up the program with `$ python3 jaded.py`. It's best to run this in the background somehow, there are various ways to do this on Linux/BSD systems with GNU Screen, Tmux or simply running `$ python3 jaded.py &`.


### Usage

```
Command List:
Help:
!jaded - Prints this command list.

Wiki Searching:
!everquest, !eq <search> - Searches P99 Wiki.
!ck2 <search> - Searches CK2 Wiki.
!ck3 <search> - Searches CK3 Wiki.
!rs <search> - Searches OSRS Wiki.

Youtube:
!youtube, !yt <search> - Searches youtube and returns first video.
!vaporwave - Returns random vaporwave track.

Misc:
!shitpost - Professionally shitposts in chat.
!redpill - Drops some fresh redpills from Alex Jones.
!audiophile - Inserts man listening to Edd Ed and Eddy Music.
!greentext - Inserts a random greentext.

Audio Controls:
!join - Joins the bot to the voice channel you're currently in.
!leave - Leaves the voice channel the bot is currently in.
!stop - Stops current audio.
!pause - Pauses current audio.
!play - Resumes current audio.

Sounds:
!nobodyhere, !nobody - There is nobody here.
!ding - Plays EQ sound effect.
!anime, !wow - Plays the woooow anime sound.
!popping - Whats pawppping.
!ramranch, !ram - Plays Ram Ranch.
!ramranch85, !ram85 - Plays Ram Ranch 85
!nice - Click. Nice.
!poopsock - Plays when mom find poop sock.
<<<<<<< HEAD
!sorry - Our daddy told us to never be ashamed of our...
!excellent - Excellent.
!augh - AUGH?!
```
