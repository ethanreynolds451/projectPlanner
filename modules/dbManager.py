import sqlite3

class Database:
    def __init__(self):
        self.db_file = None
    
    def set_db(self, db_file):
        self.db_file = db_file
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_file)
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

    def fetch_tasks(self):
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.execute("SELECT id, name, start_date, due_date, percent_complete, status FROM tasks")
        rows = cur.fetchall()
        conn.close()
        return rows

    def add_task(self, name, start_date, due_date):
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.execute("INSERT INTO tasks (name, start_date, due_date) VALUES (?, ?, ?)",
                    (name, start_date, due_date))
        conn.commit()
        conn.close()

    def delete_task(self, task_id):
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
        conn.close()
