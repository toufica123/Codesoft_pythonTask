
import json
import os
import re

import customtkinter as ctk

FILE_NAME = "contacts.json"

ACCENT = "#6366F1"
ACCENT_HOVER = "#4F46E5"
RED = "#EF4444"
CARD = ("white", "gray20")
MUTED = ("gray40", "gray65")
AVATAR_COLORS = ["#6366F1", "#EC4899", "#F59E0B", "#10B981", "#0EA5E9",
                 "#8B5CF6", "#EF4444", "#14B8A6"]

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


# ---------------------------------------------------------------- storage
def load_contacts():
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r", encoding="utf-8") as f:
                return [
                    {k: str(c.get(k, "")) for k in ("name", "phone", "email", "address")}
                    for c in json.load(f)
                ]
        except (json.JSONDecodeError, OSError, AttributeError, TypeError):
            return []
    return []


def save_contacts(contacts):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=4, ensure_ascii=False)


# -------------------------------------------------------------- validation
def normalize_phone(phone):
    return re.sub(r"[\s\-().]", "", phone)


def validate_contact(data, contacts, editing=None):
    """Return (clean_data, error_message). `editing` is the index being edited."""
    clean = {k: v.strip() for k, v in data.items()}
    if not clean["name"]:
        return clean, "Name is required."
    if not clean["phone"]:
        return clean, "Phone number is required."
    phone = normalize_phone(clean["phone"])
    if not re.fullmatch(r"\+?\d{7,15}", phone):
        return clean, "Enter a valid phone number (7-15 digits)."
    if clean["email"] and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", clean["email"]):
        return clean, "Enter a valid email address."
    for i, c in enumerate(contacts):
        if i != editing and normalize_phone(c["phone"]) == phone:
            return clean, f"This number already belongs to {c['name']}."
    return clean, ""


def matches(contact, query):
    q = query.lower().strip()
    if not q:
        return True
    return (q in contact["name"].lower()
            or q in normalize_phone(contact["phone"])
            or q in contact["phone"].lower()
            or q in contact["email"].lower())


# ------------------------------------------------------------------ dialogs
class Dialog(ctk.CTkToplevel):
    """Base modal window centred over the main window."""

    def __init__(self, parent, title, width, height):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        x = parent.winfo_x() + (parent.winfo_width() - width) // 2
        y = parent.winfo_y() + (parent.winfo_height() - height) // 3
        self.geometry(f"{width}x{height}+{max(x, 0)}+{max(y, 0)}")
        self.transient(parent)
        self.after(150, self.safe_grab)

    def safe_grab(self):
        try:
            self.grab_set()
        except Exception:
            pass


class ContactForm(Dialog):
    FIELDS = [("name", "Full name *", "e.g. Asha Sharma"),
              ("phone", "Phone number *", "e.g. +91 98765 43210"),
              ("email", "Email", "e.g. asha@example.com"),
              ("address", "Address", "e.g. Kolkata, West Bengal")]

    def __init__(self, parent, contacts, on_save, editing=None):
        title = "Edit contact" if editing is not None else "New contact"
        super().__init__(parent, title, 440, 490)
        self.contacts, self.on_save, self.editing = contacts, on_save, editing
        existing = contacts[editing] if editing is not None else {}

        ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=22, weight="bold")
                     ).pack(anchor="w", padx=26, pady=(22, 6))

        self.entries = {}
        for key, label, placeholder in self.FIELDS:
            ctk.CTkLabel(self, text=label, text_color=MUTED, font=ctk.CTkFont(size=13)
                         ).pack(anchor="w", padx=26, pady=(10, 2))
            entry = ctk.CTkEntry(self, height=40, corner_radius=10,
                                 placeholder_text=placeholder)
            entry.pack(fill="x", padx=26)
            if existing.get(key):
                entry.insert(0, existing[key])
            entry.bind("<Return>", lambda e: self.submit())
            self.entries[key] = entry
        self.entries["name"].focus()

        self.error = ctk.CTkLabel(self, text="", text_color=RED, font=ctk.CTkFont(size=13))
        self.error.pack(anchor="w", padx=26, pady=(10, 0))

        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=26, pady=(8, 0))
        ctk.CTkButton(row, text="Save", width=100, height=38, corner_radius=10,
                      fg_color=ACCENT, hover_color=ACCENT_HOVER,
                      command=self.submit).pack(side="right")
        ctk.CTkButton(row, text="Cancel", width=100, height=38, corner_radius=10,
                      fg_color="gray50", hover_color="gray40",
                      command=self.destroy).pack(side="right", padx=8)

    def submit(self):
        data = {k: e.get() for k, e in self.entries.items()}
        clean, error = validate_contact(data, self.contacts, self.editing)
        if error:
            self.error.configure(text=error)
            return
        self.on_save(clean, self.editing)
        self.destroy()


