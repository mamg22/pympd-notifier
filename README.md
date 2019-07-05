# pympd-notify

A python3 script that connects to mpd (Music Player Daemon) and pops a notification with the title, artist, elapsed time, duration, volume and state of the player.

Possible future features: 
* Message customization 
* Not hardcoding the settings (or at least provide a way to override them)
* Run in the background and send a notification on song change.

## Requirements

pympd-notify only requires:

* python-mpd2
* notify2

## Usage

` python3 mpd-notify.py ` and done.
