# pympd-notify

A python3 script that connects to mpd (Music Player Daemon) and pops a notification with the title, artist, elapsed time, duration, volume and state of the player.

Possible future features: 
* Message customization
    * Simple data expansion
    * Conditional expansions
    * Provide via config file
* Not hardcoding the settings (or at least provide a way to override them)
    * Command line arguments
    * Config file
* Run in the background and send a notification on song change.

## Requirements

pympd-notify only requires:

* python-mpd2
* notify2

## Usage

` python3 mpd-notify.py ` and done.

## Why?

Because I have a keybind in the i3 window manager to show me my current song in mpd, but it was just showing the output of `mpc`, which looked horrible. 

So with a few lines, I got something that looks good and has the possibility of doing a lot more.
