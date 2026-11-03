# Task 2: Modern Calculator

A desktop calculator built with Python and
[customtkinter](https://github.com/TomSchimansky/CustomTkinter) as part of the
**CodSoft Python Programming Internship**.

## Features
- Basic arithmetic: addition, subtraction, multiplication, division
- Percentages, parentheses, and sign toggle (±)
- **Live preview** of the result while you type
- **History panel**: click any past calculation to reuse its result
- **Full keyboard support**
- Clean error messages (for example, "Cannot divide by zero")
- Safe evaluation using Python's `ast` module (no `eval()`)

## Keyboard shortcuts
| Key | Action |
|-----|--------|
| `0-9` `.` | Enter numbers |
| `+` `-` `*` `/` | Operators |
| `%` `(` `)` | Percent and parentheses |
| `Enter` or `=` | Calculate |
| `Backspace` | Delete last character |
| `Esc` or `Delete` | Clear |

## Installation and usage
1. Open a terminal in the `Task2_Calculator` folder.
2. Install the dependency:
   ```bash
   python -m pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python calculator.py
   ```

## Project structure
```
Task2_Calculator/
├── calculator.py      # main application
├── requirements.txt   # dependencies
└── README.md
```

## How it works
Expressions are parsed into an abstract syntax tree and evaluated node by node,
allowing only numbers and the operators `+ - * /`. Anything else is rejected,
so arbitrary code can never be executed.

## Tech stack
Python, customtkinter (tkinter), `ast`

