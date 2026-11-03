import json
import os
import customtkinter as ctk

FILE_NAME = "tasks.json"
ACCENT = "#6366F1"
ACCENT_HOVER = "#4F46E5"
GREEN = "#22C55E"
RED = "#EF4444"
RED_HOVER = "#DC2626"

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


# ---------- Storage ----------
def load_tasks():
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r", encoding="utf-8") as f:
                return [
                    {"title": str(t["title"]), "completed": bool(t.get("completed", False))}
                    for t in json.load(f)
                ]
        except (json.JSONDecodeError, OSError, KeyError, TypeError):
            return []
    return []


def save_tasks(tasks):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=4)


# ---------- App ----------
class TodoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("My To-Do List")
        self.geometry("780x820")
        self.minsize(560, 600)

        self.tasks = load_tasks()
        self.filter_mode = "All"

        # Centered column so the layout never stretches too wide
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True)
        self.column = ctk.CTkFrame(outer, fg_color="transparent", width=700)
        self.column.pack(fill="y", expand=True, padx=20, pady=20)
        self.column.pack_propagate(False)

        self.build_header()
        self.build_input()
        self.build_filters()
        self.build_list()
        self.build_footer()
        self.refresh()

    # ----- UI sections -----
    def build_header(self):
        top = ctk.CTkFrame(self.column, fg_color="transparent")
        top.pack(fill="x")

        left = ctk.CTkFrame(top, fg_color="transparent")
        left.pack(side="left")
        ctk.CTkLabel(left, text="My Tasks", font=ctk.CTkFont(size=34, weight="bold")
                     ).pack(anchor="w")
        self.subtitle = ctk.CTkLabel(left, text="", font=ctk.CTkFont(size=14),
                                     text_color=("gray40", "gray65"))
        self.subtitle.pack(anchor="w")

        self.theme_switch = ctk.CTkSwitch(top, text="Dark mode", command=self.toggle_theme,
                                          progress_color=ACCENT)
        self.theme_switch.pack(side="right", pady=(10, 0))

        self.progress = ctk.CTkProgressBar(self.column, height=10, progress_color=GREEN)
        self.progress.pack(fill="x", pady=(16, 18))
        self.progress.set(0)

    def build_input(self):
        row = ctk.CTkFrame(self.column, fg_color="transparent")
        row.pack(fill="x")
        self.entry = ctk.CTkEntry(row, placeholder_text="What do you need to do?",
                                  height=46, corner_radius=12, font=ctk.CTkFont(size=15))
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.bind("<Return>", lambda e: self.add_task())
        ctk.CTkButton(row, text="+ Add", width=100, height=46, corner_radius=12,
                      fg_color=ACCENT, hover_color=ACCENT_HOVER,
                      font=ctk.CTkFont(size=15, weight="bold"),
                      command=self.add_task).pack(side="left", padx=(10, 0))

    def build_filters(self):
        row = ctk.CTkFrame(self.column, fg_color="transparent")
        row.pack(fill="x", pady=(16, 10))
        self.segment = ctk.CTkSegmentedButton(
            row, values=["All", "Pending", "Completed"], command=self.set_filter,
            selected_color=ACCENT, selected_hover_color=ACCENT_HOVER, height=38,
        font=ctk.CTkFont(size=14, weight="bold"))
        self.segment.set("All")
        self.segment.pack(side="left")

        self.search = ctk.CTkEntry(row, placeholder_text="Search...", width=190,
                                   height=38, corner_radius=10)
        self.search.pack(side="right")
        self.search.bind("<KeyRelease>", lambda e: self.refresh())

    def build_list(self):
        self.list_frame = ctk.CTkScrollableFrame(self.column, corner_radius=14)
        self.list_frame.pack(fill="both", expand=True)

    def build_footer(self):
        row = ctk.CTkFrame(self.column, fg_color="transparent")
        row.pack(fill="x", pady=(12, 0))
        self.count_label = ctk.CTkLabel(row, text="", text_color=("gray40", "gray65"))
        self.count_label.pack(side="left")
        ctk.CTkButton(row, text="Clear completed", width=140, height=34,
                      fg_color="transparent", border_width=2,
                      border_color=("gray60", "gray40"), text_color=("gray20", "gray85"),
                      hover_color=("gray85", "gray25"),
                      command=self.clear_completed).pack(side="right")

    # ----- rendering -----
    def visible_indexes(self):
        query = self.search.get().strip().lower()
        out = []
        for i, t in enumerate(self.tasks):
            if self.filter_mode == "Pending" and t["completed"]:
                continue
            if self.filter_mode == "Completed" and not t["completed"]:
                continue
            if query and query not in t["title"].lower():
                continue
            out.append(i)
        return out

    def refresh(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        shown = self.visible_indexes()
        if not shown:
            msg = ("Nothing here yet.\nAdd your first task above!" if not self.tasks
                   else "No tasks match this view.")
            ctk.CTkLabel(self.list_frame, text=msg, font=ctk.CTkFont(size=16),
                         text_color=("gray50", "gray60"), justify="center"
                         ).pack(pady=80)
        for i in shown:
            self.make_row(i)

        total = len(self.tasks)
        done = sum(t["completed"] for t in self.tasks)
        self.subtitle.configure(text=f"{total - done} pending  ·  {done} completed")
        self.count_label.configure(text=f"{done} of {total} done")
        self.progress.set(done / total if total else 0)

    def make_row(self, i):
        task = self.tasks[i]
        row = ctk.CTkFrame(self.list_frame, corner_radius=12, height=54,
                           fg_color=("white", "gray20"))
        row.pack(fill="x", pady=5, padx=4)

        var = ctk.BooleanVar(value=task["completed"])
        ctk.CTkCheckBox(row, text="", variable=var, width=28, checkbox_width=26,
                        checkbox_height=26, corner_radius=13, fg_color=GREEN,
                        hover_color="#16A34A", command=lambda: self.toggle(i)
                        ).pack(side="left", padx=(14, 4), pady=12)

        if task["completed"]:
            font = ctk.CTkFont(size=16, overstrike=True)
            color = ("gray55", "gray55")
        else:
            font = ctk.CTkFont(size=16)
            color = ("gray10", "gray95")
        ctk.CTkLabel(row, text=task["title"], font=font, text_color=color, anchor="w",
                     justify="left", wraplength=380).pack(side="left", fill="x", expand=True, padx=8)

        ctk.CTkButton(row, text="Delete", width=64, height=30, corner_radius=8,
                      fg_color="transparent", text_color=RED, hover_color=("#FEE2E2", "#4B1D1D"),
                      command=lambda: self.delete_task(i)).pack(side="right", padx=(0, 10))
        ctk.CTkButton(row, text="Edit", width=56, height=30, corner_radius=8,
                      fg_color="transparent", text_color=ACCENT,
                      hover_color=("#E0E7FF", "#2A2D5A"),
                      command=lambda: self.edit_task(i)).pack(side="right")

    # ----- actions -----
    def toggle_theme(self):
        ctk.set_appearance_mode("dark" if self.theme_switch.get() else "light")

    def set_filter(self, value):
        self.filter_mode = value
        self.refresh()

    def add_task(self):
        title = self.entry.get().strip()
        if not title:
            self.entry.configure(border_color=RED)
            self.after(900, lambda: self.entry.configure(border_color=("#979DA2", "#565B5E")))
            return
        self.tasks.append({"title": title, "completed": False})
        save_tasks(self.tasks)
        self.entry.delete(0, "end")
        self.refresh()

    def toggle(self, i):
        self.tasks[i]["completed"] = not self.tasks[i]["completed"]
        save_tasks(self.tasks)
        self.refresh()

    def delete_task(self, i):
        self.tasks.pop(i)
        save_tasks(self.tasks)
        self.refresh()

    def clear_completed(self):
        self.tasks = [t for t in self.tasks if not t["completed"]]
        save_tasks(self.tasks)
        self.refresh()

    def edit_task(self, i):
        win = ctk.CTkToplevel(self)
        win.title("Edit task")
        win.geometry("420x170")
        win.resizable(False, False)
        win.transient(self)
        win.after(150, win.grab_set)

        ctk.CTkLabel(win, text="Edit task", font=ctk.CTkFont(size=18, weight="bold")
                     ).pack(anchor="w", padx=20, pady=(18, 8))
        entry = ctk.CTkEntry(win, height=40, corner_radius=10)
        entry.pack(fill="x", padx=20)
        entry.insert(0, self.tasks[i]["title"])
        entry.focus()

        def save():
            new = entry.get().strip()
            if not new:
                return
            self.tasks[i]["title"] = new
            save_tasks(self.tasks)
            win.destroy()
            self.refresh()

        entry.bind("<Return>", lambda e: save())
        btns = ctk.CTkFrame(win, fg_color="transparent")
        btns.pack(fill="x", padx=20, pady=16)
        ctk.CTkButton(btns, text="Save", width=90, fg_color=ACCENT,
                      hover_color=ACCENT_HOVER, command=save).pack(side="right")
        ctk.CTkButton(btns, text="Cancel", width=90, fg_color="gray50",
                      hover_color="gray40", command=win.destroy).pack(side="right", padx=8)


if __name__ == "__main__":
    TodoApp().mainloop()