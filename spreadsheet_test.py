import csv
import tkinter as tk
from tkinter import ttk, filedialog

class CSVEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Editor")
        self.tree = None
        self.data = []

        tk.Button(root, text="Open CSV", command=self.load_csv).pack()
        tk.Button(root, text="Save CSV", command=self.save_csv).pack()

    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not path:
            return
        with open(path, newline="") as f:
            reader = csv.reader(f)
            self.data = list(reader)

        if self.tree:
            self.tree.destroy()

        self.tree = ttk.Treeview(self.root, show="headings")
        self.tree.pack(fill="both", expand=True)

        # Set columns
        self.tree["columns"] = [f"col{i}" for i in range(len(self.data[0]))]
        for i, col in enumerate(self.data[0]):
            self.tree.heading(f"col{i}", text=col)
            self.tree.column(f"col{i}", width=100)

        # Insert rows
        for row in self.data[1:]:
            self.tree.insert("", "end", values=row)

        # Make editable
        self.tree.bind("<Double-1>", self.edit_cell)

    def edit_cell(self, event):
        item = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        col_index = int(col.replace("#", "")) - 1

        if not item:
            return

        x, y, width, height = self.tree.bbox(item, col)
        value = self.tree.set(item, column=col)

        entry = tk.Entry(self.tree)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, value)
        entry.focus()

        def save_edit(event):
            new_value = entry.get()
            self.tree.set(item, column=col, value=new_value)
            entry.destroy()

        entry.bind("<Return>", save_edit)
        entry.bind("<Escape>", lambda e: entry.destroy())

    def save_csv(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if not path:
            return
        # Collect all data
        headers = [self.tree.heading(col)["text"] for col in self.tree["columns"]]
        rows = []
        for item in self.tree.get_children():
            rows.append(self.tree.item(item)["values"])

        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVEditor(root)
    root.mainloop()