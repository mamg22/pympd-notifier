# pympd-status

A python3 script that connects to mpd (Music Player Daemon) and gets the data you want, be it the song's data or the player state.

Possible future features: 
* Message customization
    * Conditional expansions
* Not hardcoding the settings (or at least provide a way to override them)
    * Command line arguments
* Run in the background and send a notification on song change.
* Print a new line with the next song data for your `i3bar` or `lemonbar` on song change (or any change).

## Requirements

pympd-status only requires:

* python-mpd2
* notify2
* dbus-python
* toml

## Usage

` python3 pympd-status.py ` and done.

Or set the executable bit `chmod +x pympd-status.py` and run it with `./pympd-status.py` or other place where it is.

## Why?

Because I have a keybind in the i3 window manager to show me my current song in mpd, but it was just showing the output of `mpc`, which looked bad, and required a lot of parsing to look ok; there's also `mpc current` but it only gets metadata from song, but I want to know how much of that song has passed or if I still have consume mode on!.
