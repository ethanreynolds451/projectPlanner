# A starter code from ChatGPT to use as framework for future development

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog, messagebox
import os


class File:
    def __init__(self):
        self.extension = ".project"
        self.proj_default = "myProject"
        self.project = self.proj_default + self.extension
        class Filename:
            def __init__(self):
                self.db = "tasks.db"
                self.track = "tracker.csv"
                self.plan = "planner.csv"
        self.filename = Filename()
    def db(self):
        return self.project + "/" + self.filename.db
    def track(self):
        return self.project + "/" + self.filename.track
    def plan(self):
        return self.project + "/" + self.filename.plan   
    def get(self):
        # Create new tkinter window to host file dialouge
        root = tk.Tk()
        root.withdraw()  # Hide the main Tk window
        # Ask the user to select a directory (project files are directories) 
        file_path = filedialog.askdirectory(
            title="Select existing project file or diretory in which to create a new one"
        )
        # If the user selects nothing
        if not file_path:
            root.destroy()
            return 0
        # If the user selects an existing file
        if os.path.exists(file_path) and ".project" in file_path:
            self.project = file_path
            root.destroy()
            return 1
        #If the file does not already exist
        create = messagebox.askyesno(
            "File not found",
            f"Project file does not exist.\nDo you want to create a new one?"
        )
        # If the user wants to 1 a new project
        if create:
            # Create empty file
            try:
                dir_name = simpledialog.askstring(
                    "New Directory",
                    "Enter a name for the new project:"
                )
                file_name = dir_name + self.extension 
                file_path = os.path.join(file_name, dir_name)
                os.makedirs(file_path, exist_ok=False)
                self.project = file_path
                root.destroy()
                return 1
            except:
                root.destroy()
                return 0
        else:
            # Ask for a directory
            dir_path = filedialog.askdirectory(
                title="Select directory to create file"
            )
            if not dir_path:
                root.destroy()
                return 0
            try:
                new_path = os.path.join(dir_path, self.self.proj_default + self.extension)
                os.makedirs(file_path, exist_ok=False)
                self.project = file_path
                root.destroy()
                return 1
            except:
                root.destroy()
                return 0

file = File()

# -----------------------------
# Database helper functions
# -----------------------------
def init_db():
    conn = sqlite3.connect(file.db())
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            class TEXT DEFAULT NULL,
            start_date TEXT,
            end_date TEXT,
            due_date TEXT,
            percent_complete INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active'
        )
    """)
    conn.commit()
    conn.close()

def fetch_tasks():
    conn = sqlite3.connect(file.db())
    cur = conn.cursor()
    cur.execute("SELECT id, name, start_date, due_date, percent_complete, status FROM tasks")
    rows = cur.fetchall()
    conn.close()
    return rows

def add_task(name, start_date, due_date):
    conn = sqlite3.connect(file.db())
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (name, start_date, due_date) VALUES (?, ?, ?)",
                (name, start_date, due_date))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = sqlite3.connect(file.db())
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

# -----------------------------
# Tkinter GUI
# -----------------------------
class TaskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager (Skeleton)")

        # Task list
        self.tree = ttk.Treeview(root, columns=("ID", "Name", "Start", "Due", "Complete", "Status"), show="headings")
        for col in ("ID", "Name", "Start", "Due", "Complete", "Status"):
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True)

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text="Add Task", command=self.add_task_popup).pack(side="left")
        tk.Button(btn_frame, text="Delete Task", command=self.delete_selected).pack(side="left")
        tk.Button(btn_frame, text="Refresh", command=self.refresh).pack(side="left")

        self.refresh()

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for row in fetch_tasks():
            self.tree.insert("", "end", values=row)

    def add_task_popup(self):
        win = tk.Toplevel(self.root)
        win.title("Add Task")

        tk.Label(win, text="Name:").grid(row=0, column=0)
        tk.Label(win, text="Start Date (YYYY-MM-DD):").grid(row=1, column=0)
        tk.Label(win, text="Due Date (YYYY-MM-DD):").grid(row=2, column=0)

        name_entry = tk.Entry(win)
        start_entry = tk.Entry(win)
        due_entry = tk.Entry(win)

        name_entry.grid(row=0, column=1)
        start_entry.grid(row=1, column=1)
        due_entry.grid(row=2, column=1)

        def save_task():
            name = name_entry.get().strip()
            start = start_entry.get().strip()
            due = due_entry.get().strip()
            if not name:
                messagebox.showwarning("Error", "Task must have a name")
                return
            add_task(name, start, due)
            self.refresh()
            win.destroy()

        tk.Button(win, text="Save", command=save_task).grid(row=3, column=0, columnspan=2)

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Error", "No task selected")
            return
        task_id = self.tree.item(selected[0])["values"][0]
        delete_task(task_id)
        self.refresh()

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    file.get()
    init_db()
    root = tk.Tk()
    app = TaskApp(root)
    root.mainloop()