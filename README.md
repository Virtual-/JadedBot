### New JadedBot
The time came for a rewrite of the bot as the code beforehand was messy and I wanted to be able to add modules into the bot as it's running. Thus we now have a new and improved JadedBot 1.5 now with modular plugins.

More indepth README and installation guide coming in the next commits to this repo.


### Installation.

#### Unix/Linux/BSD
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

If reddit functionality is not required, rename `reddit.py` in the cogs directory to `reddit.py.backup`. Checks will be put in place in the later version to run without any tokens added to the configfile.

The token entry, the top `TOKEN` is your discord API key. The following two are only necessary if you want reddit functionality. If you want that follow this [guide](https://praw.readthedocs.io/en/latest/getting_started/authentication.html).

Start up the program with `$ python3 jaded.py`. It's best to run this in the background somehow, there are various ways to do this on Linux/BSD systems with GNU Screen, Tmux or simply running `$ python3 jaded.py &`.

### Dependencies

If you want to play music files over discord you will need an FFMPEG install in your $PATH. You will also need youtube-dl.

#### Windows 

TODO

### Usage

```
Jaded Bot

Music:
  join       !join <channelname> - Joins the channel.
  leave      !leave - Leaves the channel.
  stop       !stop - Stops and disconnects the bot from voice.
  stream     !stream <search/URL> - Directly streams the requested URL or search terms given.
  volume     !volume <number> - Changes the volume of the audio.
  ytplay     !ytplay <search/URL> - Downloads the file first beforehand, temporarily disabled for now.
  
Reactions:
  audiophile !audiophile - Places audiophile image into chat.
  
Reddit:
  greentext  !greentext - Grabs a random post from /r/greentext
  shitpost   !shitpost - Grabs a random post from /r/copypasta
  
Sounds:
  anime      !anime - Plays the WOW sound.
  augh       !augh - Plays the tim allen sound effect.
  betterpoop !betterpoop - Plays when mom find poopsock better version.
  ding       !ding - Plays the ding sound effect.
  excellent  !excellent - Plays the excellent sound effect.
  maybach    !maybach - Plays the Maybach music sound effect.
  nice       !nice - Plays the nice sound effect.
  nobodyhere !nobodyhere, !nobody - Plays nobody here.
  poopsock   !poopsock - Plays when mom find poopsock.
  popping    !popping - Plays the whats popping sound effect.
  ram85      !ram85 - Plays ram ranch 85
  ramranch   !ramranch, !ram - Plays ram ranch.
  sorry      !sorry - Plays the sorry for what sound effect.
  trap1      !trap1 - Plays the first trapaholics sound effect.
  trap2      !trap2 - Plays the second trapaholics sound effect.
  trap3      !trap3 - Plays the first trapaholics sound effect.
  trap4      !trap4 - Plays the first trapaholics sound effect.
  
WikiSearch:
  ck2        !ck2 <search> - Searches the CK2 wiki.
  ck3        !ck3 <search> - Searches the CK3 wiki.
  everquest  !everquest, !eq <search> - Searches the Project1999 wiki.
  runescape  !runescape, !rs <search> - Searched the OSRS wiki.
  
YouTube:
  vaporwave  !vaporwave - Searches youtube for vaporwave.
  youtube    !youtube <search> - Searches youtube with your search and returns the first link.
  
​No Category:
  help       Shows this message
```
