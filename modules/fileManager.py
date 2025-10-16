import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog, messagebox, simpledialog
import os

class File:
    def __init__(self):
        self.extension = ".project"
        self.project_name_default = "myProject"
        self.project_name = self.project_name_default
        self.project = self.project_name + self.extension
        class Filename:
            def __init__(self):
                self.db = "tasks.db"
                self.track = "tracker.csv"
                self.plan = "planner.csv"
                self.settings = "settings.json"
        self.filename = Filename()

    # Returns the full path to the database file
    def db(self):
        return os.path.join(self.project, self.filename.db)

    # Returns the full path to the tracker file
    def track(self):
        return os.path.join(self.project, self.filename.track)

    # Returns the full path to the planner file
    def plan(self):
        return os.path.join(self.project, self.filename.plan)

    def settings(self):
        return os.path.join(self.project, self.filename.settings)


    def set(self, path):
        if os.path.exists(path) and ".project" in path:
            self.project_name = os.path.basename(path).replace(self.extension, "")
            self.project = path
            return 1
        else:
            return 0

    # Opens a file dialog to select or create a project file
    def get(self, root):
        def returnSuccess():
            root.deiconify()
            return 1
        def returnFail():
            root.deiconify()
            return 0
        # Create new tkinter window to host file dialouge
        root.withdraw()  # Hide the main Tk window
        # Ask the user to select a directory (project files are directories) 
        root.update()
        file_path = filedialog.askdirectory(
            title="Select existing project file or diretory in which to create a new one"
        )
        # If the user selects nothing
        if not file_path:
            return returnFail()
        # If the user selects an existing file
        if os.path.exists(file_path) and ".project" in file_path:
            self.project_name = os.path.basename(file_path).replace(self.extension, "")
            self.project = file_path
            return returnSuccess()
        #If the file does not already exist
        root.update()
        create = messagebox.askyesno (
            "File not found",
            f"Project file does not exist.\nDo you want to create a new one?"
        ) 
        # If the user wants to 1 a new project
        if create:
            try:
                root.update()
                dir_name = simpledialog.askstring(
                    "New Directory",
                    "Enter a name for the new project:"
                )
                file_name = dir_name + self.extension 
                new_file_path = os.path.join(file_path, file_name)
                os.makedirs(new_file_path, exist_ok=False)
                self.project_name = os.path.basename(new_file_path).replace(self.extension, "")
                self.project = new_file_path
                return returnSuccess()
            except:
                print("failed to create new project") #debug
                return returnFail()
        else:
            # Ask for a directory
            dir_path = filedialog.askdirectory(
                title="Select directory to create file"
            )
            if not dir_path:
                return returnFail()
            try:
                new_path = os.path.join(dir_path, self.self.proj_default + self.extension)
                os.makedirs(file_path, exist_ok=False)
                self.project = file_path
                return returnSuccess()
            except:
                return returnFail()
                