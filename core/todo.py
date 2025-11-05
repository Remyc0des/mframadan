#!/Users/remonecarter/projects/mframadan/core/venv/bin/python3
import sqlite3
import argparse
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv
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
console = Console()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS tasks (
        id INTERGER PRIMARY KEY,
        title TEXT NOT NULL,
        due_date TEXT,
        course TEXT,
        completed INTEGER DEFAULT 0
    )""")
    conn.commit()
    conn.close()


def add_task(title, due_date=None, course=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO tasks (title, due_date, course) VALUES (?, ?, ?)", (title, due_date, course))
    conn.commit()
    conn.close()
    console.print(f"[green]Added: [/green] {title} ({course or 'No course'})")



def  get_canvas_tasks():
    print(API_URL)
    todos = canvas.get_todo_items()
    for todo in todos:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
                f"""
                INSERT INTO tasks (title, due_date, course)
                SELECT '{todo.assignment['name']}', '{todo.assignment['due_at']}', '{todo.context_name}'
                WHERE NOT EXISTS (
                    SELECT 1 FROM tasks WHERE title = '{todo.assignment['name']}'
                )
                """
                )
        conn.commit()
        conn.close()
    console.print(f"[green]Added missing task from canvas")



    


    


def list_tasks():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, title, due_date, course, completed FROM tasks ORDER BY completed, due_date")
    tasks = c.fetchall()
    conn.close()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID")
    table.add_column("Task")
    table.add_column("Due")
    table.add_column("Status")
    table.add_column("Course")

    for t in tasks:
        status = "✅" if t[4] else "🕓"
        course = t[3] or "-"
        table.add_row(str(t[0]), t[1], t[2] or "-", status, course)
    console.print(table)


def complete_task(task_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE tasks SET completed=1 WHERE id=?", (task_id,))
    conn.commit()
    conn.close()
    console.print(f"[cyan]Completed task {task_id}[/cyan]")


def main():
    parser = argparse.ArgumentParser(description="Simple To-Do CLI")
    sub = parser.add_subparsers(dest="command")
    
    add = sub.add_parser("add")
    add.add_argument("title")
    add.add_argument("--due")
    add.add_argument("--course")

    sub.add_parser("list")

    sub.add_parser("canvaslist")

    done = sub.add_parser("complete")
    done.add_argument("id", type=int)

    args = parser.parse_args()
    init_db()

    if args.command == "add":
        add_task(args.title, args.due, args.course)
    elif args.command == "list":
        list_tasks()
    elif args.command == "complete":
        complete_task(args.id)
    elif args.command == "canvaslist":
        get_canvas_tasks()
    else: 
        parser.print_help()

if __name__ == "__main__":
    main()
