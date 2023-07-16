# WeewonTimeLogger
This is just a quick application that tracks the main window title and app in use, and logs start/title/stop stamps when you switch windows.

TimeLogger.py
This is the source code for the logger, if you want to edit this and recompile to an application open command line, change to the directory containing the file using "cd directory_in_question", and type "pyinstall --onefile -w TimeLogger.py".  The -w flag just suppresses the debugging window that would otherwise open with the application.

TimeLogger.exe
This is the executable version with the python interpreter attached.  Press windows+r and type shell:startup.  Place a shortcut to the location of TimeLogger.exe in the startup folder and it'll run on startup.  If you want to close the app, just press exit on the print window.

Logs
Logs are stored in your computers documents folder under "Weewon's Time Logs" as a JSON.  This JSON might get large and increase the computation time after a month or so, maybe delete it now and then.
