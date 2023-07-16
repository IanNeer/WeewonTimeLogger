# -*- coding: utf-8 -*-
"""
Created on Sat Jul 15 22:32:14 2023

@author: ianne
"""

import os
import json
from win32gui import GetWindowText, GetForegroundWindow
from win32process import GetWindowThreadProcessId
import time
from psutil import Process, pid_exists
import tkinter as tk
import threading

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
    output_data = {}

    if os.path.exists(output_path):
        with open(output_path, 'r') as f:
            output_data = json.load(f)

    previousapp = ''
    previoustitle = ''
    last_dump_time = time.time()

    while run_flag.is_set():
        app, title, timestamp = getFocus()
        if previousapp != app or previoustitle != title:
            if previousapp and output_data.get(previousapp, {}):
                output_data[previousapp][-1]['stop'] = timestamp
                output_data[previousapp][-1]['duration'] = output_data[previousapp][-1]['stop'] - output_data[previousapp][-1]['start']
                text.insert(tk.END, f"App: {previousapp}\nStart: {output_data[previousapp][-1]['start']}\nStop: {output_data[previousapp][-1]['stop']}\nTitle: {output_data[previousapp][-1]['title']}\n\n")
                text.see(tk.END)
            if app not in output_data:
                output_data[app] = []
            output_data[app].append({'start': timestamp, 'title': title, 'stop': None})
            previousapp = app
            previoustitle = title

        if time.time() - last_dump_time >= 10*60:
            with open(output_path, 'w') as f:
                json.dump(output_data, f, indent=4)
            last_dump_time = time.time()

        time.sleep(0.1)

    if output_data.get(previousapp, {}):
        output_data[previousapp][-1]['stop'] = timestamp
        output_data[previousapp][-1]['duration'] = output_data[previousapp][-1]['stop'] - output_data[previousapp][-1]['start']

    with open(output_path, 'w') as f:
        json.dump(output_data, f, indent=4)

def on_closing():
    run_flag.clear()
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
