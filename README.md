### JadedBot 2.5

JadedBot is a small, modular Discord bot. It started as a one-off for a single Discord community and has become more of a personal project for practicing Python and new programming concepts.

#### What's new in 2.5

- **Music queue** - `!stream` now queues tracks instead of talking over whatever's already playing, with `!skip`, `!queue`, `!pause`/`!resume`. A playlist link asks `!yes`/`!no` before queuing the whole thing.
- **Categorised `!help`** - commands are grouped by Music / Soundboard / Reactions / Search / Bot, with `!help <command>` and `!help <category>` for details.
- **Security fix** - `!reactionadd` could be made to write a file outside its `assets/` folder via a crafted name (e.g. `../../something`), and `!r` would then replay that file back into the channel on demand. Both the write and the read now resolve the real path and refuse anything that doesn't land inside `assets/`.
- **Single-instance guard** - if a second copy of the bot is started against the same token (e.g. a stray manual run alongside a systemd service), it now exits immediately instead of silently answering every command twice.
- Retired the old Reddit integration (`praw`) - it needed credentials most people running this bot don't have, and wasn't maintained.
- Fixed a typo that silently disabled the `!ram` alias for `!ramranch`.
- **Optional cogs** - a `cogs-optional/` folder for cogs that are off by default and opted into per-cog in `configfile`, starting with `!monsters` (Monsters & Memories wiki lookups). See [Optional cogs](#optional-cogs) below.

#### Features

- **Modular plugins** - each feature area is a separate cog (`cogs/*.py`) that can be hot-reloaded with `!load`/`!unload` without restarting the bot.
- **Music** - plays audio from YouTube and anywhere else [yt-dlp](https://github.com/yt-dlp/yt-dlp) supports, with a real queue, playlist confirmation, skip/pause/resume/volume, and text-to-speech.
- **Soundboard** - a set of short pre-recorded clips triggered by command name.
- **Reactions** - posts an image for a given command name; new ones can be added live with `!reactionadd`, backed by a small SQLite database (`reactions.db`) and the `assets/` folder, no restart required.
- **Wiki/item search** - `!everquest`/`!eq` searches the Project 1999 wiki, `!wow` searches WoWDB.
- **Extendable** - adding a feature is adding a cog; `jaded.py` just loads whatever's in `cogs/`. Cogs that aren't ready for everyone to have on by default go in `cogs-optional/` instead - see below.

### Installation

You'll need **Python 3.9 or newer** (developed and tested on 3.14) and **ffmpeg** if you want voice/audio features. Steps below are grouped by platform; all of them end up running the same `jaded.py` the same way.

#### Linux / BSD

##### FFmpeg

Install it through your package manager - e.g. on Arch:

```
$ sudo pacman -S ffmpeg
```

Debian/Ubuntu: `sudo apt install ffmpeg`. Confirm it worked:

```
$ ffmpeg -version
ffmpeg version 6.1 Copyright (c) 2000-2024 the FFmpeg developers
```

##### Python & pip

Most distributions ship Python 3 already. If `pip` isn't present, your package manager usually has it (`sudo pacman -S python-pip`, `sudo apt install python3-pip`), or use `curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python get-pip.py`.

##### Get the source and configure

```
$ git clone https://github.com/Virtual-/JadedBot
$ cd JadedBot
```

Running the bot once (`python jaded.py`) will fail but generate a blank `configfile` for you. Open it and set your bot's token:

```
[JadedBot]
TOKEN = DISCORDTOKENHERE
```

##### Virtual environment & dependencies

```
$ python -m venv bot-env
$ source ./bot-env/bin/activate
$ pip install --upgrade pip
$ pip install -r requirements.txt
```

Your prompt should now be prefixed with `(bot-env)`. Start the bot with:

```
$ python jaded.py
```

Run it somewhere persistent - GNU Screen, tmux, `nohup python3 jaded.py &`, or as a proper service (see below).

##### Updating dependencies

```
$ pip freeze | cut -d= -f1 | xargs -n1 pip install -U
```

##### Running as a systemd service (optional)

For an always-on bot on a Linux server, a unit like this (adjust the paths and user) keeps it running and restarts it if it crashes - and only ever as one instance, since `systemctl restart` stops the old process before starting the new one:

```ini
[Unit]
Description=JadedBot Discord Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/home/youruser/JadedBot
ExecStart=/home/youruser/JadedBot/bot-env/bin/python /home/youruser/JadedBot/jaded.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Save it as `/etc/systemd/system/jadedbot.service`, then `sudo systemctl enable --now jadedbot.service`. Use `sudo systemctl restart jadedbot.service` to apply code changes - don't start a second copy with a manual `python jaded.py` alongside it; the bot will refuse to start a second instance against the same working directory, but it's cleaner to only ever manage it through systemd.

#### macOS

##### FFmpeg

Install via [Homebrew](https://brew.sh):

```
$ brew install ffmpeg
```

##### Python

macOS ships an old system Python; install a current one via Homebrew instead:

```
$ brew install python
```

##### Source, virtual environment & dependencies

Same as Linux from here:

```
$ git clone https://github.com/Virtual-/JadedBot
$ cd JadedBot
$ python3 -m venv bot-env
$ source ./bot-env/bin/activate
$ pip install --upgrade pip
$ pip install -r requirements.txt
```

Run once to generate `configfile`, set your `TOKEN`, then `python jaded.py`. To keep it running after you close the terminal, the same `nohup`/`screen`/`tmux` approaches as Linux work fine; for an always-on setup, a [launchd](https://developer.apple.com/library/archive/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/CreatingLaunchdJobs.html) agent is the macOS equivalent of the systemd unit above.

#### Windows

> This section may need revisiting as tooling changes - please open an issue if a step is out of date.

##### Visual C++ Build Tools

Some Python packages need a C++ toolchain. Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/), then in "Visual Studio Installer" → "Modify" → Desktop & Mobile → "C++ build tools", make sure these are selected:

- MSVC v142 - VS 2019 C++ x64/x86 build tools
- Windows 10 SDK
- C++ CMake tools for Windows
- Testing tools core features
- C++ AddressSanitizer

Click "Modify" and wait for it to finish.

##### Python

Download and run the installer from [python.org](https://www.python.org/downloads/), making sure to check **"Add python.exe to PATH"**.

##### FFmpeg

Download a build from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z), extract it, rename the folder to `ffmpeg` and place it at `C:\ffmpeg`, so that `C:\ffmpeg\bin\ffmpeg.exe` exists. Add `C:\ffmpeg\bin` to your PATH (or the bot won't find it when launching voice).

##### JadedBot source

Download the latest release from the [releases page](https://github.com/Virtual-/JadedBot/releases), extract it, then shift+right-click inside the folder and choose "Open PowerShell window here".

```
> pip install -r requirements.txt
> pip freeze | %{$_.split('==')[0]} | %{pip install --upgrade $_}
```

Run `python jaded.py` once to generate `configfile`, open it and set `TOKEN` to your Discord bot token, then run `python jaded.py` again.

### Configuration

`configfile` is a simple INI file created automatically on first run:

```
[JadedBot]
TOKEN = DISCORDTOKENHERE
```

`TOKEN` is your Discord bot's token from the [Discord Developer Portal](https://discord.com/developers/applications). Nothing else is required for the core bot.

A fresh `configfile` also gets an `[OptionalCogs]` section for turning on cogs from `cogs-optional/` (off by default) - see [Optional cogs](#optional-cogs).

### Commands

`!help` in Discord always reflects exactly what's loaded and is the source of truth; the table below is a snapshot by category.

#### Music

| Command | Description |
|---|---|
| `!join` | Joins your current voice channel. |
| `!stream <search/URL>` (alias `!ytplay`) | Streams the track, or queues it if something is already playing. A playlist link asks for `!yes`/`!no` confirmation first. |
| `!yes` | Confirms queuing the playlist found by your last `!stream`. |
| `!no` | Declines the pending playlist and plays just the first track instead. |
| `!skip` (alias `!next`) | Skips to the next track in the queue. |
| `!queue` (alias `!q`) | Shows what's playing now and what's coming up. |
| `!pause` | Pauses the current track. |
| `!resume` | Resumes the current track. |
| `!volume <number>` | Changes the playback volume (0-100). |
| `!stop` | Stops playback and clears the queue. |
| `!leave` | Leaves the voice channel. |
| `!tts <text>` | Text to speech. |

#### Soundboard

A fixed set of short clips, each its own command: `!anime`, `!augh`, `!betterpoop`, `!ding`, `!excellent`, `!maybach`, `!nice`, `!nobodyhere` (alias `!nobody`), `!plug`, `!poopsock`, `!popping`, `!rack`, `!ram85`, `!ramranch` (alias `!ram`), `!sorry`, `!toasty`, `!trap1`-`!trap4`.

#### Reactions

| Command | Description |
|---|---|
| `!r <name>` (alias of `!reaction`) | Posts the image registered under `<name>`. |
| `!reactionlist` | Lists every reaction currently registered. |
| `!reactionadd <name> <url>` | Downloads the image at `<url>` and registers it as `<name>`, immediately usable via `!r <name>`. |

Run `!reactionlist` in your server for the current set - it grows over time as people add to it.

#### Search

| Command | Description |
|---|---|
| `!everquest <search>` (alias `!eq`) | Searches the Project 1999 wiki. |
| `!wow <search>` | Searches WoWDB. |

#### Monsters & Memories

**Optional - off by default**, lives in `cogs-optional/`; see [Optional cogs](#optional-cogs) to turn it on. Looks things up on the [Monsters & Memories wiki](https://monstersandmemories.miraheze.org/), an early-access MMO whose wiki is actively being filled in - treat gaps as "not written yet," not as bugs.

- `!monsters <search term>`
- `!monsters class 4` - Searches level 4 spells for specific class eg: `!monsters cleric 4`
- `!monsters class spells` - Lists the levels a class gets new spells at eg: `!monsters cleric spells`
- `!monsters maps` - Returns link to interactive map site.

Every class is its own subcommand (`!monsters cleric`, `!monsters archer`, etc. - run `!help monsters` for the full list), generated from the `CLASS_LEVELS` dict in `cogs-optional/monsters.py`.

#### Bot

| Command | Description |
|---|---|
| `!help [command\|category]` | Shows the command list, or details on one command/category. |
| `!version` | Shows the bot's version and, on Linux/macOS, the exact commit it's running. |
| `!load <module>` *(admin only)* | Hot-loads a cog from `cogs/` without restarting the bot. |
| `!unload <module>` *(admin only)* | Unloads a cog. |

### Optional cogs

`cogs-optional/` holds cogs that aren't part of the core bot - rougher, more experimental, or specific enough to one server that they shouldn't be on by default for everyone running JadedBot. Each one is **off unless you turn it on** in `configfile`:

```
[OptionalCogs]
monsters = true
```

The key is the cog's filename (`cogs-optional/monsters.py` → `monsters`). Leaving a key out, or setting it to `false`, keeps that cog unloaded - this is also what happens automatically on an existing `configfile` from before this section existed, so updating the bot never turns one on by surprise. Changes take effect on the next restart.

#### `!monsters` - maintenance notes

Command usage is documented under [Monsters & Memories](#monsters--memories) above; a couple of things worth knowing if you're maintaining the cog itself:

- **Per-class level lists are hardcoded**, not derived from a formula - caster classes get abilities roughly every 4 levels, melee classes get something almost every level, and it varies class to class. These were read off each class's page on the wiki at the time this cog was written and will drift as the game is patched; if a class stops matching or a level that should exist comes back empty, re-check that class's page on the wiki and update the list in `cogs-optional/monsters.py`.
- **Search is literal**, matching the wiki's own search box - it has no fuzzy or typo correction, so e.g. `nightharbour` (no space) finds nothing even though `night harbor` finds it immediately. This is a wiki limitation, not something the command works around.
- **Vendor info can be missing or placeholder text** (e.g. "Example Name") on newer pages - the cog shows whatever the wiki currently has rather than guessing.

### License

BSD 3-Clause - see [LICENSE](LICENSE).
