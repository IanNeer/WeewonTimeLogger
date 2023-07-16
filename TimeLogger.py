# -*- coding: utf-8 -*-
"""
Created on Sun Jul 16 11:33:58 2023

@author: ianne
"""

import os
import json
import ctypes
import time
from datetime import datetime
from win32gui import GetWindowText, GetForegroundWindow
from win32process import GetWindowThreadProcessId
from psutil import Process, pid_exists
import tkinter as tk
import threading

# Structure for last input info
class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [
        ('cbSize', ctypes.c_uint),
        ('dwTime', ctypes.c_uint),
    ]

def get_last_input():
    """
    Get the UNIX timestamp of the last input event in milliseconds.
    """
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))

    # Get system uptime in milliseconds
    system_uptime_ms = ctypes.windll.kernel32.GetTickCount()

    # Get current time in UNIX timestamp format (milliseconds)
    current_time_ms = round(time.time() * 1000)

    # Calculate the system start time
    system_start_time_ms = current_time_ms - system_uptime_ms

    # Calculate the UNIX timestamp of the last input event
    last_input_time_ms = system_start_time_ms + lii.dwTime

    return last_input_time_ms

def get_app_path(hwnd):
    """Get application path given hwnd."""
    try:
        pid = GetWindowThreadProcessId(hwnd)[1]
        if pid_exists(pid):
            return Process(pid).exe()
    except Exception as e:
        print(e)
        return None

def get_app_name(hwnd):
    """Get application name given hwnd."""
    path = get_app_path(hwnd)
    return os.path.basename(path) if path else None

def getFocus():
    """Get currently focused application and its window title."""
    hwnd = GetForegroundWindow()
    app_name = get_app_name(hwnd)
    window_title = GetWindowText(hwnd)
    timestamp = round(time.time()*1000)
    return app_name, window_title, timestamp

def main():
    directory = os.path.join(os.path.expanduser('~'), 'Documents', "Weewon's Time Logs")
    os.makedirs(directory, exist_ok=True)
    output_path = os.path.join(directory, "Logs.json")
    output_data = []

    if os.path.exists(output_path):
        with open(output_path, 'r') as f:
            output_data = json.load(f)

    previousapp = ''
    previoustitle = ''
    last_dump_time = time.time()
    
    user_is_afk = False

    while run_flag.is_set():
        app, title, timestamp = getFocus()
        current_time = round(time.time() * 1000)
        last_input = get_last_input()
    
        if (current_time - last_input > .1 * 60 * 1000):
            if not user_is_afk and output_data and output_data[-1]['app'] == previousapp:
                user_is_afk = True
                output_data[-1]['stop'] = last_input
                output_data[-1]['duration'] = output_data[-1]['stop'] - output_data[-1]['start']
                output_data[-1]['time_in_seconds'] = output_data[-1]['duration'] / 1000
                output_data[-1]['datetime'] = datetime.utcfromtimestamp(output_data[-1]['stop'] / 1000).strftime('%Y/%m/%d %H:%M:%S')
                text.insert(tk.END, f"App: {output_data[-1]['app']}\nStart: {output_data[-1]['start']}\nStop: {output_data[-1]['stop']}\nTitle: {output_data[-1]['title']}\nDuration (ms): {output_data[-1]['duration']}\nDuration (s): {output_data[-1]['time_in_seconds']}\nDatetime: {output_data[-1]['datetime']}\n\n")
                text.see(tk.END)
        else:
            if previousapp != app or previoustitle != title:
                if previousapp and output_data and output_data[-1]['app'] == previousapp:
                    if user_is_afk:
                        output_data[-1]['stop'] = output_data[-1]['stop']
                    else:
                        output_data[-1]['stop'] = timestamp
                    output_data[-1]['duration'] = output_data[-1]['stop'] - output_data[-1]['start']
                    output_data[-1]['time_in_seconds'] = output_data[-1]['duration'] / 1000
                    output_data[-1]['datetime'] = datetime.utcfromtimestamp(output_data[-1]['stop'] / 1000).strftime('%Y/%m/%d %H:%M:%S')
                    text.insert(tk.END, f"App: {output_data[-1]['app']}\nStart: {output_data[-1]['start']}\nStop: {output_data[-1]['stop']}\nTitle: {output_data[-1]['title']}\nDuration (ms): {output_data[-1]['duration']}\nDuration (s): {output_data[-1]['time_in_seconds']}\nDatetime: {output_data[-1]['datetime']}\n\n")
                    text.see(tk.END)
                output_data.append({'app': app, 'start': timestamp, 'title': title, 'stop': None, 'duration': None, 'time_in_seconds': None, 'datetime': None})
                previousapp = app
                previoustitle = title
                user_is_afk = False

        if time.time() - last_dump_time >= 5*60:
            with open(output_path, 'w') as f:
                json.dump(output_data, f, indent=4)
            last_dump_time = time.time()

        time.sleep(0.1)

    if output_data and output_data[-1]['app'] == previousapp:
        output_data[-1]['stop'] = timestamp
        output_data[-1]['duration'] = output_data[-1]['stop'] - output_data[-1]['start']
        output_data[-1]['time_in_seconds'] = output_data[-1]['duration'] / 1000
        output_data[-1]['datetime'] = datetime.fromtimestamp(output_data[-1]['start']/1000).strftime('%Y/%m/%d %H:%M:%S')

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=4)

def on_closing():
    run_flag.clear()
    time.sleep(1)
    root.destroy()

run_flag = threading.Event()
run_flag.set()
root = tk.Tk()
root.title('TimeLogger')
root.geometry("400x600")
root.config(bg="black")
text = tk.Text(root, bg='black', fg='gray')
text.pack(expand=True, fill=tk.BOTH)
root.protocol("WM_DELETE_WINDOW", on_closing)
threading.Thread(target=main).start()
root.mainloop()