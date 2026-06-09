import tkinter as tk
from tkinter import messagebox
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import rcParams

rcParams['font.family'] = 'monospace'


# ──────────────────────────────────────────────
#  Pill Button  (smooth rounded rect via canvas)
# ──────────────────────────────────────────────
class PillButton(tk.Canvas):
    PRESS_DARKEN = 0.72          # multiply each RGB channel on press

    def __init__(self, parent, text, bg_color, fg_color="#ffffff",
                 radius=12, command=None, font_spec=("Segoe UI", 10, "bold"),
                 **kwargs):
        super().__init__(parent, bd=0, highlightthickness=0,
                         bg=parent["bg"], **kwargs)
        self.command    = command
        self.radius     = radius
        self.bg_color   = bg_color
        self.press_color = self._darken(bg_color, self.PRESS_DARKEN)
        self.fg_color   = fg_color
        self.label      = text
        self.font_spec  = font_spec

        self.bind("<ButtonPress-1>",   self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Configure>",       lambda _e: self._draw(self.bg_color))

    # ── drawing ──────────────────────────────
    def _draw(self, color):
        self.delete("all")
        w, h, r = self.winfo_width(), self.winfo_height(), self.radius
        if w < 2 or h < 2:
            return
        # four corner arcs + two fill rects
        for x1, y1, x2, y2, start in (
            (0,     0,     r*2,   r*2,   90),
            (w-r*2, 0,     w,     r*2,   0),
            (0,     h-r*2, r*2,   h,     180),
            (w-r*2, h-r*2, w,     h,     270),
        ):
            self.create_arc(x1, y1, x2, y2, start=start, extent=90,
                            fill=color, outline="")
        self.create_rectangle(r, 0,   w-r, h,   fill=color, outline="")
        self.create_rectangle(0, r,   w,   h-r, fill=color, outline="")
        self.create_text(w//2, h//2, text=self.label, fill=self.fg_color,
                         font=self.font_spec)

    @staticmethod
    def _darken(hex_color, factor):
        h = hex_color.lstrip("#")
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return "#{:02x}{:02x}{:02x}".format(
            int(r * factor), int(g * factor), int(b * factor))

    # ── interaction ──────────────────────────
    def _on_press(self,   _e): self._draw(self.press_color)
    def _on_release(self, _e):
        self._draw(self.bg_color)
        if self.command:
            self.command()


# ──────────────────────────────────────────────
#  Main application
# ──────────────────────────────────────────────
class GraphingCalculator:
    # ── palette ──────────────────────────────
    BG          = "#0d1117"   # near-black, GitHub dark inspired
    PANEL       = "#161b22"   # raised surface
    BORDER      = "#30363d"   # subtle dividers
    TEXT        = "#e6edf3"   # primary text
    TEXT_DIM    = "#7d8590"   # secondary / labels
    ACCENT_PLOT = "#58a6ff"   # graph line – cool blue
    ACCENT_OP   = "#f0883e"   # operators – amber
    ACCENT_FN   = "#3fb950"   # math functions – green
    ACCENT_DEL  = "#f85149"   # destructive
    ACCENT_EQ   = "#58a6ff"   # equals / compute
    ACCENT_GR   = "#bc8cff"   # graph action – violet
    ACCENT_PR   = "#388bfd"   # presets – slate blue
    NUM         = "#21262d"   # number keys
    NUM_FG      = "#e6edf3"

    # ── superscript / operator token map ─────
    SUP_MAP = {"²": "**2", "³": "**3", "^": "**"}

    SAFE = {
        "sin": np.sin, "cos": np.cos, "tan": np.tan,
        "arcsin": np.arcsin, "arccos": np.arccos, "arctan": np.arctan,
        "sqrt": np.sqrt, "cbrt": np.cbrt,
        "log": np.log10, "ln": np.log, "exp": np.exp,
        "abs": np.abs, "floor": np.floor, "ceil": np.ceil,
        "pi": np.pi, "e": np.e, "tau": 2 * np.pi, "np": np,
    }

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Graph Calc")
        self.root.configure(bg=self.BG)
        self.root.resizable(False, False)
        self._center(1260, 730)

        self._expr   = ""   # internal  (Python-eval-able)
        self._disp   = ""   # displayed (human-readable)

        self._build_ui()

    # ── window helpers ────────────────────────
    def _center(self, w, h):
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    # ─────────────────────────────────────────
    #  UI construction
    # ─────────────────────────────────────────
    def _build_ui(self):
        self._build_left()
        self._build_right()

    # ── left column: display + keypad ────────
    def _build_left(self):
        left = tk.Frame(self.root, bg=self.BG)
        left.place(x=16, y=16, width=764, height=698)

        # ---- display frame ------------------
        disp_frame = tk.Frame(left, bg=self.PANEL,
                              highlightthickness=1,
                              highlightbackground=self.BORDER)
        disp_frame.place(x=0, y=0, width=764, height=96)

        tk.Label(disp_frame, text="EXPRESSION", bg=self.PANEL,
                 fg=self.TEXT_DIM,
                 font=("Consolas", 8, "bold")).place(x=14, y=8)

        self._disp_var = tk.StringVar()
        self._entry = tk.Entry(
            disp_frame, textvariable=self._disp_var,
            font=("Consolas", 28, "bold"),
            bg=self.PANEL, fg=self.TEXT,
            bd=0, justify="right",
            insertbackground=self.ACCENT_PLOT,
            highlightthickness=0,
        )
        self._entry.place(x=14, y=26, width=736, height=56)
        self._entry.bind("<Key>", self._on_key)
        self._entry.focus_set()

        # ---- status bar (shows result inline) -
        self._status_var = tk.StringVar(value="")
        tk.Label(left, textvariable=self._status_var,
                 bg=self.BG, fg=self.TEXT_DIM,
                 font=("Consolas", 11), anchor="e"
                 ).place(x=0, y=100, width=764, height=20)

        # ---- button grid --------------------
        # (label, internal_value, color_attr)
        keys = [
            ("7",    "7",      "NUM"),  ("8",   "8",      "NUM"),  ("9",   "9",      "NUM"),
            ("÷",    "/",      "ACCENT_OP"), ("sin",  "sin(",   "ACCENT_FN"), ("cos",  "cos(",   "ACCENT_FN"), ("tan",  "tan(",   "ACCENT_FN"),

            ("4",    "4",      "NUM"),  ("5",   "5",      "NUM"),  ("6",   "6",      "NUM"),
            ("×",    "*",      "ACCENT_OP"), ("√",    "sqrt(",  "ACCENT_FN"), ("log",  "log(",   "ACCENT_FN"), ("ln",   "ln(",    "ACCENT_FN"),

            ("1",    "1",      "NUM"),  ("2",   "2",      "NUM"),  ("3",   "3",      "NUM"),
            ("−",    "-",      "ACCENT_OP"), ("(",    "(",      "NUM"),     (")",    ")",      "NUM"),     ("π",    "pi",     "ACCENT_FN"),

            ("0",    "0",      "NUM"),  (".",   ".",      "NUM"),  ("x²",  "**2",    "ACCENT_FN"),
            ("+",    "+",      "ACCENT_OP"), ("e",    "e",      "ACCENT_FN"), ("x³",  "**3",    "ACCENT_FN"), ("xʸ",  "**",     "ACCENT_OP"),
        ]

        BW, BH, GAP = 98, 56, 6
        for i, (lbl, val, cat) in enumerate(keys):
            col, row = i % 7, i // 7
            x = col * (BW + GAP)
            y = 130 + row * (BH + GAP)
            color = getattr(self, cat)
            fg    = self.NUM_FG if cat == "NUM" else "#ffffff"
            self._pill(left, lbl, x, y, BW, BH, color, fg,
                       cmd=lambda v=val: self._press(v))

        # ---- control row --------------------
        CY = 130 + 4 * (BH + GAP) + 8
        ctrl = [
            ("CLR",    22,  self._clear,  self.ACCENT_DEL),
            ("⌫",     126, self._delete, self.NUM),
            ("=",      230, self._calc,   self.ACCENT_EQ),
            ("GRAPH",  400, self._graph,  self.ACCENT_GR),
        ]
        widths = {
            "CLR": 96, "⌫": 96, "=": 160, "GRAPH": 200,
        }
        for lbl, x, cmd, col in ctrl:
            w = widths[lbl]
            self._pill(left, lbl, x, CY, w, BH, col, "#ffffff",
                       cmd=cmd,
                       font_spec=("Segoe UI", 11, "bold"))

        # ---- preset strip -------------------
        PY = CY + BH + 16
        presets = [
            ("y = x",       "x"),
            ("Parabola",    "x**2"),
            ("Cubic",       "x**3"),
            ("Sine",        "sin(x)"),
            ("Cosine",      "cos(x)"),
            ("e^x",         "exp(x)"),
        ]
        PW = (764 - 5 * GAP) // 6
        for i, (lbl, val) in enumerate(presets):
            x = i * (PW + GAP)
            self._pill(left, lbl, x, PY, PW, 42, self.ACCENT_PR, "#ffffff",
                       cmd=lambda v=val: self._load_preset(v),
                       font_spec=("Segoe UI", 9, "bold"))

        # Label above preset strip
        tk.Label(left, text="QUICK PLOT", bg=self.BG, fg=self.TEXT_DIM,
                 font=("Consolas", 8, "bold")
                 ).place(x=0, y=PY - 16, width=764, anchor="w")

    # ── right column: graph panel ─────────────
    def _build_right(self):
        panel = tk.Frame(self.root, bg=self.PANEL,
                         highlightthickness=1,
                         highlightbackground=self.BORDER)
        panel.place(x=796, y=16, width=448, height=698)

        tk.Label(panel, text="PLOT CANVAS", bg=self.PANEL,
                 fg=self.TEXT_DIM,
                 font=("Consolas", 8, "bold")).place(x=14, y=10)

        self._fig = Figure(figsize=(4.2, 5.9), dpi=100,
                           facecolor=self.PANEL)
        self._ax  = self._fig.add_subplot(111)
        self._style_axes()
        self._fig.tight_layout(pad=2.2)

        self._canvas = FigureCanvasTkAgg(self._fig, master=panel)
        self._canvas.get_tk_widget().place(x=4, y=30, width=440, height=620)

        # X-range controls
        ctrl_frame = tk.Frame(panel, bg=self.PANEL)
        ctrl_frame.place(x=14, y=656, width=420, height=30)

        tk.Label(ctrl_frame, text="x range:", bg=self.PANEL,
                 fg=self.TEXT_DIM, font=("Consolas", 9)).pack(side="left")

        self._xmin_var = tk.StringVar(value="-10")
        self._xmax_var = tk.StringVar(value="10")
        for var, lbl in ((self._xmin_var, "min"), (self._xmax_var, "max")):
            tk.Label(ctrl_frame, text=f" {lbl} ", bg=self.PANEL,
                     fg=self.TEXT_DIM, font=("Consolas", 9)).pack(side="left")
            e = tk.Entry(ctrl_frame, textvariable=var, width=5,
                         bg=self.NUM, fg=self.TEXT, bd=0,
                         font=("Consolas", 9),
                         insertbackground=self.ACCENT_PLOT,
                         highlightthickness=1,
                         highlightbackground=self.BORDER)
            e.pack(side="left", padx=(0, 4))

    # ─────────────────────────────────────────
    #  Matplotlib axes styling
    # ─────────────────────────────────────────
    def _style_axes(self):
        ax = self._ax
        ax.set_facecolor(self.BG)
        ax.tick_params(colors=self.TEXT_DIM, labelsize=8)
        ax.grid(True, color=self.BORDER, linestyle="--", linewidth=0.7, alpha=0.8)
        for spine in ax.spines.values():
            spine.set_edgecolor(self.BORDER)
        ax.set_title("", color=self.TEXT, fontsize=10, fontweight="bold", pad=8)
        # subtle axes lines through zero
        ax.axhline(0, color=self.BORDER, linewidth=0.9)
        ax.axvline(0, color=self.BORDER, linewidth=0.9)

    # ─────────────────────────────────────────
    #  Button factory
    # ─────────────────────────────────────────
    def _pill(self, parent, text, x, y, w, h, color, fg,
              cmd=None, font_spec=("Segoe UI", 10, "bold")):
        btn = PillButton(parent, text=text, bg_color=color, fg_color=fg,
                         radius=12, command=cmd, font_spec=font_spec)
        btn.place(x=x, y=y, width=w, height=h)
        return btn

    # ─────────────────────────────────────────
    #  Calculator logic
    # ─────────────────────────────────────────
    def _press(self, val):
        self._expr += str(val)
        self._disp += str(val)
        self._disp_var.set(self._disp)
        self._status_var.set("")

    def _clear(self):
        self._expr = self._disp = ""
        self._disp_var.set("")
        self._status_var.set("")

    def _delete(self):
        self._expr = self._expr[:-1]
        self._disp = self._disp[:-1]
        self._disp_var.set(self._disp)

    def _load_preset(self, expr: str):
        self._clear()
        self._expr = expr
        self._disp = expr
        self._disp_var.set(self._disp)

    def _clean(self, s: str) -> str:
        for token, repl in self.SUP_MAP.items():
            s = s.replace(token, repl)
        return s

    def _calc(self):
        try:
            expr   = self._clean(self._expr)
            result = eval(expr, {"__builtins__": None}, self.SAFE)
            if isinstance(result, (float, np.floating)):
                result = round(float(result), 10)
            self._expr = self._disp = str(result)
            self._disp_var.set(self._disp)
            self._status_var.set("")
        except Exception as exc:
            self._status_var.set(f"  ✗  {exc}")

    def _graph(self):
        try:
            xmin = float(self._xmin_var.get())
            xmax = float(self._xmax_var.get())
            if xmin >= xmax:
                raise ValueError("x min must be less than x max")

            expr = self._clean(self._expr)
            x    = np.linspace(xmin, xmax, 3000)
            ctx  = {**self.SAFE, "x": x}
            y    = eval(expr, {"__builtins__": None}, ctx)

            self._ax.clear()
            self._style_axes()

            # mask infinities so matplotlib doesn't explode the axis limits
            y = np.where(np.isfinite(y), y, np.nan)

            self._ax.plot(x, y, color=self.ACCENT_PLOT,
                          linewidth=2.2, solid_capstyle="round")
            self._ax.fill_between(x, y, alpha=0.08, color=self.ACCENT_PLOT)
            self._ax.set_title(f"y = {self._disp}",
                               color=self.TEXT, fontsize=10,
                               fontweight="bold", pad=8)
            self._fig.tight_layout(pad=2.2)
            self._canvas.draw()
            self._status_var.set("  ✓  Plot updated")
        except Exception as exc:
            self._status_var.set(f"  ✗  {exc}")

    # ── keyboard shortcut support ─────────────
    def _on_key(self, event):
        key = event.keysym
        if key == "Return":
            if self._expr.strip():
                self._graph() if "x" in self._expr else self._calc()
        elif key == "BackSpace":
            self._delete()
            return "break"
        elif key == "Escape":
            self._clear()


# ──────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────
if __name__ == "__main__":
    try:
        root.destroy()           # clean up any previous Spyder instance
    except NameError:
        pass

    root = tk.Tk()
    GraphingCalculator(root)
    root.mainloop()
