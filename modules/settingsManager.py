import json
import tkinter as tk
from tkinter import filedialog

import sys
from pathlib import Path
import os

from platformdirs import user_config_dir
        
from resources.globalPresets import APP_NAME, APP_AUTHOR
from resources.globalPresets import defaultSettings

class Settings:
    def __init__(self, file):
        self.file = file
        self.system_file = self.get_system_settings_path()
        self.settings = {}
        self.system_settings = {}
        
    def get_system_settings_path(self):
        config_dir = Path(user_config_dir(APP_NAME, APP_AUTHOR))
        config_dir.mkdir(parents=True, exist_ok=True)
        return os.path.join(config_dir, "system_settings.json")

    def init_settings(self):
        self.init_project_settings()

    def init_project_settings(self):
        try:
            with open(self.file.settings(), 'r') as f:
                self.settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.settings = defaultSettings.defaults
            self.save_settings()

    def init_system_settings(self):
        try:
            with open(self.system_file, 'r') as f:
                self.system_settings = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.system_settings = defaultSettings.system_defaults
            self.save_system_settings()

    def load_settings(self):
        self.init_settings()
        self.init_system_settings()

    def save_settings(self):
        with open(self.file.settings(), 'w') as f:
            json.dump(self.settings, f, indent=4)
    
    def save_system_settings(self):
        with open(self.system_file, 'w') as f:
            json.dump(self.system_settings, f, indent=4)
            
    def get_setting(self, key):
        return self.settings.get(key, None)
    
    def get_system_setting(self, key):
        return self.system_settings.get(key, None)

    def update_setting(self, key, value):
        self.settings[key] = value
        self.save_settings()  # was incorrectly saving system settings

    def update_system_setting(self, key, value):
        self.system_settings[key] = value
        self.save_system_settings()


class settingsManagerWindow:
    def __init__(self, root, pref, file):
        self.root = root
        self.pref = pref
        self.file = file

    def launch(self): 
        window = tk.Toplevel(self.root)
        window.title("Settings Manager")
        window.geometry("600x400")

        preserve_file_var = tk.BooleanVar(value=self.pref.get_system_setting("preserve_file"))
        preserve_file = tk.Checkbutton(
            window, 
            text="Use same file on startup", 
            variable=preserve_file_var,
            command=lambda: self.pref.update_system_setting(
                "preserve_file", preserve_file_var.get()
            )
        )

        saved_file_var = tk.StringVar(value=self.pref.get_system_setting("saved_file_path"))
        saved_file_label = tk.Label(window, text="Default project file path:")
        saved_file_entry = tk.Entry(window, textvariable=saved_file_var, width=40)
        saved_file_entry.bind(
            "<FocusOut>", 
            lambda e: self.pref.update_system_setting("saved_file_path", saved_file_var.get())
        )

        saved_file_selector = tk.Button(
            window, 
            text="Browse", 
            command=lambda: self.browse_file(saved_file_var)
        )

        set_current_file = tk.Button(
            window,
            text="Set to This Project",
            command=lambda: self.set_file(self.file.project, saved_file_var)
        )

        preserve_file.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        saved_file_label.grid(row=1, column=0, sticky="w", padx=10, pady=10)
        saved_file_entry.grid(row=1, column=1, columnspan=2, sticky="w", padx=10, pady=10)
        saved_file_selector.grid(row=2, column=1, sticky="w", padx=10, pady=10)
        set_current_file.grid(row=2, column=2, sticky="w", padx=10, pady=10)

    def set_file(self, file_path, var):
        """Set the selected file path to the entry and update settings."""
        var.set(file_path)
        self.pref.update_system_setting("saved_file_path", file_path)

    def browse_file(self, var):
        file_path = filedialog.askdirectory(
            title="Select project file"
        )
        if file_path:
            self.set_file(file_path, var)