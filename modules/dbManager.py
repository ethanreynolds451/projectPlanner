import sqlite3
import time

import resources.globalPresets

class Database:
    def __init__(self, pref, file):
        self.pref = pref
        self.file = file

    def init_db(self):
        conn = sqlite3.connect(self.file.db())
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT DEFAULT 'task',
                "group" TEXT DEFAULT NULL,
                category TEXT DEFAULT NULL,
                tags TEXT DEFAULT NULL,

                parent INTEGER DEFAULT NULL,
                dependent_on TEXT DEFAULT NULL,
                sort_order INTEGER DEFAULT 0,  
                level INTEGER DEFAULT 0,
                
                complete BOOLEAN DEFAULT 0,
                pct_complete INTEGER DEFAULT 0,
                hrs_estimate REAL DEFAULT NULL,
                hrs_complete REAL DEFAULT 0,
                hrs_remaining REAL DEFAULT NULL,
                hrs_scheduled REAL DEFAULT 0,
                hrs_logged REAL DEFAULT 0,

                start_date_scheduled TEXT DEFAULT NULL,
                end_date_scheduled TEXT DEFAULT NULL,
                duration_scheduled REAL DEFAULT NULL,
                start_date_actual TEXT DEFAULT NULL,
                end_date_actual TEXT DEFAULT NULL,
                duration_actual REAL DEFAULT NULL,
                due_date TEXT DEFAULT NULL,
                days_remaining INTEGER DEFAULT NULL,

                status TEXT DEFAULT 'active',
                priority INTEGER DEFAULT 0,
                urgency INTEGER DEFAULT 0,

                archived BOOLEAN DEFAULT 0,
                date_archived TEXT DEFAULT NULL,
                date_created TEXT DEFAULT (datetime('now')),
                date_updated TEXT DEFAULT (datetime('now')),
                date_completed TEXT DEFAULT NULL,

                assigned_to TEXT DEFAULT NULL,
                created_by TEXT DEFAULT NULL,

                notes TEXT DEFAULT NULL
            )
        """)
        conn.commit()
        conn.close()

    def fetch_tasks(self, columns):
        with sqlite3.connect(self.file.db()) as conn:
            conn.row_factory = sqlite3.Row  # make rows dict-like
            cursor = conn.cursor()
            cols = ", ".join(columns)
            cursor.execute(f"SELECT id, {cols} FROM tasks")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]  # convert each Row to dict

    def add_task(self, name, start_date, due_date):
        conn = sqlite3.connect(self.file.db())
        cur = conn.cursor()
        # columns_str = ", ".join(columns)
        cur.execute("INSERT INTO tasks (name, start_date_scheduled, due_date) VALUES (?, ?, ?)",
                    (name, start_date, due_date))
        conn.commit()
        conn.close()

    def delete_task(self, task_id):
        conn = sqlite3.connect(self.file.db())
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
        conn.close()