class ConfirmDialog(Dialog):
    def __init__(self, parent, message, on_confirm):
        super().__init__(parent, "Confirm", 380, 170)
        ctk.CTkLabel(self, text=message, wraplength=330, justify="left",
                     font=ctk.CTkFont(size=15)).pack(padx=26, pady=(28, 18), anchor="w")
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", padx=26)
        ctk.CTkButton(row, text="Delete", width=100, height=36, fg_color=RED,
                      hover_color="#DC2626",
                      command=lambda: (on_confirm(), self.destroy())).pack(side="right")
        ctk.CTkButton(row, text="Cancel", width=100, height=36, fg_color="gray50",
                      hover_color="gray40", command=self.destroy).pack(side="right", padx=8)


# --------------------------------------------------------------------- app
class ContactBook(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Contact Book")
        self.geometry("820x800")
        self.minsize(600, 600)

        self.contacts = load_contacts()
        self.status_job = None

        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True)
        self.column = ctk.CTkFrame(outer, fg_color="transparent", width=720)
        self.column.pack(fill="y", expand=True, padx=20, pady=20)
        self.column.pack_propagate(False)

        self.build_header()
        self.build_toolbar()
        self.list_frame = ctk.CTkScrollableFrame(self.column, corner_radius=14)
        self.list_frame.pack(fill="both", expand=True, pady=(0, 8))
        self.status = ctk.CTkLabel(self.column, text="", text_color=MUTED, height=20)
        self.status.pack(anchor="w")

        self.bind("<Control-n>", lambda e: self.open_form())
        self.bind("<Control-f>", lambda e: self.search.focus())
        self.refresh()

    # --------------------------------------------------------------- UI
    def build_header(self):
        top = ctk.CTkFrame(self.column, fg_color="transparent")
        top.pack(fill="x")
        left = ctk.CTkFrame(top, fg_color="transparent")
        left.pack(side="left")
        ctk.CTkLabel(left, text="Contacts", font=ctk.CTkFont(size=34, weight="bold")
                     ).pack(anchor="w")
        self.subtitle = ctk.CTkLabel(left, text="", text_color=MUTED,
                                     font=ctk.CTkFont(size=14))
        self.subtitle.pack(anchor="w")
        self.theme_switch = ctk.CTkSwitch(top, text="Dark mode", progress_color=ACCENT,
                                          command=self.toggle_theme)
        self.theme_switch.pack(side="right", pady=(10, 0))

    def build_toolbar(self):
        row = ctk.CTkFrame(self.column, fg_color="transparent")
        row.pack(fill="x", pady=(18, 14))
        self.search = ctk.CTkEntry(row, height=46, corner_radius=12,
                                   placeholder_text="Search by name, phone or email...",
                                   font=ctk.CTkFont(size=15))
        self.search.pack(side="left", fill="x", expand=True)
        self.search.bind("<KeyRelease>", lambda e: self.refresh())
        ctk.CTkButton(row, text="+ New Contact", width=140, height=46, corner_radius=12,
                      fg_color=ACCENT, hover_color=ACCENT_HOVER,
                      font=ctk.CTkFont(size=15, weight="bold"),
                      command=self.open_form).pack(side="left", padx=(10, 0))

    # ------------------------------------------------------- rendering
    def refresh(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        query = self.search.get()
        shown = sorted(
            [(i, c) for i, c in enumerate(self.contacts) if matches(c, query)],
            key=lambda ic: ic[1]["name"].lower())

        total = len(self.contacts)
        if query.strip():
            self.subtitle.configure(text=f"{len(shown)} of {total} contacts")
        else:
            self.subtitle.configure(text=f"{total} contact{'s' if total != 1 else ''}")

        if not shown:
            msg = ("No contacts yet.\nClick “+ New Contact” to add your first one!"
                   if not self.contacts else "No contacts match your search.")
            ctk.CTkLabel(self.list_frame, text=msg, text_color=MUTED, justify="center",
                         font=ctk.CTkFont(size=16)).pack(pady=90)
            return

        current_letter = None
        for index, contact in shown:
            letter = contact["name"][:1].upper()
            letter = letter if letter.isalpha() else "#"
            if letter != current_letter:
                current_letter = letter
                ctk.CTkLabel(self.list_frame, text=letter, text_color=ACCENT,
                             font=ctk.CTkFont(size=14, weight="bold")
                             ).pack(anchor="w", padx=10, pady=(10, 0))
            self.make_card(index, contact)

    def make_card(self, index, contact):
        card = ctk.CTkFrame(self.list_frame, corner_radius=14, fg_color=CARD)
        card.pack(fill="x", padx=4, pady=5)

        color = AVATAR_COLORS[sum(map(ord, contact["name"])) % len(AVATAR_COLORS)]
        avatar = ctk.CTkFrame(card, width=48, height=48, corner_radius=24, fg_color=color)
        avatar.pack(side="left", padx=(14, 12), pady=14)
        avatar.pack_propagate(False)
        ctk.CTkLabel(avatar, text=contact["name"][:1].upper(), text_color="white",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(expand=True)

        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, pady=10)
        ctk.CTkLabel(info, text=contact["name"], anchor="w",
                     font=ctk.CTkFont(size=17, weight="bold")).pack(fill="x")
        ctk.CTkLabel(info, text=f"Phone: {contact['phone']}",
                     anchor="w", text_color=MUTED).pack(fill="x")
        if contact["email"]:
            ctk.CTkLabel(info, text=f"Email: {contact['email']}", anchor="w",
                         text_color=MUTED).pack(fill="x")
        if contact["address"]:
            ctk.CTkLabel(info, text=f"Address: {contact['address']}", anchor="w",
                         text_color=MUTED, wraplength=360, justify="left").pack(fill="x")

        ctk.CTkButton(card, text="Delete", width=64, height=30, corner_radius=8,
                      fg_color="transparent", text_color=RED,
                      hover_color=("#FEE2E2", "#4B1D1D"),
                      command=lambda: self.confirm_delete(index)
                      ).pack(side="right", padx=(0, 10))
        ctk.CTkButton(card, text="Edit", width=56, height=30, corner_radius=8,
                      fg_color="transparent", text_color=ACCENT,
                      hover_color=("#E0E7FF", "#2A2D5A"),
                      command=lambda: self.open_form(index)).pack(side="right")

    # ----------------------------------------------------------- actions
    def toggle_theme(self):
        ctk.set_appearance_mode("dark" if self.theme_switch.get() else "light")

    def flash(self, text):
        self.status.configure(text=text)
        if self.status_job:
            self.after_cancel(self.status_job)
        self.status_job = self.after(2500, lambda: self.status.configure(text=""))

    def open_form(self, editing=None):
        ContactForm(self, self.contacts, self.save_contact, editing)

    def save_contact(self, data, editing):
        if editing is None:
            self.contacts.append(data)
            self.flash(f"Added {data['name']}")
        else:
            self.contacts[editing] = data
            self.flash(f"Updated {data['name']}")
        save_contacts(self.contacts)
        self.refresh()

    def confirm_delete(self, index):
        name = self.contacts[index]["name"]
        ConfirmDialog(self, f"Delete {name} from your contacts? This can't be undone.",
                      lambda: self.delete_contact(index))

    def delete_contact(self, index):
        name = self.contacts.pop(index)["name"]
        save_contacts(self.contacts)
        self.flash(f"Deleted {name}")
        self.refresh()


if __name__ == "__main__":
    ContactBook().mainloop()