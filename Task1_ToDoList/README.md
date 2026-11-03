# Task 1: To-Do List App

A modern desktop to-do list application built with Python and
[customtkinter](https://github.com/TomSchimansky/CustomTkinter) as part of the
**CodSoft Python Programming Internship**.

## Features
- Add, edit, and delete tasks
- Mark tasks as completed or pending
- Filter tasks: All, Pending, Completed
- Search tasks by name
- Progress bar showing how much is done
- Light and dark mode
- Tasks are saved automatically in `tasks.json`, so they are still there when you reopen the app

## Requirements
- Python 3.8 or newer
- customtkinter

## Installation and usage
1. Clone or download this repository.
2. Open a terminal in the `Task1_ToDoList` folder.
3. Install the dependency:
   ```bash
   python -m pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   python todo.py
   ```

## Project structure
```
Task1_ToDoList/
├── todo.py            # main application
├── tasks.json         # saved tasks (created automatically)
├── requirements.txt   # dependencies
└── README.md
```

## Tech stack
- Python
- customtkinter (tkinter)
- JSON for data storage
