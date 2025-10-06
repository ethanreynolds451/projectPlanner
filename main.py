import tkinter as tk

from modules.fileManager import File
file = File()

from modules.dbManager import Database
db = Database()

from apps.homepage import MainApp

# The main application code
# Stuff to execute on application launch
if __name__ == "__main__":
    root = tk.Tk()
    file.get(root)          # have user select project file or create new one
    db.set_db(file.db())    # set the database file
    # selector failed didn't create new file but just opened default
    app = MainApp(root, file, db)
    root.mainloop()