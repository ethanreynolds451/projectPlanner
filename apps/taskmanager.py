import tkinter as tk
from tkinter import ttk, PhotoImage
from PIL import Image, ImageTk  # Requires Pillow


from resources.globalPresets import taskParameters as taskParams

class taskManagerApp:
    def __init__(self, root, pref, file, db):
        self.root = root
        self.pref = pref
        self.file = file
        self.db = db

        self.checkbox_states = {}  # item_id -> bool

        checkbox_size = 15

        checked = Image.open("resources/images/checkbox_checked_green.png")
        unchecked = Image.open("resources/images/checkbox_unchecked.png")

        # Resize to fit row height (keeping aspect ratio)
        checked = checked.resize((checkbox_size, checkbox_size), Image.LANCZOS)
        unchecked = unchecked.resize((checkbox_size, checkbox_size), Image.LANCZOS)

        self.checked_img = ImageTk.PhotoImage(checked)
        self.unchecked_img = ImageTk.PhotoImage(unchecked)
            
        self.columns = []

        # Task list with scrollbar
        self.scrollTable = tk.Frame(root)
        self.scrollTable.grid(row=0, column=0, sticky="nsew")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        def build_table(self):
            self.get_columns()

            columnNames = [taskParams.title[col] for col in self.columns]

            self.tree = ttk.Treeview(
                self.scrollTable,
                columns=[col for col in columnNames if col != "Complete"],  # always hide the value of the checkbox column
                show="tree headings"  # include #0 for the checkbox
            )

            self.tree.column("#0", width=checkbox_size, stretch=False, anchor="center")
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


        build_table(self)

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.grid(row=1, column=0, sticky="nsew")

        tk.Button(btn_frame, text="Add Task", command=self.add_task_popup).pack(side="left")
        tk.Button(btn_frame, text="Delete Task", command=self.delete_selected).pack(side="left")
        tk.Button(btn_frame, text="Refresh", command=self.refresh).pack(side="left")

        self.refresh()

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

        col = self.tree.identify_column(event.x)
        if not col or int(col.replace("#","")) - 1 != 0:
            return  # only toggle #0 column

        # Toggle stored state
        current_state = self.checkbox_states.get(item_id, False)
        new_state = not current_state
        self.checkbox_states[item_id] = new_state

        # Update image
        new_image = self.checked_img if new_state else self.unchecked_img
        self.tree.item(item_id, image=new_image)

        # Update database if you want
        # task_id = int(item_id)
        # self.db.update_task_complete(task_id, new_state)

    def refresh(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for row in self.db.fetch_tasks(self.columns):
            task_id = row["id"]
            complete_val = bool(row[taskParams.key["Complete"]])
            img = self.checked_img if complete_val else self.unchecked_img
            self.tree.insert(
                "", "end", iid=str(task_id),
                values=[row[col] for col in self.columns],
                image=img
            )


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
