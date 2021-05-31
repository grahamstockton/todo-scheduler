# todo-scheduler
Todo and schedule program with python

## Description
This app is a console-based scheduling and todo-list app for the console. Here is what an example screen looks like:

## Installation
Just download and the files and run todo_schedule. It should work with linux terminal, windows terminal, and powershell. It will create a save file called 'schedule_objects.json' by default, used for saving items between runs.

## Controls
Items are created, modified, or deleted via user input. Supported commands are:

- 'q' or 'quit': quit
- 'n' or 'newday': delete all items and start over
- 's' or 'schedule': create a schedule item
- 'r' or 'reschedule': change the time on a schedule item
- 'e' or 'edit': edit description of a schedule item
- 'd' or 'delete': delete a schedule item
- 't' or 'todo': create a todo item
- 'done': mark todo item as done
- 'u' or 'undone': mark todo item as undone
- 'dt' or 'delete-todo': delete todo item
- 'te' or 'todo-edit': edit description of todo item

## Features to brag about
- Item are saved automatically with JSON
- Visual display of schedule items: items display a time range and stack to prevent overlaps
