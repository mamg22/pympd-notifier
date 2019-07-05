#!/usr/bin/env python3

import math

import mpd
import notify2

# Convert floating point strings to HH:MM:SS time
def format_secs(seconds):
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

# Generate a ncmpcpp like state list
def format_state(state):
    # Add the state flag symbol else a dash
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
        progress = "<b>" + format_secs(state['elapsed']) + "/" + format_secs(state['duration']) + "</b>\n"

    volume = state['volume'] + "%" if state['volume'] != "-1" else "N/A"
    
    # Build the output
    mpdinfo = f"<b>{current['title']}</b>\n" \
              f"<i>{current['artist']}</i>\n" \
              f"{progress}" \
              f"Vol: {volume}\n" \
              f"{format_state(state)}"

    # Show it
    notification.update("", mpdinfo)
    notification.show()

if __name__ == "__main__":
    main()
