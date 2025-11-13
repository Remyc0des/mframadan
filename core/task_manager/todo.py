#!/Users/remonecarter/projects/mframadan/core/venv/bin/python3

import argparse
import pytermgui as ptg 
import time

from pytermgui.widgets.button import Button
from database import Database
from typing import Any, cast

class TaskUI(ptg.Window):
    def __init__(self, db: Database):
        super().__init__(static_width=80, border="lightgoldenrodyellow", corner="lightgoldenrodyellow", title="[lightgoldenrodyellow bold]Tasks")
        self.db = db
        self.refresh_tasks()
        self.tasks = []
        self.cursor = 0
        self.styles.border = "lightgoldenrodyellow"
        self.styles.corner = "lightgoldenrodyellow"
        self.refresh_tasks()


    def refresh_tasks(self):
        self.tasks = list(self.db.get_all_tasks())

    def update_content(self): 

        for tid, title, due, course, completed in self.tasks: 
            due_fmt = due or "-"
            course_fmt = f"({course})" if course else ""
            checkbox = ptg.Checkbox(title)
            checkbox.checked = bool(completed)


            self.row = checkbox,f"{title}", f"{course_fmt}[/]", f"{due_fmt}"
                               
            
        ##button
        self.canvasync = ptg.Button("Canvas Sync", lambda *_: self.db.get_canvas_tasks())


            
        
    def move_up(self, *_):
        self.cursor = max(0, self.cursor - 1)
        self.update_content()

    def move_down(self, *_):
        self.cursor = min(len(self.tasks) - 1, self.cursor + 1)
        self.update_content()

    def toggle_complete(self, *_):
        tid = self.tasks[self.cursor][0]
        self.db.complete_task(tid)
        self.refresh_tasks()

    @staticmethod
    def macro_time(fmt: str) -> str:
        return time.strftime(fmt)   
    ptg.tim.define("!time", cast(Any,macro_time("%c")))  

    def _build_ui(self): 
        self.styles.border = "lightgoldenrodyellow"
        self.update_content()

    
        with ptg.WindowManager() as manager:
            window = (
                    ptg.Window( 
                    self.row,
                    self.canvasync
                    )
                )
            #manager.add(self)
            
            manager.add(window) 
 
def main():
    parser = argparse.ArgumentParser(description="to do list and task manager CLI")
    sub = parser.add_subparsers(dest="command")

    add = sub.add_parser("add")
    add.add_argument("title")
    add.add_argument("--due")
    add.add_argument("--course")
    
    sub.add_parser("list")
    sub.add_parser("canvaslist")
    sub.add_parser("clear")
    sub.add_parser("help")

    done = sub.add_parser("complete")
    done.add_argument("id", type=int)

    args = parser.parse_args()
    db = Database()
    ui = TaskUI(db)

    if args.command == "add":
        db.add_task(args.title, args.due, args.course)
    elif args.command == "list":
        db.get_all_tasks()  # probably print later
    elif args.command == "complete":
        db.complete_task(args.id)
    elif args.command == "canvaslist":
        db.get_canvas_tasks()
    elif args.command == "help":
        parser.print_help()
    elif args.command == "clear":
        db.clear_board()
    else:
        ui._build_ui()



if __name__ == "__main__":
    main()
