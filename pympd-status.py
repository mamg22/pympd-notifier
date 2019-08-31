#!/usr/bin/env python3

import string 
from os.path import expanduser
import argparse

import mpd
import notify2
import toml

# Convert floating point strings to HH:MM:SS time
def format_time(seconds):
    try:
        secs = float(seconds)
    except:
        # Not valid time
        return ""
    # Clamp the numbers into the correct ranges
    hours = round(secs // 3600)
    minutes = round((secs // 60) % 60)
    secs = round(secs % 60)
    # Pad seconds with 0's
    out = f"{secs:02d}"
    if hours > 0:
        # If including hours then pad minutes with 0's
        out = f"{hours}:{minutes:02d}:" + out
    else:
        # Else just put the minutes
        out = f"{minutes}:" + out
    return out

def extract_info(current_song, state):
    info = {}
    # Song metadata
    info["artist"] = current_song.get("artist", "")
    info["title"]  = current_song.get("title", "")
    info["album_artist"] = current_song.get("albumartist", "")
    info["album"] = current_song.get("album", "")
    info["date"] = current_song.get("date", "")
    info["genre"] = current_song.get("genre", "")
    info["composer"] = current_song.get("composer", "")
    info["track"] = current_song.get("track", "")
    info["disc"] = current_song.get("disc", "")

    # The filename
    info["filename"] = current_song.get("file", "")

    # Song status
    info["elapsed"] = format_time(state.get("elapsed", ""))
    info["duration"] = format_time(state.get("duration", ""))

    # Playlist status
    info["playlist_current"] = state.get("song", "")
    info["playlist_length"] = state.get("playlistlength", "")

    # Player status
    volume = state.get("volume", "") + "%"
    if volume == "-1%":
        # mpd is stopped
        volume = "N/A"
    info["volume"] = volume

    info["state"] = state.get("state", "")

    info["repeat"] = state.get("repeat", "")
    info["random"] = state.get("random", "")
    info["single"] = state.get("single", "")
    info["consume"] = state.get("consume", "")
    info["xfade"] = state.get("xfade", "0")

    info["updating_db"] = state.get("updating_db", "0")
    if info["updating_db"] != "0":
        info["updating_db"] = "1"

    # TODO? Use the the nextsong state key to provide info about the next song

    return info

def expand(argument, information):
    return information.get(argument, "")

def format_state_ncmpcpp(argument, information):
    out = "[ "
    flags = [ ("repeat",  "r "),
              ("random",  "z "),
              ("single",  "s "),
              ("consume", "c "),
              ("xfade",   "x ")
            ]
    for flag in flags:
        if information[flag[0]] == "0":
            out += "- "
        else:
            out += flag[1]
    return out + "]"

def echo(argument, information):
    return arg

def parse_fmt_str(fmt_str, information):
    # format: $function{argument}
    # ${} is an alias for $expand{}
    # TODO: Wrap this in an object, so it can have a mapping of functions (maybe)
    out = ""
    mode = "normal"
    name = "" # Variable or function name
    argument = "" # function argument
    escape = False
    functions = {
        "": expand,
        "expand": expand,
        "ncmpcpp_state": format_state_ncmpcpp,
        "echo": echo,
        }
    for char in fmt_str:
        if mode == "normal":
            if not escape:
                if char == "$":
                    mode = "read_name"
                elif char == "\\":
                    escape = True
                else:
                    out += char
            else:
                out += char
                escape = False
        elif mode == "read_name":
            if not escape:
                if char in string.ascii_letters + string.digits + "_":
                    # Names are only [a-zA-Z0-9_]
                    name += char
                elif char == "{":
                    mode = "read_arg"
                else:
                    out += expand(name, information)
                    if char == "\\":
                        escape = True
                    else:
                        out += char
                    name = ""
                    mode = "normal"
            else:
                out += expand(name, information) + char
                name = ""
                mode = "normal"

        elif mode == "read_arg":
            if not escape:
                if char == "}":
                    out += functions[name](argument, information)
                    mode = "normal"
                    name = ""
                    argument = ""
                else:
                    if char == "\\":
                        escape = True
                    else:
                        argument += char
            else:
                argument += char
                escape = False
        else:
            out += char
            escape = False
    # Expand remaining variable, if any
    if mode == "read_name":
        out += expand(name, information)
    return out

def main():
    # Setup argument parser
    argparser = argparse.ArgumentParser(description="Query MPD status and print to stdout or send in a notification")
    argparser.add_argument("-n", "--notify", action="store_true",
                           help="Send a desktop notification and not print to stdout")
    argparser.add_argument("-s", "--style", action="store",
                           help="Specify alternate style",
                           default="default")
    argparser.add_argument("-c", "--config", action="store",
                           help="Specify alternate configuration file")

    args = argparser.parse_args()

    # Init notifications if notifying
    if args.notify:
        notify2.init("pympd-status")
        notification = notify2.Notification("Python MPD notifier")

    # Load config
    configfile = args.config
    if configfile == None:
        configfile = "~/.config/pympd-status/config.toml"

    with open(expanduser(configfile)) as config_file:
        config = toml.load(config_file)

    # Connect to mpd
    client = mpd.MPDClient()
    client.timeout = 10
    client.idletimeout = None
    client.connect(config["mpd"]["host"], config["mpd"]["port"])

    # Get current song and state
    current = client.currentsong()
    state = client.status()

    format_str = config["style"][args.style]["format"]

    info = extract_info(current, state)

    mpdinfo = parse_fmt_str(format_str, info)

    # Show it
    if args.notify:
        notification.update("", mpdinfo)
        notification.show()
    else:
        print(mpdinfo)

if __name__ == "__main__":
    main()
