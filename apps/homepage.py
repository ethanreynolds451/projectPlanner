import tkinter as tk
from tkinter import ttk, messagebox

from apps.taskManager import taskManagerApp as tm

class MainApp:
    def __init__(self, root, file, db):
        self.root = root
        self.root.title(file.project_name)
        self.root.geometry("1400x800")

        self.file = file
        self.db = db
        self.tracker = None  # Placeholder for tracker functionality
        self.planner = None  # Placeholder for planner functionality

        # Layer apps as sub-frames 

        self.header = tk.Frame(root)
        self.left = tk.Frame(root)
        self.right = tk.Frame(root)

        self.header.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.left.grid(row=1, column=0, sticky="nsew")
        self.right.grid(row=1, column=1, sticky="nsew")
        
        self.taskViewer = tk.Frame(self.left)
        self.placeHolder = tk.Frame(self.left)

        self.taskViewer.grid(row=0, column=0, sticky="nsew")
        self.placeHolder.grid(row=1, column=0, sticky="nsew")

        tm(self.taskViewer, self.file, self.db)
        tm(self.placeHolder, self.file, self.db)
