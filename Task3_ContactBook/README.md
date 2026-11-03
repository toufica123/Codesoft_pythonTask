# Task 3: Contact Book

A desktop contact management app built with Python and
[customtkinter](https://github.com/TomSchimansky/CustomTkinter) as part of the
**CodSoft Python Programming Internship**.

## Features
- **Add** contacts with name, phone number, email, and address
- **View** all contacts, grouped alphabetically with coloured initial avatars
- **Search** live by name, phone number, or email
- **Update** any contact's details
- **Delete** a contact (with a confirmation prompt)
- **Input validation**: required fields, phone and email format, and duplicate phone number detection
- Data saved automatically to `contacts.json`
- Light and dark mode
- Keyboard shortcuts: `Ctrl+N` new contact, `Ctrl+F` focus search

## Installation and usage
1. Open a terminal in the `Task3_ContactBook` folder.
2. Install the dependency:
   ```bash
   python -m pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python contact_book.py
   ```

## Project structure
```
Task3_ContactBook/
├── contact_book.py    # main application
├── requirements.txt   # dependencies
├── .gitignore         # keeps personal contacts.json out of Git
└── README.md
```
`contacts.json` is created automatically the first time you save a contact.

## Tech stack
Python, customtkinter (tkinter), JSON, regular expressions (validation)

