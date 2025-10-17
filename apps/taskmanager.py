import tkinter as tk
from tkinter import ttk, PhotoImage
from PIL import Image, ImageTk  # Requires Pillow
from tkinter import messagebox


from resources.globalPresets import taskParameters as taskParams

class taskManagerApp:
    def __init__(self, tk_parent, parent):
        self.root = tk_parent
        self.pref = parent.pref
        self.file = parent.file
        self.db = parent.db

        self.checkbox_states = {}  # item_id -> bool

        # Task list with scrollbar
        self.scrollTable = tk.Frame(self.root)
        self.scrollTable.grid(row=0, column=0, sticky="nsew")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        
        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.grid(row=1, column=0, sticky="nsew")

        tk.Button(btn_frame, text="Add Task", command=self.add_task_popup).pack(side="left")
        tk.Button(btn_frame, text="Delete Task", command=self.delete_selected).pack(side="left")
        tk.Button(btn_frame, text="Undo", command=self.undo_archive_task).pack(side="left")
        tk.Button(btn_frame, text="Redo", command=self.redo_archive_task).pack(side="left")
        tk.Button(btn_frame, text="Refresh", command=self.refresh).pack(side="left")

    def build_table(self):
        checkbox_size = 15

        # Load checkbox images
        checked = Image.open("resources/images/checkbox_checked_green.png")
        unchecked = Image.open("resources/images/checkbox_unchecked.png")

        # Resize to fit row height (keeping aspect ratio)
        checked = checked.resize((checkbox_size, checkbox_size), Image.LANCZOS)
        unchecked = unchecked.resize((checkbox_size, checkbox_size), Image.LANCZOS)

        # Convert to PhotoImage
        self.checked_img = ImageTk.PhotoImage(checked)
        self.unchecked_img = ImageTk.PhotoImage(unchecked)
            
        self.columns = []

        self.get_columns()

        columnNames = [taskParams.title[col] for col in self.columns]

        self.tree = ttk.Treeview(
            self.scrollTable,
            columns=[col for col in columnNames if col != "Complete"],  # always hide the value of the checkbox column
            show="tree headings"  # include #0 for the checkbox
        )

        self.tree.column("#0", width=2*checkbox_size, stretch=False, anchor="center")
        self.tree.heading("#0", text="")  # optional, leave header blank

        # Keep references to checkbox images
        self.tree.checked_images = {
            "checked": self.checked_img,
            "unchecked": self.unchecked_img
        }

        for col in columnNames:
            if col != "Complete":
                self.tree.heading(col, text=col)
                self.tree.column(col, anchor="center", stretch=True)

        self.tree.bind("<ButtonRelease-1>", self.on_column_resize)
        self.apply_column_widths()

        self.tree.grid(row=0, column=0, sticky="nsew")
        self.vsb = ttk.Scrollbar(self.scrollTable, orient="vertical", command=self.tree.yview)
        self.hsb = ttk.Scrollbar(self.scrollTable, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        self.vsb.grid(row=0, column=1, sticky="ns")
        self.hsb.grid(row=1, column=0, sticky="ew")
        self.scrollTable.grid_rowconfigure(0, weight=1)
        self.scrollTable.grid_columnconfigure(0, weight=1)

        # Load tasks from DB and insert into tree
        self.row_id_map = {}  # Map Treeview item ID → DB row
        tasks = self.db.fetch_tasks(self.columns)
        
        for row in self.db.fetch_tasks(self.columns):
            task_id = row["id"]
            complete_val = bool(row[taskParams.key["Complete"]])
            img = self.checked_img if complete_val else self.unchecked_img

            self.tree.insert(
                "",
                "end",
                iid=str(task_id),
                text="",
                image=img,
                values=[row[col] for col in self.columns if col != taskParams.key["Complete"]]
            )

            # Store checkbox state
            self.checkbox_states[str(task_id)] = complete_val

        # Bind click event for toggling
        self.tree.bind("<Button-1>", self.toggle_complete_checkbox)

    def get_columns(self):
        self.columns = []   # reset columns list
        places = []
        # Increment through all columns
        for column in taskParams.key.values():
            # If the column is set to be visible
            if self.pref.settings["task_column_visible"][column]:
                # Add the place and column key to their respective lists
                places.append(self.pref.settings["task_column_order"][column])
                self.columns.append(column)

        # Sort the columns and order list
        paired = list(zip(places, self.columns))
        self.columns = [col for _, col in sorted(paired, key=lambda x: places.index(x[0]))]

    def apply_column_widths(self):
        # Load saved widths
        saved_widths = self.pref.get_setting("task_column_width") or {}

        for display_name in self.tree["columns"]:
            internal_key = taskParams.key.get(display_name)
            width = saved_widths.get(internal_key, 120)
            self.tree.column(display_name, width=width, anchor="center", stretch=True)

    def on_column_resize(self, event):
        new_widths = {}
        for display_name in self.tree["columns"]:
            internal_key = taskParams.key.get(display_name)
            if internal_key:
                width = self.tree.column(display_name)["width"]
                new_widths[internal_key] = width

        old_widths = self.pref.get_setting("task_column_width") or {}

        # Compare with your stored settings
        if new_widths != old_widths:
            self.pref.settings["task_column_width"] = new_widths
            self.pref.save_settings()

    def toggle_complete_checkbox(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id:
            return

        # Identify the column clicked
        col = self.tree.identify_column(event.x)
        if col != "#0":
            return  # Only respond to clicks in the checkbox column

        # Check if click is inside the image area of #0
        bbox = self.tree.bbox(item_id, column="#0")
        if not bbox:
            return
        x1, y1, width, height = bbox
        # Only toggle if click is roughly inside the checkbox image
        if not (0 <= event.x - x1 <= width and 0 <= event.y - y1 <= height):
            return

        # Toggle stored state
        current_state = self.checkbox_states.get(item_id, False)
        new_state = not current_state
        self.checkbox_states[item_id] = new_state

        # Update image
        new_image = self.checked_img if new_state else self.unchecked_img
        self.tree.item(item_id, image=new_image)

        task_id = int(item_id)
        self.db.modify_task(task_id, ["complete"], [new_state])

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for row in self.db.fetch_active_tasks(self.columns):
            task_id = row["id"]
            complete_val = bool(row[taskParams.key["Complete"]])
            img = self.checked_img if complete_val else self.unchecked_img
            self.tree.insert(
                "", "end", iid=str(task_id),
                values=[row[col] for col in self.columns],
                image=img
            )


    def add_task_popup(self):
        win = tk.Toplevel(self.self.root)
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
            columns = ["name", "start_date_scheduled", "due_date"]
            data = [name, start if start else None, due if due else None]
            self.db.add_task(columns, data)
            self.refresh()
            win.destroy()

        tk.Button(win, text="Save", command=save_task).grid(row=3, column=0, columnspan=2)

    # This does not permanently delete the task from the database, sets it as archived
    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Error", "No task selected")
            return

        # The item iid is the task_id
        task_id = int(selected[0])
        self.db.archive_task(task_id)
        self.refresh()

    def undo_archive_task(self):
        self.db.restore_latest()
        self.refresh()

    def redo_archive_task(self):
        self.db.undo_restore_latest()
        self.refresh() 
    
    def load(self): 
        self.build_table()
        self.refresh()