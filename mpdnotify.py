#!/usr/bin/env python3

import string 

import mpd
import notify2

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
        
def extract_info(current_song, state):
    def get_info(source, name):
        try: 
            return source["name"]
        except:
            return ""

    info = {}
    info["artist"] = get_info(current_song, "artist")
    info["title"]  = get_info(current_song, "title")
    info["filename"] = get_info(current_song, "file")
    volume = get_info(state, "volume") + "%"
    if volume == "-1%":
        # mpd is stopped
        volume = "N/A"
    info["volume"] = volume
    info["state_ncmpcpp"] = format_state_ncmpcpp(state)
    # these keys don't exist when the player is stopped
    if state['state'] != "stop":
        info["elapsed"] = format_time(get_info(state, "elapsed"))
        info["duration"] = format_time(get_info(state, "duration"))
    return info
    
def parse_fmt_str(fmt_str, information):
    out = ""
    mode = "normal"
    expand_str = ""
    for char in fmt_str:
        if mode == "normal" and char == "$":
            mode = "expand"
        # Variables are only [a-zA-Z0-9_]
        elif mode == "expand" and char in string.ascii_letters + string.digits + "_":
            expand_str += char
        elif mode == "expand" and expand_str == "" and char == "$":
            out += "$"
            mode = "normal"
        elif mode == "expand":
            try:
                out += information[expand_str]
                out += char
            except:
                pass
            expand_str = ""
            mode = "normal"
        else:
            out += char
    return out

def main():
    # Init notifications
    notify2.init("pympd-notify")
    notification = notify2.Notification("Python MPD notifier")

    # Connect to mpd
    client = mpd.MPDClient()
    client.timeout = 10
    client.idletimeout = None
    client.connect("localhost", 6600)

    # Get current song and state
    current = client.currentsong()
    state = client.status()

    progress = ""
    if state['state'] != "stop":
        progress = "<b>" + format_time(state['elapsed']) + "/" + format_time(state['duration']) + "</b>\n"

    volume = state['volume'] + "%" if state['volume'] != "-1" else "N/A"

    # Build the output
#    mpdinfo = f"<b>{current['title']}</b>\n" \
#              f"<i>{current['artist']}</i>\n" \
#              f"{progress}" \
#              f"Vol: {volume}\n" \
#              f"{format_state_ncmpcpp(state)}"

    format_str = "<b>$title</b>\n" \
                 "<i>$artist</i>\n" \
                 "$elapsed/$duration\n" \
                 "Vol: $volume\n" \
                 "$state_ncmpcpp"

    info = extract_info(current, state)

    mpdinfo = parse_fmt_str(format_str, info)

    # Show it
    notification.update("", mpdinfo)
    notification.show()

if __name__ == "__main__":
    main()
