import tkinter as tk
import sys
import os

# Import app modules
from modules.fileManager import File
from modules.settingsManager import Settings
from modules.dbManager import Database
from modules.csvManager import Csv
from apps.homepage import HomePage

class mainApp:
    def __init__(self):
        # Initialize modules
        self.file = File()
        self.pref = Settings(self)
        self.db = Database(self)
        self.csv = Csv(self) 
        self.root = tk.Tk()               
        self.app = HomePage(self)

    # The main application code
    def runApp(self):
        if sys.platform == "darwin" and sys.stdout.isatty():
            self.root.lift()                     # bring window to front
            self.root.attributes('-topmost', True)
            self.root.after(200, lambda: self.root.attributes('-topmost', False))
            self.root.focus_force()
        self.pref.init_system_settings()     # initialize system settings (creates if not exists)
        if not self.pref.get_system_setting("preserve_file"):
            # Create new tkinter window to host file dialouge
            self.root.withdraw()  # Hide the main Tk window
            self.file.get(self.root)                  # have user select project file or create new one
        else :
            if not os.path.isdir(self.pref.get_system_setting("saved_file_path")) or not os.path.exists(self.pref.get_system_setting("saved_file_path")):
                
                tk.messagebox.showwarning("File Not Found", "The previously saved file path is invalid. Please select a new file.")
                self.file.get(self.root)
            try:
                self.file.set(self.pref.get_system_setting("saved_file_path"))
            except:
                print("No saved file path found, opening file dialog.")
                self.file.get(self.root)
        print("Initializing project file")
        self.file.initialize_file(self)             # initialize the project file components (creates if not exists)
        self.app.initialize_homepage()
        self.root.mainloop()

