#!/Users/remonecarter/projects/mframadan/core/venv/bin/python3
import sqlite3
from dotenv import load_dotenv
import rich
import os
from canvasapi import Canvas
import json 

load_dotenv()
CONFIG_FILE = os.path.expanduser("~/.config/mframadan/config.json")
with open(CONFIG_FILE) as f:
    config = json.load(f)

auth_token = config.get("auth_token")
API_URL = config.get("API_URL")
canvas = Canvas(API_URL, auth_token)
DB_PATH = os.path.expanduser("~/.local/share/todo.db")


class Database:
    def __init__(self, DBP=DB_PATH):
        self.conn = sqlite3.connect(DBP)
        self.c = self.conn.cursor()
        self.init_db()
    def init_db(self):
        query = """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            due_date TEXT,
            course TEXT,
            completed INTEGER DEFAULT 0
        ) """
        self.c.execute(query)

    def _run_query(self, query, *query_args):
        result = self.c.execute(query, *query_args)
        self.conn.commit()
        return result
    def  get_canvas_tasks(self):
        todos = canvas.get_todo_items()
        for todo in todos: 
            self._run_query(f"""
                            INSERT INTO tasks (title, due_date, course) 
                            SELECT '{todo.assignment['name']}', '{todo.assignment['due_at']}', '{todo.context_name}' 
                            WHERE NOT EXISTS ( 
                                SELECT 1 FROM tasks WHERE title == '{todo.assignment['name']}'
                            ) 
                            """
                            )
            print("Added missing task from canvas")


    def add_task(self, title, due_date, course):
        self._run_query('INSERT INTO tasks (title, due_date, course) VALUES (?, ?, ?)', (title, due_date, course))
        print(f"[green]Added: [/green] {title} ({course or 'No course'})")
    def get_all_tasks(self):
        res = self.c.execute("SELECT id, title, due_date, course, completed FROM tasks")
        return res
       # return result.fetchall()
    def clear_board(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM tasks")
        conn.commit()
        conn.close()
        print("All task erased:)")
    def complete_task(self,task_id):
        self._run_query("UPDATE tasks SET completed=1 WHERE id=?",(task_id,))
        print(f"[cyan]Completed task {task_id}[/cyan]")
