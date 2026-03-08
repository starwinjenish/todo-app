import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class Database:
    def __init__(self, db_path: str = "todo.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT DEFAULT 'General',
                due_date TEXT,
                priority TEXT DEFAULT 'Medium',
                status TEXT DEFAULT 'Pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                color TEXT DEFAULT '#6750A4'
            )
        ''')
        
        default_categories = [
            ('Work', '#FF6B6B'),
            ('Personal', '#4ECDC4'),
            ('Shopping', '#FFE66D'),
            ('Health', '#95E1D3'),
            ('General', '#6750A4')
        ]
        
        for cat, color in default_categories:
            cursor.execute('INSERT OR IGNORE INTO categories (name, color) VALUES (?, ?)', (cat, color))
        
        conn.commit()
        conn.close()
    
    def add_task(self, title: str, description: str = "", category: str = "General",
                 due_date: str = None, priority: str = "Medium") -> int:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks (title, description, category, due_date, priority, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, description, category, due_date, priority, "Pending"))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return task_id
    
    def get_all_tasks(self, status: str = None) -> List[Dict]:
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
                SELECT * FROM tasks WHERE status = ? ORDER BY 
                CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 WHEN 'Low' THEN 3 END, 
                due_date ASC
            ''', (status,))
        else:
            cursor.execute('''
                SELECT * FROM tasks ORDER BY 
                CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 WHEN 'Low' THEN 3 END, 
                due_date ASC
            ''')
        
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tasks
    
    def get_task(self, task_id: int) -> Optional[Dict]:
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def update_task(self, task_id: int, **kwargs):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        
        values.append(task_id)
        query = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?"
        
        cursor.execute(query, values)
        conn.commit()
        conn.close()
    
    def complete_task(self, task_id: int):
        completed_at = datetime.now().isoformat()
        self.update_task(task_id, status="Completed", completed_at=completed_at)
    
    def delete_task(self, task_id: int):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()
    
    def get_statistics(self) -> Dict:
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT status, COUNT(*) FROM tasks GROUP BY status')
        status_counts = dict(cursor.fetchall())
        
        cursor.execute('SELECT category, COUNT(*) FROM tasks GROUP BY category')
        category_counts = dict(cursor.fetchall())
        
        cursor.execute('SELECT priority, COUNT(*) FROM tasks GROUP BY priority')
        priority_counts = dict(cursor.fetchall())
        
        cursor.execute('SELECT COUNT(*) FROM tasks WHERE status = "Completed"')
        completed = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM tasks')
        total = cursor.fetchone()[0] or 1
        
        cursor.execute('''
            SELECT date(completed_at), COUNT(*) FROM tasks 
            WHERE status = "Completed" AND completed_at >= date('now', '-7 days')
            GROUP BY date(completed_at)
        ''')
        weekly_stats = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'status': status_counts,
            'category': category_counts,
            'priority': priority_counts,
            'completion_rate': (completed / total) * 100,
            'total_tasks': total,
            'completed_tasks': completed,
            'weekly': weekly_stats
        }
    
    def get_categories(self) -> List[Dict]:
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM categories')
        categories = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return categories