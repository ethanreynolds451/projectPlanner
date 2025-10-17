import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog, messagebox, simpledialog
import os
import shutil
import tempfile
import filecmp

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

    def create_new(self, root, file_path, switch_to_file=True):
        try:
            # Ask for project name
            dir_name = simpledialog.askstring(
                "New Project",
                "Enter a name for the new project:",
                parent=root
            )
            if not dir_name:
                print("Project creation cancelled.")
                return 0

            # Create directory with the project "extension"
            project_dir = os.path.join(file_path, dir_name + self.extension)
            os.makedirs(project_dir, exist_ok=False)

            # Switch to the new project if requested
            if switch_to_file:
                self.set(project_dir)

            # Prompt for start and end dates (non-blocking modal)
            date_window = tk.Toplevel(root)
            date_window.title("Project Dates")

            tk.Label(date_window, text="Project Start Date (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=3)
            tk.Label(date_window, text="Project End Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=3)

            start_entry = tk.Entry(date_window)
            end_entry = tk.Entry(date_window)
            start_entry.grid(row=0, column=1, padx=5, pady=3)
            end_entry.grid(row=1, column=1, padx=5, pady=3)

            def save_dates():
                start_date = start_entry.get().strip()
                end_date = end_entry.get().strip()
                # TODO: Save to project settings file or DB here
                print(f"Project created at {project_dir}")
                print(f"Start: {start_date}, End: {end_date}")
                date_window.destroy()

            tk.Button(date_window, text="Save", command=save_dates).grid(row=2, column=0, columnspan=2, pady=8)

            # Make the window modal
            date_window.grab_set()
            date_window.wait_window()

        except FileExistsError:
            messagebox.showerror("Error", "A project with that name already exists.")
            return 0
        except Exception as e:
            print("Failed to create new project:", e)
            messagebox.showerror("Error", f"Failed to create project:\n{e}")
            return 0

        return 1
        

    # Opens a file dialog to select or create a project file
    def get(self, root):
        def returnSuccess():
            root.deiconify()
            return 1
        def returnFail():
            root.deiconify()
            return 0
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
            self.create_new(file_path)
        else:
        #  No idea what this was doing here in the first place  
            # # Ask for a directory
            # dir_path = filedialog.askdirectory(
            #     title="Select directory to create file"
            # )
            # if not dir_path:
            #     return returnFail()
            # try:
            #     new_path = os.path.join(dir_path, self.self.proj_default + self.extension)
            #     os.makedirs(file_path, exist_ok=False)
            #     self.project = file_path
            #     return returnSuccess()
            # except:
                return returnFail()

    def initialize_file(self, parent):
        parent.file = self
        parent.pref.load_settings()
        # No system settings because this not part of the project file
        parent.db.init_db(parent)                  # initialize the database at the file (creates if not exists) 
        # uncomment when csv manager is implemented
        #csv.init_csv()               # initialize the csv(s) at the file (creates if not exists)
    

class fileManagerWindow:
    def __init__(self, parent, root, pref, db, csv, file):
        self.parent = parent
        self.root = root
        self.pref = pref
        self.db = db
        self.csv = csv
        self.file = file
    
    def launch(self): 
        window = tk.Toplevel(self.root)
        window.title("File Manager")
        window.geometry("600x400")

        current_file_label = tk.Label(window, text=f"Current Project File: {self.file.project}")
        current_file_label.pack(pady=10)

        select_file_button = tk.Button(
            window, 
            text="Select Project File", 
            command=lambda: self.select_file(current_file_label)
        )
        select_file_button.pack(pady=10)

        copy_file_button = tk.Button(
            window, 
            text="Copy Project File", 
            command=self.copy_file
        )
        copy_file_button.pack(pady=10)

        move_file_button = tk.Button(
            window, 
            text="Move Project File", 
            command=self.move_file
        )
        move_file_button.pack(pady=10)

        delete_file_button = tk.Button(
            window, 
            text="Delete Project File", 
            command=self.delete_file
        )
        delete_file_button.pack(pady=10)

        create_new_file_button = tk.Button(
            window, 
            text="Create New Project File", 
            command=lambda: self.create_new_file(current_file_label)
        )
        create_new_file_button.pack(pady=10)

    def select_file(self, label):
        if self.file.get(self.root):
            label.config(text=f"Current Project File: {self.file.project}")
            self.pref.update_system_setting("saved_file_path", self.file.project)
            self.root.title(self.file.project_name)                  # Update main window title
            self.file.initialize_file(self.pref, self.db, self.csv)  # Initialize the newly selected file
            messagebox.showinfo("File Selected", f"Project file set to: {self.file.project}")
            self.parent.load_apps()
            # Ask user if they want to set this file as default
            set_default = messagebox.askyesno(
                "Set as Default", 
                "Do you want to set this project file as the default on startup?"
            )
            if set_default:
                self.pref.update_system_setting("saved_file_path", self.file.project)
                messagebox.showinfo("Default Set", f"Project file {self.file.project} set as default on startup.")

        else:
            messagebox.showwarning("File Selection Cancelled", "No project file selected.")

    def copy_file(self):
        # Prompt user for new file location
        file_path = filedialog.askdirectory(
            title="Select the location to copy the project file"
        )
        if not file_path:
            return
        # Ask user for name of file copy
        dir_name = simpledialog.askstring(
            "Copy Project File",
            "Enter a name for the copied project:"
        )
        if not dir_name:
            return
        # Make a directory with that name
        new_file_name = dir_name + self.file.extension
        new_file_path = os.path.join(file_path, new_file_name)
        os.makedirs(new_file_path, exist_ok=False)
        # Copy contents of file from current location to new location
        try:
            import shutil
            shutil.copytree(self.file.project, new_file_path, dirs_exist_ok=True)
            messagebox.showinfo("File Copied", f"Project file copied to: {new_file_path}")
        except Exception as e:
            messagebox.showerror("Copy Failed", f"Failed to copy project file: {e}")
            return
        # Ask user if they would like to switch to the copied file
        switch = messagebox.askyesno(
            "Switch File", 
            "Do you want to switch to the copied project file?"
        )
        if switch: 
            if self.file.set(new_file_path):
                self.pref.update_system_setting("saved_file_path", self.file.project)
                self.root.title(self.file.project_name)                  # Update main window title
                self.file.initialize_file(self.pref, self.db, self.csv)
                messagebox.showinfo("File Selected", f"Project file set to: {self.file.project}")
                self.parent.load_apps()
            else:
                messagebox.showerror("Switch Failed", "Failed to set project file to copied location.")

    def move_file(self):
        dest_dir = filedialog.askdirectory(title="Select location to move project file")
        if not dest_dir:
            return

        new_file_path = os.path.join(dest_dir, self.file.project_name + self.file.extension)
        if os.path.exists(new_file_path):
            messagebox.showerror("Move Failed", "Destination folder already exists.")
            return

        # Step 1: Backup original
        backup_path = tempfile.mkdtemp(prefix="project_backup_")
        shutil.copytree(self.file.project, backup_path, dirs_exist_ok=True)

        try:
            # Step 2: Copy to new location
            shutil.copytree(self.file.project, new_file_path)

            # Step 3: Verify copy
            dc = filecmp.dircmp(self.file.project, new_file_path)
            if dc.diff_files or dc.left_only or dc.right_only:
                messagebox.showerror("Move Failed", "Some files failed to copy. Original not deleted.")
                return

            # Step 4: Ask user to delete original
            if messagebox.askyesno("Confirm Delete", f"Delete original project folder?\n{self.file.project}"):
                shutil.rmtree(self.file.project)
            else:
                messagebox.showinfo("Move Cancelled", "Original files not deleted.")

        except Exception as e:
            messagebox.showerror("Move Failed", f"Error during move: {e}")
            return

        # Step 5: Set new project file and update UI
        if self.file.set(new_file_path):
            self.pref.update_system_setting("saved_file_path", self.file.project)
            self.root.title(self.file.project_name)
            self.file.initialize_file(self.pref, self.db, self.csv)
            messagebox.showinfo("File Selected", f"Project file set to: {self.file.project}")
            self.parent.load_apps()
        else:
            messagebox.showerror("Move Failed", "Failed to set project file to new location.")

    def delete_file(self):
        # Prompt for confirmation before deletion
        answer = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this project?")
        if answer:
            shutil.rmtree(self.file.project)
            messagebox.showinfo("Deleted", "Project deleted.")
            self.file.get(self.root)  # Prompt user to select or create a new project file
            self.parent.load_apps()

    def create_new_file(self, label):
        file_path = filedialog.askdirectory(title="Select directory to create new project file")
        if self.file.create_new(self.root, file_path, switch_to_file=False):
            switch = messagebox.askyesno("Switch to New File", "Would you like to switch to the new project file?")
            if switch: 
                self.file.set(file_path)
                tk.messagebox.showinfo("File Created", f"New project file created at: {self.file.project} but has not been activated; restart program to use it (will fix this later).")
                # NEED TO INITIALIZE FILE HERE
        else: 
            messagebox.showinfo("Failed to create file", "There was an error creating the new file")