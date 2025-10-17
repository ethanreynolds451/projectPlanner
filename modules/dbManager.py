import sqlite3
import time

import resources.globalPresets

class Database:
    def __init__(self, parent):
        self.pref = parent.pref
        self.file = parent.file

    def init_db(self, parent):
        self.pref = parent.pref       # make sure to update pref and file in case they changed
        self.file = parent.file
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
            columns_str = ", ".join(columns)
            cursor.execute(f"SELECT id, {columns_str} FROM tasks")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]  # convert each Row to dict

    def fetch_active_tasks(self, columns):
        tasks = self.fetch_tasks(columns)
        return [task for task in tasks if not task.get("archived", 0)]


    def add_task(self, columns, data):
        conn = sqlite3.connect(self.file.db())
        cur = conn.cursor()

        if "name" in columns:
            idx = columns.index("name")
            if not data[idx]:  # empty string or None
                data[idx] = "Untitled"
        else: 
            columns.append("name")
            data.append("Untitled")

        columns_str = ", ".join(columns)
        placeholders = ", ".join("?" for _ in data)
        sql = f"INSERT INTO tasks ({columns_str}) VALUES ({placeholders})"
        cur.execute(sql, data)
        conn.commit()
        conn.close()

    def modify_task(self, task_id, columns, data):
        conn = sqlite3.connect(self.file.db())
        cur = conn.cursor()
        set_clause = ", ".join(f"{col}=?" for col in columns)
        sql = f"UPDATE tasks SET {set_clause}, date_updated=datetime('now') WHERE id=?"
        cur.execute(sql, data + [task_id])
        conn.commit()
        conn.close()

    def duplicate_task(self, task_id):
        conn = sqlite3.connect(self.file.db())
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
        row = cur.fetchone()
        if row:
            columns = [description[0] for description in cur.description if description[0] != "id"]
            values = [row[i] for i in range(len(row)) if cur.description[i][0] != "id"]
            columns_str = ", ".join(columns)
            placeholders = ", ".join("?" for _ in values)
            sql = f"INSERT INTO tasks ({columns_str}) VALUES ({placeholders})"
            cur.execute(sql, values)
            conn.commit()
        conn.close()

    def archive_task(self, task_id):
        conn = sqlite3.connect(self.file.db())
        cur = conn.cursor()
        cur.execute("""
            UPDATE tasks 
            SET archived=1, date_archived=datetime('now'), date_updated=datetime('now') 
            WHERE id=?
        """, (task_id,))
        conn.commit()
        conn.close()

    def restore_task(self, task_id):
        conn = sqlite3.connect(self.file.db())
        cur = conn.cursor()
        cur.execute("""
            UPDATE tasks 
            SET archived=0, date_archived=NULL, date_updated=datetime('now') 
            WHERE id=?
        """, (task_id,))
        conn.commit()
        conn.close()

    def restore_latest(self):
        conn = sqlite3.connect(self.file.db())
        cur = conn.cursor()
        cur.execute("""
            SELECT id FROM tasks 
            WHERE archived=1 
            ORDER BY date_archived DESC 
            LIMIT 1
        """)
        row = cur.fetchone()
        if row:
            task_id = row[0]
            self.restore_task(task_id)
        conn.close()

    def undo_restore_latest(self):
        conn = sqlite3.connect(self.file.db())
        cur = conn.cursor()
        cur.execute("""
            SELECT id FROM tasks 
            WHERE archived=0 AND date_archived IS NULL 
            ORDER BY date_updated DESC 
            LIMIT 1
        """)
        row = cur.fetchone()
        if row:
            task_id = row[0]
            self.archive_task(task_id)
        conn.close()

    def permanently_delete_task(self, task_id):
        conn = sqlite3.connect(self.file.db())
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
        conn.close()
