
import ast
import operator
import re

import customtkinter as ctk

# ---------------------------------------------------------------- theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG = "#0B1120"
PANEL = "#111827"
DISPLAY_BG = "#111827"
KEY_DIGIT = "#1F2937"
KEY_DIGIT_HOVER = "#374151"
KEY_SPECIAL = "#374151"
KEY_SPECIAL_HOVER = "#4B5563"
KEY_OPERATOR = "#4C1D95"
KEY_OPERATOR_HOVER = "#5B21B6"
KEY_EQUALS = "#8B5CF6"
KEY_EQUALS_HOVER = "#7C3AED"
TEXT = "#F9FAFB"
MUTED = "#9CA3AF"
OPERATOR_TEXT = "#DDD6FE"
ERROR = "#F87171"

MAX_LENGTH = 32
OPERATOR_CHARS = "+-*/"
SEPARATORS = r"[+\-*/%()]"

# ---------------------------------------------------------- calculation
BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
UNARY_OPS = {ast.USub: operator.neg, ast.UAdd: operator.pos}


class CalculationError(Exception):
    """Raised when an expression cannot be evaluated."""


def safe_calculate(expression):
    """Evaluate an arithmetic expression without using eval()."""
    expression = expression.replace("%", "/100")
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError:
        raise CalculationError("Invalid expression")

    def evaluate(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in BIN_OPS:
            return BIN_OPS[type(node.op)](evaluate(node.left), evaluate(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY_OPS:
            return UNARY_OPS[type(node.op)](evaluate(node.operand))
        raise CalculationError("Invalid expression")

    try:
        return evaluate(tree.body)
    except ZeroDivisionError:
        raise CalculationError("Cannot divide by zero")
    except OverflowError:
        raise CalculationError("Number too large")


def format_number(value):
    """Turn a result into a clean string (no trailing .0, no float noise)."""
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise CalculationError("Invalid result")
        value = round(value, 10)
        if value.is_integer():
            value = int(value)
    text = str(value)
    if len(text) > 16:
        text = f"{value:.10g}"
    return text


def pretty(expression):
    """Internal expression -> what the user sees."""
    return (expression.replace("*", "×").replace("/", "÷").replace("-", "−"))


# ------------------------------------------------------------------ app
class Calculator(ctk.CTk):
    BUTTONS = [
        [("C", "special"), ("⌫", "special"), ("%", "special"), ("÷", "operator")],
        [("7", "digit"), ("8", "digit"), ("9", "digit"), ("×", "operator")],
        [("4", "digit"), ("5", "digit"), ("6", "digit"), ("−", "operator")],
        [("1", "digit"), ("2", "digit"), ("3", "digit"), ("+", "operator")],
        [("±", "special"), ("0", "digit"), (".", "digit"), ("=", "equals")],
    ]
    TOKENS = {"÷": "/", "×": "*", "−": "-"}

    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.configure(fg_color=BG)
        self.resizable(False, False)
        self.calc_width, self.panel_width, self.height = 380, 290, 700
        self.geometry(f"{self.calc_width}x{self.height}")

        self.expression = ""
        self.just_evaluated = False
        self.message = ""
        self.top_text = ""
        self.history = []
        self.history_open = False

        self.fonts = {
            size: ctk.CTkFont(size=size, weight="bold")
            for size in (46, 38, 30, 24, 18)
        }

        self.calc_frame = ctk.CTkFrame(self, fg_color="transparent",
                                       width=self.calc_width, height=self.height)
        self.calc_frame.pack(side="left", fill="y")
        self.calc_frame.pack_propagate(False)
        self.history_frame = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=0,
                                          width=self.panel_width, height=self.height)
        self.history_frame.pack_propagate(False)

        self.build_topbar()
        self.build_display()
        self.build_keypad()
        self.build_history_panel()
        self.bind("<Key>", self.on_key)
        self.refresh()

    # ------------------------------------------------------------- UI
    def build_topbar(self):
        bar = ctk.CTkFrame(self.calc_frame, fg_color="transparent")
        bar.pack(fill="x", padx=20, pady=(16, 0))
        ctk.CTkLabel(bar, text="Calculator", text_color=MUTED,
                     font=ctk.CTkFont(size=15, weight="bold")).pack(side="left")
        self.history_button = ctk.CTkButton(
            bar, text="History", width=84, height=30, corner_radius=15,
            fg_color=KEY_DIGIT, hover_color=KEY_DIGIT_HOVER, text_color=TEXT,
            font=ctk.CTkFont(size=13, weight="bold"), command=self.toggle_history)
        self.history_button.pack(side="right")

    def build_display(self):
        box = ctk.CTkFrame(self.calc_frame, fg_color=DISPLAY_BG, corner_radius=20,
                           height=170)
        box.pack(fill="x", padx=20, pady=(14, 14))
        box.pack_propagate(False)
        self.top_label = ctk.CTkLabel(box, text="", anchor="e", text_color=MUTED,
                                      font=ctk.CTkFont(size=16))
        self.top_label.pack(fill="x", padx=20, pady=(18, 0))
        self.main_label = ctk.CTkLabel(box, text="0", anchor="e", text_color=TEXT,
                                       font=self.fonts[46])
        self.main_label.pack(fill="both", expand=True, padx=20, pady=(0, 14))

    def build_keypad(self):
        pad = ctk.CTkFrame(self.calc_frame, fg_color="transparent")
        pad.pack(fill="both", expand=True, padx=15, pady=(0, 18))
        styles = {
            "digit": (KEY_DIGIT, KEY_DIGIT_HOVER, TEXT),
            "special": (KEY_SPECIAL, KEY_SPECIAL_HOVER, TEXT),
            "operator": (KEY_OPERATOR, KEY_OPERATOR_HOVER, OPERATOR_TEXT),
            "equals": (KEY_EQUALS, KEY_EQUALS_HOVER, "white"),
        }
        for r, row in enumerate(self.BUTTONS):
            pad.grid_rowconfigure(r, weight=1, uniform="row")
            for c, (label, kind) in enumerate(row):
                pad.grid_columnconfigure(c, weight=1, uniform="col")
                fg, hover, fg_text = styles[kind]
                ctk.CTkButton(
                    pad, text=label, fg_color=fg, hover_color=hover, text_color=fg_text,
                    corner_radius=18, font=ctk.CTkFont(size=24, weight="bold"),
                    command=lambda t=label: self.press(t)
                ).grid(row=r, column=c, padx=5, pady=5, sticky="nsew")

    def build_history_panel(self):
        head = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        head.pack(fill="x", padx=16, pady=(16, 8))
        ctk.CTkLabel(head, text="History", text_color=TEXT,
                     font=ctk.CTkFont(size=18, weight="bold")).pack(side="left")
        ctk.CTkButton(head, text="Clear", width=60, height=28, corner_radius=14,
                      fg_color="transparent", border_width=1, border_color=KEY_SPECIAL,
                      text_color=MUTED, hover_color=KEY_DIGIT,
                      command=self.clear_history).pack(side="right")
        self.history_list = ctk.CTkScrollableFrame(self.history_frame,
                                                   fg_color="transparent")
        self.history_list.pack(fill="both", expand=True, padx=6, pady=(0, 10))

    # -------------------------------------------------------- history
    def toggle_history(self):
        self.history_open = not self.history_open
        if self.history_open:
            self.history_frame.pack(side="right", fill="y")
            self.geometry(f"{self.calc_width + self.panel_width}x{self.height}")
            self.history_button.configure(fg_color=KEY_EQUALS, hover_color=KEY_EQUALS_HOVER)
        else:
            self.history_frame.pack_forget()
            self.geometry(f"{self.calc_width}x{self.height}")
            self.history_button.configure(fg_color=KEY_DIGIT, hover_color=KEY_DIGIT_HOVER)
        self.render_history()

    def render_history(self):
        for w in self.history_list.winfo_children():
            w.destroy()
        if not self.history:
            ctk.CTkLabel(self.history_list, text="No calculations yet",
                         text_color=MUTED).pack(pady=40)
            return
        for expr, result in reversed(self.history):
            ctk.CTkButton(
                self.history_list, text=f"{pretty(expr)}\n= {result}", anchor="e",
                height=56, corner_radius=12, fg_color=KEY_DIGIT, hover_color=KEY_DIGIT_HOVER,
                text_color=TEXT, font=ctk.CTkFont(size=14),
                command=lambda r=result: self.use_result(r)
            ).pack(fill="x", padx=6, pady=4)

    def clear_history(self):
        self.history.clear()
        self.render_history()

    def use_result(self, result):
        self.expression = result
        self.just_evaluated = True
        self.message = ""
        self.top_text = ""
        self.refresh()

    # ---------------------------------------------------------- input
    def press(self, label):
        token = self.TOKENS.get(label, label)
        if label == "C":
            self.clear()
        elif label == "⌫":
            self.backspace()
        elif label == "=":
            self.equals()
        elif label == "±":
            self.toggle_sign()
        else:
            self.add_token(token)
        self.refresh()

    def on_key(self, event):
        ch, sym = event.char, event.keysym
        if sym in ("Return", "KP_Enter") or ch == "=":
            self.press("=")
        elif sym == "BackSpace":
            self.press("⌫")
        elif sym in ("Escape", "Delete"):
            self.press("C")
        elif ch and ch in "0123456789.+-*/%()":
            self.press(ch)
        elif ch in ("x", "X"):
            self.press("×")

    def clear(self):
        self.expression, self.message, self.top_text = "", "", ""
        self.just_evaluated = False

    def backspace(self):
        self.message = ""
        self.just_evaluated = False
        self.top_text = ""
        self.expression = self.expression[:-1]

    def add_token(self, token):
        self.message = ""
        if self.just_evaluated:
            # a number starts fresh; an operator continues from the result
            if token not in OPERATOR_CHARS + "%":
                self.expression = ""
            self.just_evaluated = False
            self.top_text = ""
        expr = self.expression
        if len(expr) >= MAX_LENGTH and token not in OPERATOR_CHARS:
            return
        last = expr[-1] if expr else ""
        segment = re.split(SEPARATORS, expr)[-1]

        def after(chars):
            """True if the expression currently ends with one of `chars`."""
            return bool(last) and last in chars

        if token.isdigit():
            if segment == "0":
                expr = expr[:-1]
            if after(")%"):
                expr += "*"
            expr += token
        elif token == ".":
            if "." in segment:
                return
            if after(")%"):
                expr += "*"
            expr += "." if segment else "0."
        elif token in OPERATOR_CHARS:
            if not expr:
                if token != "-":
                    return
                expr = "-"
            elif after(OPERATOR_CHARS):
                expr = expr[:-1] + token
            elif last == "(":
                if token == "-":
                    expr += token
            else:
                expr += token
        elif token == "%":
            if last.isdigit() or after(")"):
                expr += "%"
            else:
                return
        elif token == "(":
            if last.isdigit() or after(")%."):
                expr += "*"
            expr += "("
        elif token == ")":
            if expr.count("(") > expr.count(")") and (last.isdigit() or after(")%")):
                expr += ")"
            else:
                return
        self.expression = expr

    def toggle_sign(self):
        self.message = ""
        expr = self.expression
        wrapped = re.search(r"\(-(\d+\.?\d*)\)$", expr)
        number = re.search(r"(\d+\.?\d*)$", expr)
        if wrapped:
            self.expression = expr[:wrapped.start()] + wrapped.group(1)
        elif number:
            self.expression = expr[:number.start()] + "(-" + number.group(1) + ")"
        self.just_evaluated = False

    def equals(self):
        expr = self.expression
        if not expr or self.just_evaluated:
            return
        expr += ")" * (expr.count("(") - expr.count(")"))
        while expr and expr[-1] in OPERATOR_CHARS:
            expr = expr[:-1]
        try:
            result = format_number(safe_calculate(expr))
        except CalculationError as err:
            self.message = str(err)
            self.top_text = pretty(expr)
            self.expression = ""
            return
        self.history.append((expr, result))
        self.top_text = pretty(expr) + " ="
        self.expression = result
        self.just_evaluated = True
        if self.history_open:
            self.render_history()

    # -------------------------------------------------------- display
    def preview(self):
        expr = self.expression
        if self.just_evaluated or not expr:
            return ""
        if not re.search(r"[+*/%]|(?<=[\d)])-", expr):
            return ""
        expr += ")" * (expr.count("(") - expr.count(")"))
        while expr and expr[-1] in OPERATOR_CHARS:
            expr = expr[:-1]
        try:
            return "= " + format_number(safe_calculate(expr))
        except (CalculationError, ValueError):
            return ""

    def refresh(self):
        if self.message:
            self.main_label.configure(text=self.message, text_color=ERROR,
                                      font=self.fonts[24])
            self.top_label.configure(text=self.top_text)
            return
        text = pretty(self.expression) or "0"
        n = len(text)
        size = 46 if n <= 9 else 38 if n <= 12 else 30 if n <= 16 else 24 if n <= 21 else 18
        self.main_label.configure(text=text, text_color=TEXT, font=self.fonts[size])
        self.top_label.configure(text=self.top_text or self.preview())


if __name__ == "__main__":
    Calculator().mainloop()