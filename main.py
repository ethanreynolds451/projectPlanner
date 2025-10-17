import tkinter as tk
import sys
import os

from modules.fileManager import File
file = File()

from modules.settingsManager import Settings
pref = Settings(file)

from modules.dbManager import Database
db = Database(pref, file)

csv = None  # placeholder for future csv manager

from apps.homepage import MainApp

# The main application code
def runApp():
    root = tk.Tk()                  # create the main window
    if sys.platform == "darwin" and sys.stdout.isatty():
        root.lift()                     # bring window to front
        root.attributes('-topmost', True)
        root.after(200, lambda: root.attributes('-topmost', False))
        root.focus_force()
    pref.init_system_settings()     # initialize system settings (creates if not exists)
    if not pref.get_system_setting("preserve_file"):
        # Create new tkinter window to host file dialouge
        root.withdraw()  # Hide the main Tk window
        file.get(root)                  # have user select project file or create new one
    else :
        if not os.path.isdir(pref.get_system_setting("saved_file_path")) or not os.path.exists(pref.get_system_setting("saved_file_path")):
            root.withdraw()
            tk.messagebox.showwarning("File Not Found", "The previously saved file path is invalid. Please select a new file.")
            file.get(root)
        try:
            file.set(pref.get_system_setting("saved_file_path"))
        except:
            print("No saved file path found, opening file dialog.")
            file.get(root)
    file.initialize_file(pref, db, csv)             # initialize the project file components (creates if not exists)
    app = MainApp(root, pref, file, db, csv) # launch the main application
    root.mainloop()