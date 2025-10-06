import tkinter as tk
from tkinter import ttk, messagebox

class taskManagerApp:
    def __init__(self, root, file, db):
        self.root = root

        self.file = file
        self.db = db

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
        for row in self.db.fetch_tasks():
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
            self.db.add_task(name, start, due)
            self.refresh()
            win.destroy()

        tk.Button(win, text="Save", command=save_task).grid(row=3, column=0, columnspan=2)

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Error", "No task selected")
            return
        task_id = self.tree.item(selected[0])["values"][0]
        self.db.delete_task(task_id)
        self.refresh()
