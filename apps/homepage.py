import tkinter as tk
from tkinter import ttk, messagebox

from apps.taskmanager import taskManagerApp as tm

from modules.settingsManager import settingsManagerApp

class MainApp:
    def __init__(self, root, pref, file, db, csv):
        self.root = root
        self.root.title(file.project_name)
        self.root.geometry("1400x800")

        self.pref = pref
        self.file = file
        self.db = db
        self.csv = csv

        self.pref.load_settings()

        # Layer apps as sub-frames 

        # --- Main layout frames ---
        self.header = tk.Frame(root, bg="lightgray", height=40)
        self.left = tk.Frame(root, bg="white")
        self.right = tk.Frame(root, bg="white")

        # Place frames in grid
        self.header.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.left.grid(row=1, column=0, sticky="nsew")
        self.right.grid(row=1, column=1, sticky="nsew")

        # --- Configure grid weights so resizing works ---
        root.grid_rowconfigure(0, weight=0)  # header row doesn’t stretch vertically
        root.grid_rowconfigure(1, weight=1)  # main content area fills space
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)

        # --- Add widgets to header ---
        self.fileOpenerLauncher = tk.Button(self.header, text="File", command=self.launch_file_opener)
        self.settingsLauncher = tk.Button(self.header, text="Settings", command=self.launch_settings_manager)
        self.fileSaverLauncher = tk.Button(self.header, text="Save", command=self.launch_file_saver)
        self.spacer0 = tk.Frame(self.header, width=20, bg="lightgray")
        self.taskLauncher = tk.Button(self.header, text="Tasks", command=self.launch_task_manager)
        self.ganttLauncher = tk.Button(self.header, text="Gantt", command=self.launch_gantt_viewer)
        self.plannerLauncher = tk.Button(self.header, text="Plan", command=self.launch_planner)
        self.trackerLauncher = tk.Button(self.header, text="Track", command=self.launch_tracker)
        self.schedulerLauncher = tk.Button(self.header, text="Schedule", command=self.launch_scheduler)
        self.reportLauncher = tk.Button(self.header, text="Reports", command=self.launch_report) 
        self.spacer1 = tk.Frame(self.header, width=20, bg="lightgray")
        self.dayForward = tk.Button(self.header, text=">", command=lambda: None)  # Placeholder
        self.dayToday = tk.Button(self.header, text="Today", command=lambda: None)  # Placeholder
        self.dayBackward = tk.Button(self.header, text="<", command=lambda: None)  # Placeholder
        self.spacer2 = tk.Frame(self.header, width=20, bg="lightgray")
        self.forward = tk.Button(self.header, text=">>", command=lambda: None)  # Placeholder
        self.back = tk.Button(self.header, text="<<", command=lambda: None)  # Placeholder
        self.reload = tk.Button(self.header, text="Reload", command=lambda: None)  # Placeholder


        self.fileOpenerLauncher.grid(row=0, column=0, columnspan=1, sticky="nsew")
        self.settingsLauncher.grid(row=0, column=1, columnspan=1, sticky="nsew")
        self.fileSaverLauncher.grid(row=0, column=2, columnspan=1, sticky="nsew")

        self.spacer0.grid(row=0, column=3, columnspan=1, sticky="nsew")

        self.taskLauncher.grid(row=0, column=4, columnspan=2, sticky="nsew")
        self.ganttLauncher.grid(row=0, column=6, columnspan=2, sticky="nsew")
        self.plannerLauncher.grid(row=0, column=8, columnspan=2, sticky="nsew")
        self.trackerLauncher.grid(row=0, column=10, columnspan=2, sticky="nsew")
        self.schedulerLauncher.grid(row=0, column=12, columnspan=2, sticky="nsew")
        self.reportLauncher.grid(row=0, column=14, columnspan=2, sticky="nsew")

        self.spacer1.grid(row=0, column=16, columnspan=1, sticky="nsew")

        self.dayBackward.grid(row=0, column=17, columnspan=1, sticky="nsew")
        self.dayToday.grid(row=0, column=18, columnspan=2, sticky="nsew")
        self.dayForward.grid(row=0, column=20, columnspan=1, sticky="nsew")

        self.spacer2.grid(row=0, column=21, columnspan=1, sticky="nsew")

        self.back.grid(row=0, column=22, columnspan=1, sticky="nsew")
        self.forward.grid(row=0, column=23, columnspan=1, sticky="nsew")
        self.reload.grid(row=0, column=24, columnspan=1, sticky="nsew")

        # --- Add widgets to left frame ---
        self.taskViewer = tk.Frame(self.left)
        self.ganttViewer = tk.Frame(self.left)

        self.taskViewer.grid(row=0, column=0, sticky="nsew")
        self.ganttViewer.grid(row=1, column=0, sticky="nsew")
    
        # Allow widgets to fill their parents
        self.left.grid_rowconfigure(0, weight=1)
        self.left.grid_columnconfigure(0, weight=1)

        # Add apps to frames
        tm(self.taskViewer, self.pref, self.file, self.db)
       

        # --- Add widgets to right frame ---

        self.dateHeader = tk.Frame(self.right)
        self.scheduler = tk.Frame(self.right)
        self.tracker = tk.Frame(self.right)

        self.dateHeader.grid(row=0, column=0, sticky="nsew")
        self.scheduler.grid(row=1, column=0, sticky="nsew")
        self.tracker.grid(row=2, column=0, sticky="nsew")

        self.right.grid_rowconfigure(0, weight=1)
        self.right.grid_columnconfigure(0, weight=1)
    

    def launch_file_opener(self):
        # placeholder for actual code to launch file opener
        messagebox.showinfo("File Opener", "File Opener Launched!")
    
    def launch_settings_manager(self):
        settingsManagerApp(self.root, self.pref, self.file).launch()
        
    def launch_file_saver(self):
        # placeholder for actual code to launch file saver
        messagebox.showinfo("File Saver", "File Saver Launched!")

    def launch_task_manager(self):
        # placeholder for actual code to launch task manager
        messagebox.showinfo("Task Manager", "Task Manager Launched!")

    def launch_gantt_viewer(self):
        # placeholder for actual code to launch gantt viewer
        messagebox.showinfo("Gantt Viewer", "Gantt Viewer Launched!")
    
    def launch_planner(self):
        # placeholder for actual code to launch planner
        messagebox.showinfo("Planner", "Planner Launched!")

    def launch_tracker(self):
        # placeholder for actual code to launch tracker
        messagebox.showinfo("Tracker", "Tracker Launched!")
    
    def launch_scheduler(self):
        # placeholder for actual code to launch scheduler
        messagebox.showinfo("Scheduler", "Scheduler Launched!")

    def launch_report(self):
        # placeholder for actual code to launch report viewer
        messagebox.showinfo("Reports", "Reports Launched!")
    
