#!/usr/bin/env python3

import string 
from os.path import expanduser

import mpd
import notify2
import toml

# Convert floating point strings to HH:MM:SS time
def format_time(seconds):
    secs = float(seconds)
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

# Generate a ncmpcpp-like state list
def format_state_ncmpcpp(state):
    # Add the state flag symbol or a dash
    def add_or_dash(state, char):
        return char if bool(int(state)) else '- '
    out = '[ '
    out += add_or_dash(state["repeat"], 'r ')
    out += add_or_dash(state["random"], 'z ')
    out += add_or_dash(state["single"], 's ')
    out += add_or_dash(state["consume"], 'c ')
    out += add_or_dash(state["xfade"], 'x ')
    out += ']'
    return out
        
def extract_vars(current_song, state):
    info = {}
    info["artist"] = current_song.get("artist", "")
    info["title"]  = current_song.get("title", "")
    info["filename"] = current_song.get("file", "")
    volume = state.get("volume", "") + "%"
    if volume == "-1%":
        # mpd is stopped
        volume = "N/A"
    info["volume"] = volume
    info["state_ncmpcpp"] = format_state_ncmpcpp(state)
    # these keys don't exist when the player is stopped
    if state['state'] != "stop":
        info["elapsed"] = format_time(state.get("elapsed", ""))
        info["duration"] = format_time(state.get("duration", ""))
    return info

def expand(argument, information):
    return information.get(argument, "")

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
        }
    for char in fmt_str:
        if not escape and char == "\\":
            escape = True
        elif escape and char == "\\":
            escape = False
            out += "\\"
        elif mode == "normal" and char == "$":
            if not escape:
                mode = "read_name"
            else:
                out += "$"
                escape = False
        elif mode == "read_name":
            if char in string.ascii_letters + string.digits + "_":
                # Names are only [a-zA-Z0-9_]
                name += char
            elif char == "{":
                mode = "read_arg"
            else:
                out += expand(name, information) + char
                name = ""
                mode = "normal"
        elif mode == "read_arg":
            if char == "}" and not escape:
                out += functions[name](argument, information)
                mode = "normal"
                name = ""
                argument = ""
            else:
                argument += char
                escape = False
        else:
            out += char
            escape = False
    return out

def main():
    # Init notifications
    notify2.init("pympd-status")
    notification = notify2.Notification("Python MPD notifier")

    # Load config
    with open(expanduser("~/.config/pympd-status/config.toml")) as config_file:
        config = toml.load(config_file)

    # Connect to mpd
    client = mpd.MPDClient()
    client.timeout = 10
    client.idletimeout = None
    client.connect(config["mpd"]["host"], config["mpd"]["port"])

    # Get current song and state
    current = client.currentsong()
    state = client.status()

    format_str = config["format_str"]

    info = extract_vars(current, state)

    mpdinfo = parse_fmt_str(format_str, info)

    # Show it
    notification.update("", mpdinfo)
    notification.show()

if __name__ == "__main__":
    main()
