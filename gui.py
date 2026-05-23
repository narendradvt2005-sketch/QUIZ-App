import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import random
import os
import math

DB_NAME = "quiz1.db"

# ---------------------------------------------------------
# GLOBAL DRAW HELPERS FOR CANVAS CARD AESTHETICS
# ---------------------------------------------------------

def draw_rounded_rect(canvas, x1, y1, x2, y2, radius=12, fill_color="", border_color="", border_width=1):
    max_r = min(abs(x2 - x1) // 2, abs(y2 - y1) // 2)
    if radius > max_r:
        radius = max(max_r, 1)

    # Arc corners
    canvas.create_arc(x1, y1, x1+2*radius, y1+2*radius, start=90, extent=90, fill=fill_color, outline="", style="pieslice")
    canvas.create_arc(x2-2*radius, y1, x2, y1+2*radius, start=0, extent=90, fill=fill_color, outline="", style="pieslice")
    canvas.create_arc(x1, y2-2*radius, x1+2*radius, y2, start=180, extent=90, fill=fill_color, outline="", style="pieslice")
    canvas.create_arc(x2-2*radius, y2-2*radius, x2, y2, start=270, extent=90, fill=fill_color, outline="", style="pieslice")

    # Internal fill blocks
    canvas.create_rectangle(x1+radius, y1, x2-radius, y2, fill=fill_color, outline="")
    canvas.create_rectangle(x1, y1+radius, x2, y2-radius, fill=fill_color, outline="")

    # Border arcs & lines
    if border_color:
        canvas.create_arc(x1, y1, x1+2*radius, y1+2*radius, start=90, extent=90, style="arc", outline=border_color, width=border_width)
        canvas.create_arc(x2-2*radius, y1, x2, y1+2*radius, start=0, extent=90, style="arc", outline=border_color, width=border_width)
        canvas.create_arc(x1, y2-2*radius, x1+2*radius, y2, start=180, extent=90, style="arc", outline=border_color, width=border_width)
        canvas.create_arc(x2-2*radius, y2-2*radius, x2, y2, start=270, extent=90, style="arc", outline=border_color, width=border_width)

        canvas.create_line(x1+radius, y1, x2-radius, y1, fill=border_color, width=border_width)
        canvas.create_line(x1+radius, y2, x2-radius, y2, fill=border_color, width=border_width)
        canvas.create_line(x1, y1+radius, x1, y2-radius, fill=border_color, width=border_width)
        canvas.create_line(x2, y1+radius, x2, y2-radius, fill=border_color, width=border_width)


def draw_rounded_border(canvas, x1, y1, x2, y2, radius=12, border_color="#E2E8F0", border_width=1):
    max_r = min(abs(x2 - x1) // 2, abs(y2 - y1) // 2)
    if radius > max_r:
        radius = max(max_r, 1)

    canvas.create_arc(x1, y1, x1+2*radius, y1+2*radius, start=90, extent=90, style="arc", outline=border_color, width=border_width)
    canvas.create_arc(x2-2*radius, y1, x2, y1+2*radius, start=0, extent=90, style="arc", outline=border_color, width=border_width)
    canvas.create_arc(x1, y2-2*radius, x1+2*radius, y2, start=180, extent=90, style="arc", outline=border_color, width=border_width)
    canvas.create_arc(x2-2*radius, y2-2*radius, x2, y2, start=270, extent=90, style="arc", outline=border_color, width=border_width)

    canvas.create_line(x1+radius, y1, x2-radius, y1, fill=border_color, width=border_width)
    canvas.create_line(x1+radius, y2, x2-radius, y2, fill=border_color, width=border_width)
    canvas.create_line(x1, y1+radius, x1, y2-radius, fill=border_color, width=border_width)
    canvas.create_line(x2, y1+radius, x2, y2-radius, fill=border_color, width=border_width)


def draw_rounded_gradient(canvas, x1, y1, x2, y2, radius=12, color1="#0F172A", color2="#2563EB"):
    w = int(x2 - x1)
    h = int(y2 - y1)
    if w <= 0 or h <= 0:
        return

    max_r = min(w // 2, h // 2)
    if radius > max_r:
        radius = max(max_r, 1)

    def hex_to_rgb(hex_str):
        hex_str = hex_str.lstrip('#')
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)

    for i in range(w):
        y_start = 0
        y_end = h

        if i < radius:
            dx = radius - i
            dy = radius - math.sqrt(max(0.0, radius**2 - dx**2))
            y_start = dy
            y_end = h - dy
        elif i > w - radius:
            dx = i - (w - radius)
            dy = radius - math.sqrt(max(0.0, radius**2 - dx**2))
            y_start = dy
            y_end = h - dy

        r = int(r1 + (r2 - r1) * i / w)
        g = int(g1 + (g2 - g1) * i / w)
        b = int(b1 + (b2 - b1) * i / w)
        color = f"#{r:02x}{g:02x}{b:02x}"

        canvas.create_line(x1 + i, y1 + y_start, x1 + i, y1 + y_end, fill=color)


# ---------------------------------------------------------
# MAIN QUIZ APP CODE
# ---------------------------------------------------------

class QuizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("EvalPro - Academic Evaluation System")
        self.geometry("1180x780")
        self.configure(bg="#F1F5F9")
        self.minsize(1100, 720)

        # Center Window
        self.update_idletasks()
        width = self.winfo_width()
        frm_width = self.winfo_rootx() - self.winfo_x()
        win_width = width + 2 * frm_width
        height = self.winfo_height()
        titlebar_height = self.winfo_rooty() - self.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = self.winfo_screenwidth() // 2 - win_width // 2
        y = self.winfo_screenheight() // 2 - win_height // 2
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

        self.validate_database()
        self.setup_styles()

        # Layout Setup
        self.main_layout = tk.Frame(self, bg="#F1F5F9")
        self.main_layout.pack(fill="both", expand=True)

        # Sidebar Canvas
        self.sidebar = tk.Canvas(self.main_layout, bg="#09090B", bd=0, highlightthickness=0, width=255)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        def draw_sidebar_bg(event=None):
            self.sidebar.delete("bg")
            w = self.sidebar.winfo_width()
            h = self.sidebar.winfo_height()
            if w <= 0 or h <= 0:
                return
            r1, g1, b1 = 9, 9, 11
            r2, g2, b2 = 2, 6, 23
            for i in range(0, h, 2):
                r = int(r1 + (r2 - r1) * i / h)
                g = int(g1 + (g2 - g1) * i / h)
                b = int(b1 + (b2 - b1) * i / h)
                self.sidebar.create_rectangle(0, i, w, i+2, fill=f"#{r:02x}{g:02x}{b:02x}", outline="", tags="bg")

        self.sidebar.bind("<Configure>", draw_sidebar_bg)

        # Main content area (Right)
        self.content_container = tk.Frame(self.main_layout, bg="#F1F5F9")
        self.content_container.pack(side="right", fill="both", expand=True)
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        self.build_sidebar()

        self.frames = {}
        self.shared_data = {}

        for F in (HomeDashboard, AddQuestionFrame, ViewQuestionsFrame, DeleteQuestionFrame, PreQuizFrame, QuizFrame, QuizResultFrame, LeaderboardFrame):
            page_name = F.__name__
            frame = F(parent=self.content_container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.active_tab = None
        self.show_frame("HomeDashboard")

    def validate_database(self):
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions(
                question_id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT,
                option1 TEXT,
                option2 TEXT,
                option3 TEXT,
                option4 TEXT,
                correct_answer TEXT
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_scores(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                total_questions INTEGER,
                score INTEGER,
                percentage INTEGER
            )
            """)
            cursor.execute("SELECT COUNT(*) FROM questions")
            count = cursor.fetchone()[0]

            if count == 0:
                default_questions = [
                    ("How many elements are in the periodic table?", "116", "117", "118", "119", "C"),
                    ("Which animal lays the largest eggs?", "Whale", "Crocodile", "Elephant", "Ostrich", "D"),
                    ("What is the most abundant gas in Earth's atmosphere?", "Nitrogen", "Oxygen", "Carbon-Dioxide", "Hydrogen", "A"),
                    ("How many bones are in the human body?", "206", "207", "208", "209", "A"),
                    ("Which planet in the solar system is the hottest?", "Mercury", "Venus", "Earth", "Mars", "B")
                ]
                for q in default_questions:
                    cursor.execute("""
                    INSERT INTO questions (question, option1, option2, option3, option4, correct_answer)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, q)
                conn.commit()
            conn.close()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to validate database:\n{e}")
            self.destroy()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure("TFrame", background="#F1F5F9")
        style.configure("TLabel", background="#F1F5F9", font=("Segoe UI", 11), foreground="#1E293B")
        style.configure("Title.TLabel", font=("Segoe UI", 24, "bold"), foreground="#0F172A", background="#F1F5F9")
        style.configure("Subtitle.TLabel", font=("Segoe UI", 11), foreground="#64748B", background="#F1F5F9")

        # Treeview
        style.configure("Treeview",
                        background="#FFFFFF",
                        foreground="#0F172A",
                        rowheight=52,
                        fieldbackground="#FFFFFF",
                        font=("Segoe UI", 10),
                        borderwidth=0,
                        highlightthickness=0)
        style.map('Treeview',
                  background=[('selected', '#EFF6FF')],
                  foreground=[('selected', '#2563EB')])

        style.configure("Treeview.Heading",
                        font=("Segoe UI Bold", 9),
                        background="#0F172A",
                        foreground="#F1F5F9",
                        borderwidth=0,
                        padding=14)
        style.map("Treeview.Heading",
                  background=[('active', '#1E293B')],
                  foreground=[('active', '#F1F5F9')])

        style.configure("Vertical.TScrollbar",
                        background="#CBD5E1",
                        troughcolor="#F8FAFC",
                        borderwidth=0,
                        bordercolor="#F8FAFC",
                        lightcolor="#CBD5E1",
                        darkcolor="#CBD5E1",
                        arrowsize=0,
                        width=10)
        style.map("Vertical.TScrollbar",
                  background=[('active', '#94A3B8')])

    def build_sidebar(self):
        # App Branding
        branding = tk.Frame(self.sidebar, bg="#09090B")
        self.sidebar.create_window(127, 85, window=branding, anchor="center")

        logo_lbl = tk.Label(branding, text="🎓 EvalPro", font=("Segoe UI", 22, "bold"), fg="#FFFFFF", bg="#09090B")
        logo_lbl.pack(anchor="w")

        sub_lbl = tk.Label(branding, text="Academic Evaluation Platform", font=("Segoe UI Semibold", 9), fg="#71717A", bg="#09090B")
        sub_lbl.pack(anchor="w", pady=(3, 0))

        # Navigation Links Frame
        self.nav_frame = tk.Frame(self.sidebar, bg="#09090B")
        self.sidebar.create_window(127, 340, window=self.nav_frame, anchor="center", width=225)

        self.nav_buttons = {}
        nav_items = [
            ("HomeDashboard", "📊  Dashboard Home"),
            ("ViewQuestionsFrame", "📚  Question Bank"),
            ("AddQuestionFrame", "➕  Add Question"),
            ("DeleteQuestionFrame", "🗑️  Delete Question"),
            ("LeaderboardFrame", "🏆  Leaderboard"),
            ("PreQuizFrame", "📝  Start Quiz")
        ]

        for frame_name, display_text in nav_items:
            item_container = tk.Frame(self.nav_frame, bg="#09090B")
            item_container.pack(fill="x", pady=5)

            indicator = tk.Frame(item_container, bg="#09090B", width=4)
            indicator.pack(side="left", fill="y")

            btn = tk.Button(item_container, text=f"   {display_text}", font=("Segoe UI Semibold", 11),
                            fg="#A1A1AA", bg="#09090B", activeforeground="#FFFFFF", activebackground="#18181B",
                            anchor="w", relief="flat", bd=0, padx=12, pady=10,
                            command=lambda f=frame_name: self.show_frame(f))
            btn.pack(side="left", fill="x", expand=True)

            btn.bind("<Enter>", lambda e, b=btn: self.on_nav_enter(b))
            btn.bind("<Leave>", lambda e, b=btn: self.on_nav_leave(b))

            self.nav_buttons[frame_name] = (item_container, indicator, btn)

        # Footer Status details
        footer = tk.Frame(self.sidebar, bg="#09090B")
        self.sidebar.create_window(127, 715, window=footer, anchor="center", width=215)

        status_lbl = tk.Label(footer, text="Database Connected", font=("Segoe UI", 9, "bold"), fg="#10B981", bg="#09090B")
        status_lbl.pack(anchor="w")

        db_lbl = tk.Label(footer, text="quiz1.db (sqlite3)", font=("Segoe UI", 9), fg="#71717A", bg="#09090B")
        db_lbl.pack(anchor="w", pady=(2, 12))

        exit_btn = tk.Button(footer, text="🚪 Exit Application", font=("Segoe UI Semibold", 10),
                             fg="#FDA4AF", bg="#09090B", activeforeground="#FFFFFF", activebackground="#E11D48",
                             relief="flat", bd=0, anchor="w", command=self.destroy)
        exit_btn.pack(fill="x")

        exit_btn.bind("<Enter>", lambda e: exit_btn.config(bg="#E11D48", fg="#FFFFFF"))
        exit_btn.bind("<Leave>", lambda e: exit_btn.config(bg="#09090B", fg="#FDA4AF"))

    def on_nav_enter(self, btn):
        for frame_name, (container, indicator, b) in self.nav_buttons.items():
            if b == btn and self.active_tab != frame_name:
                btn.config(bg="#18181B", fg="#FFFFFF")

    def on_nav_leave(self, btn):
        for frame_name, (container, indicator, b) in self.nav_buttons.items():
            if b == btn and self.active_tab != frame_name:
                btn.config(bg="#09090B", fg="#A1A1AA")

    def highlight_nav(self, frame_name):
        for key, (container, indicator, btn) in self.nav_buttons.items():
            btn.config(bg="#09090B", fg="#A1A1AA")
            indicator.config(bg="#09090B")
            container.config(bg="#09090B")

        if frame_name in self.nav_buttons:
            container, indicator, btn = self.nav_buttons[frame_name]
            btn.config(bg="#2563EB", fg="#FFFFFF")
            indicator.config(bg="#38BDF8")
            container.config(bg="#2563EB")
            self.active_tab = frame_name

    def show_frame(self, page_name):
        frame = self.frames[page_name]

        if page_name == "QuizFrame":
            self.sidebar.pack_forget()
        else:
            if not self.sidebar.winfo_manager():
                self.sidebar.pack(side="left", fill="y")

        self.highlight_nav(page_name)

        if hasattr(frame, "on_show"):
            frame.on_show()
        frame.tkraise()


class HomeDashboard(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Welcome Banner Canvas
        self.banner = tk.Canvas(self, bg="#F1F5F9", bd=0, highlightthickness=0, height=155)
        self.banner.pack(fill="x", padx=50, pady=(45, 20))

        def draw_welcome_banner(event=None):
            self.banner.delete("all")
            w = self.banner.winfo_width()
            h = self.banner.winfo_height()
            if w <= 0 or h <= 0:
                return

            # Main gradient background shape
            draw_rounded_gradient(self.banner, 0, 0, w - 3, h - 3, radius=16, color1="#0F172A", color2="#2563EB")

            # Outer border line
            draw_rounded_border(self.banner, 0, 0, w - 3, h - 3, radius=16, border_color="#E2E8F0")

            # Rings
            self.banner.create_oval(w - 240, -100, w + 100, h + 100, outline="#E2E8F0", width=1)
            self.banner.create_oval(w - 180, -60, w + 60, h + 60, outline="#E2E8F0", width=1)

            # Text
            self.banner.create_text(35, h / 2 - 18, text="Welcome to EvalPro 👋", font=("Segoe UI", 24, "bold"), fill="#FFFFFF", anchor="w")
            self.banner.create_text(35, h / 2 + 20, text="Academic Evaluation Console. Administrate question banks, view leaderboard rankings, or start quiz sessions.", font=("Segoe UI", 11), fill="#E2E8F0", anchor="w", width=w - 70)

        self.banner.bind("<Configure>", draw_welcome_banner)

        # Metrics row container
        self.metrics_container = tk.Frame(self, bg="#F1F5F9")
        self.metrics_container.pack(fill="x", padx=50, pady=(0, 20))
        self.metrics_container.columnconfigure(0, weight=1)
        self.metrics_container.columnconfigure(1, weight=1)
        self.metrics_container.columnconfigure(2, weight=1)

        self.metric_q = self.create_metric_card(self.metrics_container, "Total Bank Questions", "0", "📚", 0, "#2563EB", "#1D4ED8")
        self.metric_s = self.create_metric_card(self.metrics_container, "Submissions Recorded", "0", "📝", 1, "#10B981", "#047857")
        self.metric_a = self.create_metric_card(self.metrics_container, "System Score Average", "0%", "📈", 2, "#8B5CF6", "#6D28D9")

        # Two-Column Dashboard Overview widgets
        overview_split = tk.Frame(self, bg="#F1F5F9")
        overview_split.pack(fill="both", expand=True, padx=50, pady=(0, 45))
        overview_split.columnconfigure(0, weight=1)
        overview_split.columnconfigure(1, weight=1)
        overview_split.rowconfigure(0, weight=1)

        # Left Panel: System Status Card
        sys_outer = tk.Frame(overview_split, bg="#E2E8F0", bd=0, highlightthickness=0)
        sys_outer.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        sys_inner = tk.Frame(sys_outer, bg="#FFFFFF", bd=0, highlightthickness=1, highlightbackground="#E2E8F0")
        sys_inner.pack(fill="both", expand=True, padx=(0, 2), pady=(0, 2))
        sys_inner.config(padx=25, pady=25)

        def on_enter_sys(e):
            sys_inner.config(highlightbackground="#3B82F6")
            sys_outer.config(bg="#CBD5E1")
        def on_leave_sys(e):
            sys_inner.config(highlightbackground="#E2E8F0")
            sys_outer.config(bg="#E2E8F0")

        sys_inner.bind("<Enter>", on_enter_sys)
        sys_inner.bind("<Leave>", on_leave_sys)

        accent_left = tk.Frame(sys_inner, bg="#3B82F6", height=4)
        accent_left.pack(fill="x", side="top", pady=(0, 15))

        tk.Label(sys_inner, text="⚙️  Evaluation System Status", font=("Segoe UI", 16, "bold"), fg="#0F172A", bg="#FFFFFF").pack(anchor="w", pady=(0, 10))

        sys_details = [
            ("Registry Status", "Active", "#10B981"),
            ("Database Engine", "SQLite3 connection", "#3B82F6"),
            ("Sequential IDs", "Auto-reorder active", "#10B981"),
            ("Layout Theme", "Premium SaaS light", "#8B5CF6")
        ]

        for label, desc, color in sys_details:
            row_frame = tk.Frame(sys_inner, bg="#F8FAFC", highlightbackground="#E2E8F0", highlightthickness=1)
            row_frame.pack(fill="x", pady=5)
            tk.Label(row_frame, text=label, font=("Segoe UI Semibold", 10), fg="#334155", bg="#F8FAFC").pack(side="left", padx=12, pady=10)

            badge_frame = tk.Frame(row_frame, bg=color, padx=10, pady=4)
            badge_frame.pack(side="right", padx=12, pady=8)
            tk.Label(badge_frame, text=desc, font=("Segoe UI Bold", 8), fg="#FFFFFF", bg=color).pack()

        # Right Panel: Platform Operations Guide Card
        ops_outer = tk.Frame(overview_split, bg="#E2E8F0", bd=0, highlightthickness=0)
        ops_outer.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        ops_inner = tk.Frame(ops_outer, bg="#FFFFFF", bd=0, highlightthickness=1, highlightbackground="#E2E8F0")
        ops_inner.pack(fill="both", expand=True, padx=(0, 2), pady=(0, 2))
        ops_inner.config(padx=25, pady=25)

        def on_enter_ops(e):
            ops_inner.config(highlightbackground="#8B5CF6")
            ops_outer.config(bg="#CBD5E1")
        def on_leave_ops(e):
            ops_inner.config(highlightbackground="#E2E8F0")
            ops_outer.config(bg="#E2E8F0")

        ops_inner.bind("<Enter>", on_enter_ops)
        ops_inner.bind("<Leave>", on_leave_ops)

        accent_right = tk.Frame(ops_inner, bg="#8B5CF6", height=4)
        accent_right.pack(fill="x", side="top", pady=(0, 15))

        tk.Label(ops_inner, text="🛠️  Administrator Controls", font=("Segoe UI", 16, "bold"), fg="#0F172A", bg="#FFFFFF").pack(anchor="w", pady=(0, 10))

        ops_tips = [
            ("Database Management", "Manage Question registry database parameters directly inside the 'Question Bank' and 'Delete Question' menus."),
            ("Launch session", "Launch session controls, define candidate names, and specify test question count limit from the 'Start Quiz' interface."),
            ("Live Leaderboard", "Observe candidate standings and score averages dynamically calculated on the live Standings 'Leaderboard'.")
        ]

        for title, tip in ops_tips:
            tip_frame = tk.Frame(ops_inner, bg="#FFFFFF")
            tip_frame.pack(fill="x", pady=6, anchor="w")

            bullet = tk.Label(tip_frame, text="✦", font=("Segoe UI Bold", 12), fg="#3B82F6", bg="#FFFFFF")
            bullet.pack(side="left", anchor="n", padx=(0, 10))

            text_container = tk.Frame(tip_frame, bg="#FFFFFF")
            text_container.pack(side="left", fill="x", expand=True)

            title_lbl = tk.Label(text_container, text=title, font=("Segoe UI Semibold", 10), fg="#0F172A", bg="#FFFFFF")
            title_lbl.pack(anchor="w")

            desc_lbl = tk.Label(text_container, text=tip, font=("Segoe UI", 9), fg="#64748B", bg="#FFFFFF", justify="left", wraplength=350)
            desc_lbl.pack(anchor="w", pady=(2, 0))

    def create_metric_card(self, parent, title, value, icon, col, color1, color2):
        canvas = tk.Canvas(parent, bg="#F1F5F9", bd=0, highlightthickness=0, height=130)
        canvas.grid(row=0, column=col, sticky="nsew", padx=10)

        canvas.is_hovered = False

        def draw_card(event=None, val=value):
            canvas.delete("all")
            w = canvas.winfo_width()
            h = canvas.winfo_height()
            if w <= 0 or h <= 0:
                return

            if canvas.is_hovered:
                shadow_offset = 6
                card_offset = -2
                curr_shadow = "#CBD5E1"
                curr_border = "#FFFFFF"
            else:
                shadow_offset = 3
                card_offset = 0
                curr_shadow = "#E2E8F0"
                curr_border = "#E2E8F0"

            # Draw shadow
            draw_rounded_rect(canvas, 3 + shadow_offset + card_offset, 3 + shadow_offset + card_offset, w - 3 + card_offset, h - 3 + card_offset, radius=12, fill_color=curr_shadow)

            # Draw gradient rounded background
            draw_rounded_gradient(canvas, card_offset, card_offset, w - 3 - shadow_offset + card_offset, h - 3 - shadow_offset + card_offset, radius=12, color1=color1, color2=color2)

            # Draw borders
            draw_rounded_border(canvas, card_offset, card_offset, w - 3 - shadow_offset + card_offset, h - 3 - shadow_offset + card_offset, radius=12, border_color=curr_border)

            card_w = w - 3 - shadow_offset + card_offset
            card_h = h - 3 - shadow_offset + card_offset

            # Subtle circles on right
            canvas.create_oval(card_w - 70, card_h - 70, card_w + 30, card_h + 30, outline="#E2E8F0", width=1)
            canvas.create_oval(card_w - 100, card_h - 100, card_w + 60, card_h + 60, outline="#E2E8F0", width=1)

            # Text labels
            canvas.create_text(25 + card_offset, 30 + card_offset, text=icon, font=("Segoe UI", 26), fill="#FFFFFF", anchor="w")
            canvas.create_text(25 + card_offset, card_h - 48 + card_offset, text=title.upper(), font=("Segoe UI Bold", 8), fill="#E2E8F0", anchor="w")
            canvas.create_text(25 + card_offset, card_h - 22 + card_offset, text=val, font=("Segoe UI", 24, "bold"), fill="#FFFFFF", anchor="w")

        def on_enter(e):
            canvas.is_hovered = True
            draw_card()
        def on_leave(e):
            canvas.is_hovered = False
            draw_card()

        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)

        canvas.bind("<Configure>", lambda e: draw_card())
        canvas.update_value = lambda new_val: draw_card(val=new_val)
        return canvas

    def on_show(self):
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM questions")
            total_questions = cursor.fetchone()[0]
            self.metric_q.update_value(str(total_questions))

            cursor.execute("SELECT COUNT(*) FROM quiz_scores")
            total_scores = cursor.fetchone()[0]
            self.metric_s.update_value(str(total_scores))

            if total_scores > 0:
                cursor.execute("SELECT AVG(percentage) FROM quiz_scores")
                avg = int(cursor.fetchone()[0])
                self.metric_a.update_value(f"{avg}%")
            else:
                self.metric_a.update_value("0%")
            conn.close()
        except Exception as e:
            print(f"Failed to reload stats: {e}")


class AddQuestionFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Header banner Canvas
        self.header = tk.Canvas(self, bg="#F1F5F9", bd=0, highlightthickness=0, height=110)
        self.header.pack(fill="x", padx=40, pady=(35, 15))

        def draw_header(event=None):
            self.header.delete("all")
            w = self.header.winfo_width()
            h = self.header.winfo_height()
            if w <= 0 or h <= 0:
                return

            draw_rounded_gradient(self.header, 0, 0, w - 3, h - 3, radius=12, color1="#111827", color2="#2563EB")
            draw_rounded_border(self.header, 0, 0, w - 3, h - 3, radius=12, border_color="#E2E8F0")

            self.header.create_oval(w - 180, -60, w + 60, h + 60, outline="#FFFFFF", width=1)
            self.header.create_oval(w - 140, -30, w + 30, h + 30, outline="#FFFFFF", width=1)
            self.header.create_text(30, h / 2 - 14, text="➕  Add Question Prompt", font=("Segoe UI", 18, "bold"), fill="#FFFFFF", anchor="w")
            self.header.create_text(30, h / 2 + 18, text="Insert new academic evaluations, database questions, and answer keys directly.", font=("Segoe UI", 10), fill="#E2E8F0", anchor="w")

        self.header.bind("<Configure>", draw_header)

        # Form card using Canvas centered relative to frame
        self.card = tk.Canvas(self, bg="#F1F5F9", bd=0, highlightthickness=0)
        self.card.place(relx=0.5, rely=0.58, anchor="center", relwidth=0.78, height=560)

        self.card_inner = tk.Frame(self.card, bg="#FFFFFF")
        self.card.create_window(0, 0, window=self.card_inner, anchor="nw")

        self.card.is_hovered = False

        def draw_form_card(event=None):
            w = self.card.winfo_width()
            h = self.card.winfo_height()
            if w <= 0 or h <= 0:
                return

            self.card.delete("bg")
            if self.card.is_hovered:
                shadow_offset = 6
                card_offset = -2
                curr_shadow = "#CBD5E1"
                curr_border = "#3B82F6"
                border_w = 2
            else:
                shadow_offset = 3
                card_offset = 0
                curr_shadow = "#E2E8F0"
                curr_border = "#E2E8F0"
                border_w = 1

            # Draw Shadow & Main
            draw_rounded_rect(self.card, 3 + shadow_offset + card_offset, 3 + shadow_offset + card_offset, w - 3 + card_offset, h - 3 + card_offset, radius=14, fill_color=curr_shadow)
            draw_rounded_rect(self.card, card_offset, card_offset, w - 3 - shadow_offset + card_offset, h - 3 - shadow_offset + card_offset, radius=14, fill_color="#FFFFFF", border_color=curr_border, border_width=border_w)

            # Move inside frame and enforce horizontal expansion
            card_w = w - 3 - shadow_offset
            card_h = h - 3 - shadow_offset
            self.card.coords(1, card_offset + 35, card_offset + 25)
            self.card_inner.config(width=card_w - 70, height=card_h - 50)
            self.card_inner.grid_propagate(False)

        self.card.bind("<Configure>", draw_form_card)

        def on_enter(e):
            self.card.is_hovered = True
            draw_form_card()
        def on_leave(e):
            self.card.is_hovered = False
            draw_form_card()

        self.card.bind("<Enter>", on_enter)
        self.card.bind("<Leave>", on_leave)

        # Form content column weighting
        self.card_inner.columnconfigure(0, weight=1)
        self.card_inner.columnconfigure(1, weight=1)

        self.q_var = tk.StringVar()
        self.opt_a_var = tk.StringVar()
        self.opt_b_var = tk.StringVar()
        self.opt_c_var = tk.StringVar()
        self.opt_d_var = tk.StringVar()
        self.ans_var = tk.StringVar()

        self.create_grid_input(self.card_inner, "Type the Question", self.q_var, row_idx=0, col_idx=0, col_span=2)
        self.create_grid_input(self.card_inner, "Option A", self.opt_a_var, row_idx=1, col_idx=0)
        self.create_grid_input(self.card_inner, "Option B", self.opt_b_var, row_idx=1, col_idx=1)
        self.create_grid_input(self.card_inner, "Option C", self.opt_c_var, row_idx=2, col_idx=0)
        self.create_grid_input(self.card_inner, "Option D", self.opt_d_var, row_idx=2, col_idx=1)

        # Answer choices selector grid
        ans_lbl = tk.Label(self.card_inner, text="Correct Answer Key", font=("Segoe UI Semibold", 10), fg="#475569", bg="#FFFFFF")
        ans_lbl.grid(row=3, column=0, columnspan=2, sticky="w", padx=10, pady=(12, 6))

        sel_frame = tk.Frame(self.card_inner, bg="#FFFFFF")
        sel_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 15))
        sel_frame.columnconfigure(0, weight=1)
        sel_frame.columnconfigure(1, weight=1)

        self.ans_btns = {}
        coords = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for idx, key in enumerate(["A", "B", "C", "D"]):
            r, c = coords[idx]
            pill_canvas = tk.Canvas(sel_frame, bg="#FFFFFF", bd=0, highlightthickness=0, height=44)
            pill_canvas.grid(row=r, column=c, sticky="ew", padx=10, pady=5)

            self.ans_btns[key] = {
                "canvas": pill_canvas,
                "is_hovered": False
            }

            def bind_pill_events(k=key, canv=pill_canvas):
                canv.bind("<Configure>", lambda e: self.draw_selection_pill(k))

                def on_enter(e):
                    self.ans_btns[k]["is_hovered"] = True
                    self.draw_selection_pill(k)
                def on_leave(e):
                    self.ans_btns[k]["is_hovered"] = False
                    self.draw_selection_pill(k)
                def on_click(e):
                    self.select_option(k)

                canv.bind("<Enter>", on_enter)
                canv.bind("<Leave>", on_leave)
                canv.bind("<Button-1>", on_click)

            bind_pill_events(key, pill_canvas)

        # Submit button canvas
        self.btn_save_canvas = tk.Canvas(self.card_inner, bg="#FFFFFF", bd=0, highlightthickness=0, height=52)
        self.btn_save_canvas.grid(row=5, column=0, columnspan=2, sticky="ew", padx=10, pady=(15, 0))

        self.btn_save_canvas.is_hovered = False
        self.btn_save_canvas.is_pressed = False

        def draw_save_btn(event=None):
            self.btn_save_canvas.delete("all")
            w = self.btn_save_canvas.winfo_width()
            h = self.btn_save_canvas.winfo_height()
            if w <= 0 or h <= 0:
                return

            if self.btn_save_canvas.is_pressed:
                shadow_offset = 1
                card_offset = 2
                c1, c2 = "#1D4ED8", "#1E40AF"
                border_color = "#1D4ED8"
            elif self.btn_save_canvas.is_hovered:
                shadow_offset = 5
                card_offset = -2
                c1, c2 = "#3B82F6", "#1D4ED8"
                border_color = "#FFFFFF"
            else:
                shadow_offset = 3
                card_offset = 0
                c1, c2 = "#2563EB", "#1D4ED8"
                border_color = "#3B82F6"

            # Draw Shadow
            draw_rounded_rect(self.btn_save_canvas, 3 + shadow_offset + card_offset, 3 + shadow_offset + card_offset, w - 3 + card_offset, h - 3 + card_offset, radius=8, fill_color="#E2E8F0")
            # Draw Gradient Card
            draw_rounded_gradient(self.btn_save_canvas, card_offset, card_offset, w - 3 - shadow_offset + card_offset, h - 3 - shadow_offset + card_offset, radius=8, color1=c1, color2=c2)
            # Draw Border
            draw_rounded_border(self.btn_save_canvas, card_offset, card_offset, w - 3 - shadow_offset + card_offset, h - 3 - shadow_offset + card_offset, radius=8, border_color=border_color)

            # Draw text
            self.btn_save_canvas.create_text(w / 2, h / 2 + card_offset, text="Save Question to Registry Database →", font=("Segoe UI Bold", 11), fill="#FFFFFF")

        self.btn_save_canvas.bind("<Configure>", draw_save_btn)

        def on_save_enter(e):
            self.btn_save_canvas.is_hovered = True
            draw_save_btn()
        def on_save_leave(e):
            self.btn_save_canvas.is_hovered = False
            self.btn_save_canvas.is_pressed = False
            draw_save_btn()
        def on_save_down(e):
            self.btn_save_canvas.is_pressed = True
            draw_save_btn()
        def on_save_up(e):
            if self.btn_save_canvas.is_pressed:
                self.btn_save_canvas.is_pressed = False
                draw_save_btn()
                self.save_question()

        self.btn_save_canvas.bind("<Enter>", on_save_enter)
        self.btn_save_canvas.bind("<Leave>", on_save_leave)
        self.btn_save_canvas.bind("<Button-1>", on_save_down)
        self.btn_save_canvas.bind("<ButtonRelease-1>", on_save_up)

    def draw_selection_pill(self, key):
        pill = self.ans_btns[key]
        canvas = pill["canvas"]
        is_hovered = pill["is_hovered"]
        is_selected = (self.ans_var.get() == key)

        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w <= 0 or h <= 0:
            return

        if is_selected:
            c1, c2 = "#2563EB", "#1D4ED8"
            border_color = "#3B82F6"
            text_color = "#FFFFFF"
            shadow_offset = 3
            card_offset = -1
        elif is_hovered:
            c1, c2 = "#EFF6FF", "#EFF6FF"
            border_color = "#3B82F6"
            text_color = "#2563EB"
            shadow_offset = 2
            card_offset = -1
        else:
            c1, c2 = "#F8FAFC", "#F8FAFC"
            border_color = "#E2E8F0"
            text_color = "#475569"
            shadow_offset = 1
            card_offset = 0

        # Draw shadow
        draw_rounded_rect(canvas, 1 + shadow_offset + card_offset, 1 + shadow_offset + card_offset, w - 1 + card_offset, h - 1 + card_offset, radius=20, fill_color="#CBD5E1")
        
        # Draw main pill background
        if is_selected:
            draw_rounded_gradient(canvas, card_offset, card_offset, w - 1 - shadow_offset + card_offset, h - 1 - shadow_offset + card_offset, radius=20, color1=c1, color2=c2)
        else:
            draw_rounded_rect(canvas, card_offset, card_offset, w - 1 - shadow_offset + card_offset, h - 1 - shadow_offset + card_offset, radius=20, fill_color=c1)

        # Draw border
        draw_rounded_border(canvas, card_offset, card_offset, w - 1 - shadow_offset + card_offset, h - 1 - shadow_offset + card_offset, radius=20, border_color=border_color, border_width=1.5 if (is_selected or is_hovered) else 1)

        # Draw text
        canvas.create_text((w - 1 - shadow_offset) / 2 + card_offset, (h - 1) / 2 + card_offset, text=f"Option {key}", font=("Segoe UI Bold", 10), fill=text_color)

    def create_grid_input(self, parent, label_text, variable, row_idx, col_idx, col_span=1):
        wrapper = tk.Frame(parent, bg="#FFFFFF")
        wrapper.grid(row=row_idx, column=col_idx, columnspan=col_span, sticky="ew", padx=10, pady=8)

        tk.Label(wrapper, text=label_text, font=("Segoe UI Semibold", 10), fg="#475569", bg="#FFFFFF").pack(anchor="w", pady=(0, 5))

        border_frame = tk.Frame(wrapper, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightcolor="#3B82F6", highlightthickness=1)
        border_frame.pack(fill="x")

        entry = tk.Entry(border_frame, textvariable=variable, font=("Segoe UI", 10), bg="#FFFFFF", fg="#0F172A", bd=0, highlightthickness=0, insertbackground="#3B82F6")
        entry.pack(fill="x", padx=15, pady=12)

        entry.bind("<FocusIn>", lambda e: border_frame.config(highlightbackground="#3B82F6", highlightcolor="#3B82F6", highlightthickness=2))
        entry.bind("<FocusOut>", lambda e: border_frame.config(highlightbackground="#E2E8F0", highlightcolor="#E2E8F0", highlightthickness=1))

        border_frame.bind("<Enter>", lambda e: border_frame.config(highlightbackground="#94A3B8") if entry != parent.focus_get() else None)
        border_frame.bind("<Leave>", lambda e: border_frame.config(highlightbackground="#E2E8F0") if entry != parent.focus_get() else None)

    def select_option(self, key):
        self.ans_var.set(key)
        for k in self.ans_btns.keys():
            self.draw_selection_pill(k)

    def save_question(self):
        q = self.q_var.get().strip()
        a = self.opt_a_var.get().strip()
        b = self.opt_b_var.get().strip()
        c = self.opt_c_var.get().strip()
        d = self.opt_d_var.get().strip()
        ans = self.ans_var.get().strip()

        if not q or not a or not b or not c or not d:
            messagebox.showwarning("Form Error", "Please fill in all parameter text fields before saving.", parent=self)
            return

        if not ans:
            messagebox.showwarning("Form Error", "Please select the correct answer option key (A, B, C, or D) below the input fields.", parent=self)
            return

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO questions (question, option1, option2, option3, option4, correct_answer)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (q, a, b, c, d, ans))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Question successfully loaded into the registry database!", parent=self)

            self.q_var.set("")
            self.opt_a_var.set("")
            self.opt_b_var.set("")
            self.opt_c_var.set("")
            self.opt_d_var.set("")
            self.ans_var.set("")
            self.select_option("")
        except Exception as e:
            messagebox.showerror("Database Error", f"Operation failed: {e}", parent=self)


class ViewQuestionsFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.all_records = []

        # Header banner Canvas
        self.header = tk.Canvas(self, bg="#F1F5F9", bd=0, highlightthickness=0, height=110)
        self.header.pack(fill="x", padx=40, pady=(35, 15))

        def draw_header(event=None):
            self.header.delete("all")
            w = self.header.winfo_width()
            h = self.header.winfo_height()
            if w <= 0 or h <= 0:
                return

            draw_rounded_gradient(self.header, 0, 0, w - 3, h - 3, radius=12, color1="#1E293B", color2="#2563EB")
            draw_rounded_border(self.header, 0, 0, w - 3, h - 3, radius=12, border_color="#E2E8F0")

            self.header.create_oval(w - 180, -60, w + 60, h + 60, outline="#FFFFFF", width=1)
            self.header.create_oval(w - 140, -30, w + 30, h + 30, outline="#FFFFFF", width=1)
            self.header.create_text(30, h / 2 - 14, text="📚  Question Registry Bank", font=("Segoe UI", 18, "bold"), fill="#FFFFFF", anchor="w")
            self.header.create_text(30, h / 2 + 18, text="Search and view academic evaluation prompts stored in database tables.", font=("Segoe UI", 10), fill="#E2E8F0", anchor="w")

        self.header.bind("<Configure>", draw_header)

        # Stats row frame
        stats_frame = tk.Frame(self, bg="#F1F5F9")
        stats_frame.pack(fill="x", padx=40, pady=(0, 15))
        stats_frame.columnconfigure((0, 1, 2, 3), weight=1)

        self.stat_total_lbl = self.create_stat_card(stats_frame, "Total Questions", "0", "📊", 0, "#3B82F6")
        self.create_stat_card(stats_frame, "Database Status", "Operational", "🛡️", 1, "#10B981")
        self.create_stat_card(stats_frame, "Registry Health", "100% Secure", "⚡", 2, "#06B6D4")
        self.create_stat_card(stats_frame, "Engine Type", "SQLite 3", "⚙️", 3, "#8B5CF6")

        # Datagrid Container Card using Canvas
        self.card = tk.Canvas(self, bg="#F1F5F9", bd=0, highlightthickness=0)
        self.card.pack(fill="both", expand=True, padx=40, pady=(0, 40))

        self.card_inner = tk.Frame(self.card, bg="#FFFFFF")
        self.card.create_window(0, 0, window=self.card_inner, anchor="nw")

        self.card.is_hovered = False

        def draw_grid_card(event=None):
            w = self.card.winfo_width()
            h = self.card.winfo_height()
            if w <= 0 or h <= 0:
                return

            self.card.delete("bg")
            if self.card.is_hovered:
                shadow_offset = 6
                card_offset = -2
                curr_shadow = "#CBD5E1"
                curr_border = "#3B82F6"
                border_w = 2
            else:
                shadow_offset = 3
                card_offset = 0
                curr_shadow = "#E2E8F0"
                curr_border = "#E2E8F0"
                border_w = 1

            # Draw Shadow & Main
            draw_rounded_rect(self.card, 3 + shadow_offset + card_offset, 3 + shadow_offset + card_offset, w - 3 + card_offset, h - 3 + card_offset, radius=14, fill_color=curr_shadow)
            draw_rounded_rect(self.card, card_offset, card_offset, w - 3 - shadow_offset + card_offset, h - 3 - shadow_offset + card_offset, radius=14, fill_color="#FFFFFF", border_color=curr_border, border_width=border_w)

            # Relocate frame
            self.card.coords(1, card_offset + 20, card_offset + 20)
            self.card_inner.config(width=w - 40 - shadow_offset, height=h - 40 - shadow_offset)

        self.card.bind("<Configure>", draw_grid_card)

        def on_enter(e):
            self.card.is_hovered = True
            draw_grid_card()
        def on_leave(e):
            self.card.is_hovered = False
            draw_grid_card()

        self.card.bind("<Enter>", on_enter)
        self.card.bind("<Leave>", on_leave)

        self.card_inner.columnconfigure(0, weight=1)
        self.card_inner.rowconfigure(1, weight=1)

        # Filter action bar inside Card inner (Row 0)
        filter_bar = tk.Frame(self.card_inner, bg="#FFFFFF")
        filter_bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        search_lbl = tk.Label(filter_bar, text="🔍", font=("Segoe UI", 13), fg="#64748B", bg="#FFFFFF")
        search_lbl.pack(side="left", padx=(0, 8))

        # Search field border frame
        search_border = tk.Frame(filter_bar, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightcolor="#3B82F6", highlightthickness=1)
        search_border.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_border, textvariable=self.search_var, font=("Segoe UI", 10), bg="#FFFFFF", fg="#0F172A", bd=0, highlightthickness=0, insertbackground="#3B82F6")
        self.search_entry.pack(fill="x", padx=12, pady=10)
        self.search_var.trace_add("write", lambda *args: self.filter_questions())

        self.search_entry.bind("<FocusIn>", lambda e: search_border.config(highlightbackground="#3B82F6", highlightcolor="#3B82F6", highlightthickness=2))
        self.search_entry.bind("<FocusOut>", lambda e: search_border.config(highlightbackground="#E2E8F0", highlightcolor="#E2E8F0", highlightthickness=1))

        # Reset button
        reset_btn = tk.Button(
            filter_bar,
            text="Clear Search",
            font=("Segoe UI Semibold", 10),
            bg="#F1F5F9",
            fg="#475569",
            activebackground="#E2E8F0",
            activeforeground="#0F172A",
            relief="flat",
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.clear_filter
        )
        reset_btn.pack(side="right")
        reset_btn.bind("<Enter>", lambda e: reset_btn.config(bg="#E2E8F0"))
        reset_btn.bind("<Leave>", lambda e: reset_btn.config(bg="#F1F5F9"))

        # Scrollbar
        scroll = ttk.Scrollbar(self.card_inner, orient="vertical", style="Vertical.TScrollbar")
        scroll.grid(row=1, column=1, sticky="ns")

        # Treeview grid
        self.tree = ttk.Treeview(self.card_inner, columns=("id", "question", "opt1", "opt2", "opt3", "opt4", "correct"), show="headings", yscrollcommand=scroll.set)
        self.tree.grid(row=1, column=0, sticky="nsew")
        scroll.config(command=self.tree.yview)

        # Headers Setup
        headers = {
            "id": ("ID", 50, "center", "center"),
            "question": ("QUESTION PROMPT CONTEXT", 480, "w", "w"),
            "opt1": ("OPTION A", 140, "center", "center"),
            "opt2": ("OPTION B", 140, "center", "center"),
            "opt3": ("OPTION C", 140, "center", "center"),
            "opt4": ("OPTION D", 140, "center", "center"),
            "correct": ("KEY", 70, "center", "center")
        }

        for col, (text, width, h_anchor, r_anchor) in headers.items():
            self.tree.heading(col, text=text, anchor=h_anchor)
            self.tree.column(col, width=width, anchor=r_anchor, stretch=(col in ["question", "opt1", "opt2", "opt3", "opt4"]))

        self.tree.tag_configure('evenrow', background="#FFFFFF", foreground="#0F172A")
        self.tree.tag_configure('oddrow', background="#F8FAFC", foreground="#0F172A")
        self.tree.tag_configure('hover', background="#EFF6FF", foreground="#2563EB")

        self.tree.bind("<Motion>", self.on_tree_hover)
        self.tree.bind("<Leave>", self.on_leave_tree)

    def create_stat_card(self, parent, title, desc, icon, col, theme_color):
        card = tk.Frame(parent, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
        card.grid(row=0, column=col, sticky="nsew", padx=8, pady=5)

        accent = tk.Frame(card, bg=theme_color, height=3)
        accent.pack(fill="x")

        inner_frame = tk.Frame(card, bg="#FFFFFF", padx=16, pady=16)
        inner_frame.pack(fill="both", expand=True)

        text_frame = tk.Frame(inner_frame, bg="#FFFFFF")
        text_frame.pack(side="left", anchor="w")

        title_lbl = tk.Label(text_frame, text=title.upper(), font=("Segoe UI Bold", 8), fg="#64748B", bg="#FFFFFF")
        title_lbl.pack(anchor="w")

        desc_lbl = tk.Label(text_frame, text=desc, font=("Segoe UI Semibold", 13), fg="#0F172A", bg="#FFFFFF")
        desc_lbl.pack(anchor="w", pady=(3, 0))

        icon_lbl = tk.Label(inner_frame, text=icon, font=("Segoe UI", 20), fg=theme_color, bg="#FFFFFF")
        icon_lbl.pack(side="right", anchor="e")

        def on_enter(e):
            card.config(highlightbackground=theme_color)
        def on_leave(e):
            card.config(highlightbackground="#E2E8F0")

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        inner_frame.bind("<Enter>", on_enter)
        inner_frame.bind("<Leave>", on_leave)

        return desc_lbl

    def on_tree_hover(self, event):
        item = self.tree.identify_row(event.y)
        for child in self.tree.get_children():
            tags = list(self.tree.item(child, "tags") or [])
            if 'hover' in tags:
                tags.remove('hover')
                self.tree.item(child, tags=tuple(tags))

        if item:
            self.tree.config(cursor="hand2")
            tags = list(self.tree.item(item, "tags") or [])
            if 'hover' not in tags:
                tags.append('hover')
                self.tree.item(item, tags=tuple(tags))
        else:
            self.tree.config(cursor="")

    def on_leave_tree(self, event):
        self.tree.config(cursor="")
        for item in self.tree.get_children():
            tags = list(self.tree.item(item, "tags") or [])
            if 'hover' in tags:
                tags.remove('hover')
                self.tree.item(item, tags=tuple(tags))

    def on_show(self):
        self.search_var.set("")
        self.load_questions()

    def load_questions(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM questions")
            self.all_records = cursor.fetchall()

            self.stat_total_lbl.config(text=f"{len(self.all_records)}")

            for index, row in enumerate(self.all_records):
                tag = 'evenrow' if index % 2 == 0 else 'oddrow'
                self.tree.insert("", "end", values=row, tags=(tag,))
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve questions list: {e}", parent=self)

    def filter_questions(self):
        query = self.search_var.get().strip().lower()

        for item in self.tree.get_children():
            self.tree.delete(item)

        filtered = [row for row in self.all_records if query in str(row[1]).lower() or query in str(row[0]).lower()]

        for index, row in enumerate(filtered):
            tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=row, tags=(tag,))

    def clear_filter(self):
        self.search_var.set("")
        self.load_questions()


class DeleteQuestionFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Header banner Canvas
        self.header = tk.Canvas(self, bg="#F1F5F9", bd=0, highlightthickness=0, height=110)
        self.header.pack(fill="x", padx=40, pady=(35, 15))

        def draw_header(event=None):
            self.header.delete("all")
            w = self.header.winfo_width()
            h = self.header.winfo_height()
            if w <= 0 or h <= 0:
                return

            draw_rounded_gradient(self.header, 0, 0, w - 3, h - 3, radius=12, color1="#EF4444", color2="#9F1239")
            draw_rounded_border(self.header, 0, 0, w - 3, h - 3, radius=12, border_color="#E2E8F0")

            self.header.create_oval(w - 180, -60, w + 60, h + 60, outline="#FFFFFF", width=1)
            self.header.create_oval(w - 140, -30, w + 30, h + 30, outline="#FFFFFF", width=1)
            self.header.create_text(30, h / 2 - 14, text="🗑️  Delete Registry Question", font=("Segoe UI", 18, "bold"), fill="#FFFFFF", anchor="w")
            self.header.create_text(30, h / 2 + 18, text="Warning: Removing prompts will automatically re-index the sequence IDs sequentially.", font=("Segoe UI", 10), fill="#E2E8F0", anchor="w")

        self.header.bind("<Configure>", draw_header)

        # Danger warning alert card using Canvas for glow / shadow depth
        self.warn_banner = tk.Canvas(self, bg="#F1F5F9", bd=0, highlightthickness=0, height=72)
        self.warn_banner.pack(fill="x", padx=40, pady=(0, 15))

        def draw_warn_banner(event=None):
            self.warn_banner.delete("all")
            w = self.warn_banner.winfo_width()
            h = self.warn_banner.winfo_height()
            if w <= 0 or h <= 0:
                return

            draw_rounded_rect(self.warn_banner, 0, 0, w - 3, h - 3, radius=10, fill_color="#FFF1F2", border_color="#FCA5A5", border_width=1)
            self.warn_banner.create_text(25, h / 2, text="⚠️ DANGER ZONE: Double-check selection records before deletion. Deletion removes files, records, and tables forever.", font=("Segoe UI Semibold", 10), fill="#9F1239", anchor="w")

        self.warn_banner.bind("<Configure>", draw_warn_banner)

        # Delete Action bar frame aligned bottom-right
        action_bar = tk.Frame(self, bg="#F1F5F9")
        action_bar.pack(fill="x", padx=40, pady=(10, 40), side="bottom")

        # Create a red gradient canvas button for the Delete Question action
        self.btn_delete_canvas = tk.Canvas(action_bar, bg="#F1F5F9", bd=0, highlightthickness=0, width=420, height=52)
        self.btn_delete_canvas.pack(side="right")

        self.btn_delete_canvas.is_hovered = False
        self.btn_delete_canvas.is_pressed = False

        def draw_delete_btn(event=None):
            self.btn_delete_canvas.delete("all")
            w = self.btn_delete_canvas.winfo_width()
            h = self.btn_delete_canvas.winfo_height()
            if w <= 0 or h <= 0:
                return

            if self.btn_delete_canvas.is_pressed:
                shadow_offset = 1
                card_offset = 2
                c1, c2 = "#9F1239", "#EF4444"
                border_color = "#9F1239"
            elif self.btn_delete_canvas.is_hovered:
                shadow_offset = 6
                card_offset = -2
                c1, c2 = "#F87171", "#DC2626"
                border_color = "#FFFFFF"
            else:
                shadow_offset = 3
                card_offset = 0
                c1, c2 = "#EF4444", "#B91C1C"
                border_color = "#FCA5A5"

            # Draw Shadow
            draw_rounded_rect(self.btn_delete_canvas, 3 + shadow_offset + card_offset, 3 + shadow_offset + card_offset, w - 3 + card_offset, h - 3 + card_offset, radius=8, fill_color="#CBD5E1")
            # Draw Gradient Card
            draw_rounded_gradient(self.btn_delete_canvas, card_offset, card_offset, w - 3 - shadow_offset + card_offset, h - 3 - shadow_offset + card_offset, radius=8, color1=c1, color2=c2)
            # Draw Border
            draw_rounded_border(self.btn_delete_canvas, card_offset, card_offset, w - 3 - shadow_offset + card_offset, h - 3 - shadow_offset + card_offset, radius=8, border_color=border_color)

            # Draw text/icon
            self.btn_delete_canvas.create_text(w / 2 - 10, h / 2 - 1 + card_offset, text="🗑️  Permanently Delete Selected Evaluation Prompt", font=("Segoe UI Bold", 11), fill="#FFFFFF")

        self.btn_delete_canvas.bind("<Configure>", draw_delete_btn)

        def on_btn_enter(e):
            self.btn_delete_canvas.is_hovered = True
            draw_delete_btn()
        def on_btn_leave(e):
            self.btn_delete_canvas.is_hovered = False
            self.btn_delete_canvas.is_pressed = False
            draw_delete_btn()
        def on_btn_down(e):
            self.btn_delete_canvas.is_pressed = True
            draw_delete_btn()
        def on_btn_up(e):
            if self.btn_delete_canvas.is_pressed:
                self.btn_delete_canvas.is_pressed = False
                draw_delete_btn()
                self.delete_question()

        self.btn_delete_canvas.bind("<Enter>", on_btn_enter)
        self.btn_delete_canvas.bind("<Leave>", on_btn_leave)
        self.btn_delete_canvas.bind("<Button-1>", on_btn_down)
        self.btn_delete_canvas.bind("<ButtonRelease-1>", on_btn_up)

        # Datagrid Container Card
        card_outer = tk.Frame(self, bg="#E2E8F0", bd=0, highlightthickness=0)
        card_outer.pack(fill="both", expand=True, padx=40, pady=(0, 20), side="top")

        card_inner = tk.Frame(card_outer, bg="#FFFFFF", bd=0, highlightthickness=1, highlightbackground="#E2E8F0")
        card_inner.pack(fill="both", expand=True, padx=(0, 2), pady=(0, 2))
        card_inner.config(padx=20, pady=20)

        card_inner.columnconfigure(0, weight=1)
        card_inner.rowconfigure(0, weight=1)

        # Treeview Scrollbar
        scroll = ttk.Scrollbar(card_inner, orient="vertical", style="Vertical.TScrollbar")
        scroll.grid(row=0, column=1, sticky="ns")

        # Treeview grid
        self.tree = ttk.Treeview(card_inner, columns=("id", "question", "opt1", "opt2", "opt3", "opt4", "correct"), show="headings", yscrollcommand=scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scroll.config(command=self.tree.yview)

        # Headers Setup
        headers = {
            "id": ("ID", 50, "center", "center"),
            "question": ("QUESTION PROMPT CONTEXT", 480, "w", "w"),
            "opt1": ("OPTION A", 140, "center", "center"),
            "opt2": ("OPTION B", 140, "center", "center"),
            "opt3": ("OPTION C", 140, "center", "center"),
            "opt4": ("OPTION D", 140, "center", "center"),
            "correct": ("KEY", 70, "center", "center")
        }

        for col, (text, width, h_anchor, r_anchor) in headers.items():
            self.tree.heading(col, text=text, anchor=h_anchor)
            self.tree.column(col, width=width, anchor=r_anchor, stretch=(col in ["question", "opt1", "opt2", "opt3", "opt4"]))

        # Row tagging
        self.tree.tag_configure('evenrow', background="#FFFFFF", foreground="#0F172A")
        self.tree.tag_configure('oddrow', background="#F8FAFC", foreground="#0F172A")
        self.tree.tag_configure('hover', background="#FEF2F2", foreground="#EF4444")

        self.tree.bind("<Motion>", self.on_tree_hover)
        self.tree.bind("<Leave>", self.on_leave_tree)

    def on_tree_hover(self, event):
        item = self.tree.identify_row(event.y)
        for child in self.tree.get_children():
            tags = list(self.tree.item(child, "tags") or [])
            if 'hover' in tags:
                tags.remove('hover')
                self.tree.item(child, tags=tuple(tags))

        if item:
            self.tree.config(cursor="hand2")
            tags = list(self.tree.item(item, "tags") or [])
            if 'hover' not in tags:
                tags.append('hover')
                self.tree.item(item, tags=tuple(tags))
        else:
            self.tree.config(cursor="")

    def on_leave_tree(self, event):
        self.tree.config(cursor="")
        for item in self.tree.get_children():
            tags = list(self.tree.item(item, "tags") or [])
            if 'hover' in tags:
                tags.remove('hover')
                self.tree.item(item, tags=tuple(tags))

    def on_show(self):
        self.load_questions()

    def load_questions(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM questions")
            records = cursor.fetchall()

            for index, row in enumerate(records):
                tag = 'evenrow' if index % 2 == 0 else 'oddrow'
                self.tree.insert("", "end", values=row, tags=(tag,))
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve questions list: {e}", parent=self)

    def delete_question(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please click a row in the table to select it for deletion.", parent=self)
            return

        item_data = self.tree.item(selected[0])
        question_id = item_data['values'][0]

        confirm = messagebox.askyesno("Confirm Deletion", f"Permanently delete evaluation question ID {question_id}?", parent=self)
        if confirm:
            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM questions WHERE question_id = ?", (question_id,))

                # Reorder sequentially
                cursor.execute("SELECT question_id FROM questions ORDER BY question_id")
                remaining = cursor.fetchall()
                for new_id, row in enumerate(remaining, start=1):
                    old_id = row[0]
                    if old_id != new_id:
                        cursor.execute("UPDATE questions SET question_id = ? WHERE question_id = ?", (new_id, old_id))

                cursor.execute("DELETE FROM sqlite_sequence WHERE name='questions'")
                conn.commit()
                conn.close()

                messagebox.showinfo("Success", "Question deleted and database reordered.", parent=self)
                self.on_show()
            except Exception as e:
                messagebox.showerror("Error", f"Operation failed: {e}", parent=self)


class PreQuizFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Centered setup card using Canvas
        self.card = tk.Canvas(self, bg="#F1F5F9", bd=0, highlightthickness=0)
        self.card.place(relx=0.5, rely=0.5, anchor="center", width=520, height=500)

        self.card_inner = tk.Frame(self.card, bg="#FFFFFF")
        self.card.create_window(0, 0, window=self.card_inner, anchor="nw")

        self.card.is_hovered = False

        def draw_prequiz_card(event=None):
            w = self.card.winfo_width()
            h = self.card.winfo_height()
            if w <= 0 or h <= 0:
                return

            self.card.delete("bg")
            if self.card.is_hovered:
                shadow_offset = 6
                card_offset = -2
                curr_shadow = "#CBD5E1"
                curr_border = "#3B82F6"
                border_w = 2
            else:
                shadow_offset = 3
                card_offset = 0
                curr_shadow = "#E2E8F0"
                curr_border = "#E2E8F0"
                border_w = 1

            # Draw Shadow
            draw_rounded_rect(self.card, 3 + shadow_offset + card_offset, 3 + shadow_offset + card_offset, w - 3 + card_offset, h - 3 + card_offset, radius=14, fill_color=curr_shadow)
            # Draw Main
            draw_rounded_rect(self.card, card_offset, card_offset, w - 3 - shadow_offset + card_offset, h - 3 - shadow_offset + card_offset, radius=14, fill_color="#FFFFFF", border_color=curr_border, border_width=border_w)

            # Move inside frame
            self.card.coords(1, card_offset + 40, card_offset + 35)
            self.card_inner.config(width=w - 80 - shadow_offset)

        self.card.bind("<Configure>", draw_prequiz_card)

        def on_enter(e):
            self.card.is_hovered = True
            draw_prequiz_card()
        def on_leave(e):
            self.card.is_hovered = False
            draw_prequiz_card()

        self.card.bind("<Enter>", on_enter)
        self.card.bind("<Leave>", on_leave)

        # Content fields
        accent_strip = tk.Canvas(self.card_inner, bg="#FFFFFF", bd=0, highlightthickness=0, height=4)
        accent_strip.pack(fill="x", pady=(0, 15))

        def draw_accent_strip(event=None):
            accent_strip.delete("all")
            w = accent_strip.winfo_width()
            if w <= 0:
                return
            for i in range(w):
                r = int(59 + (6 - 59) * i / w)
                g = int(130 + (182 - 130) * i / w)
                b = int(246 + (212 - 246) * i / w)
                accent_strip.create_line(i, 0, i, 4, fill=f"#{r:02x}{g:02x}{b:02x}")
        accent_strip.bind("<Configure>", draw_accent_strip)

        tk.Label(self.card_inner, text="Start New Quiz Session", font=("Segoe UI", 18, "bold"), fg="#0F172A", bg="#FFFFFF").pack(pady=(5, 5))
        tk.Label(self.card_inner, text="Define session credentials and test parameters below.", font=("Segoe UI", 10), fg="#64748B", bg="#FFFFFF").pack(pady=(0, 25))

        self.name_var = tk.StringVar()
        self.create_premium_input_pack(self.card_inner, "Candidate Name", self.name_var, pady_val=(0, 20))

        self.num_var = tk.StringVar()
        self.create_premium_input_pack(self.card_inner, "Number of Questions", self.num_var, pady_val=(0, 35))

        # Setup buttons
        btn_frame = tk.Frame(self.card_inner, bg="#FFFFFF")
        btn_frame.pack(fill="x", padx=10)

        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            font=("Segoe UI Bold", 11),
            bg="#F1F5F9",
            fg="#475569",
            activebackground="#E2E8F0",
            activeforeground="#0F172A",
            relief="flat",
            bd=0,
            pady=12,
            cursor="hand2",
            command=lambda: controller.show_frame("HomeDashboard")
        )
        cancel_btn.pack(side="left", expand=True, fill="x", padx=(0, 8))
        cancel_btn.bind("<Enter>", lambda e: cancel_btn.config(bg="#E2E8F0"))
        cancel_btn.bind("<Leave>", lambda e: cancel_btn.config(bg="#F1F5F9"))

        start_btn = tk.Button(
            btn_frame,
            text="Start Test →",
            font=("Segoe UI Bold", 11),
            bg="#3B82F6",
            fg="#FFFFFF",
            activebackground="#2563EB",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            pady=12,
            cursor="hand2",
            command=self.start_quiz
        )
        start_btn.pack(side="right", expand=True, fill="x", padx=(8, 0))
        start_btn.bind("<Enter>", lambda e: start_btn.config(bg="#2563EB"))
        start_btn.bind("<Leave>", lambda e: start_btn.config(bg="#3B82F6"))

    def create_premium_input_pack(self, parent, label_text, variable, pady_val=(0, 20)):
        tk.Label(parent, text=label_text, font=("Segoe UI Semibold", 10), fg="#475569", bg="#FFFFFF").pack(anchor="w", padx=10, pady=(0, 6))

        border_frame = tk.Frame(parent, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightcolor="#3B82F6", highlightthickness=1)
        border_frame.pack(fill="x", padx=10, pady=pady_val)

        entry = tk.Entry(border_frame, textvariable=variable, font=("Segoe UI", 10), bg="#FFFFFF", fg="#0F172A", bd=0, highlightthickness=0, insertbackground="#3B82F6")
        entry.pack(fill="x", padx=15, pady=12)

        entry.bind("<FocusIn>", lambda e: border_frame.config(highlightbackground="#3B82F6", highlightcolor="#3B82F6", highlightthickness=2))
        entry.bind("<FocusOut>", lambda e: border_frame.config(highlightbackground="#E2E8F0", highlightcolor="#E2E8F0", highlightthickness=1))

        border_frame.bind("<Enter>", lambda e: border_frame.config(highlightbackground="#94A3B8") if entry != parent.focus_get() else None)
        border_frame.bind("<Leave>", lambda e: border_frame.config(highlightbackground="#E2E8F0") if entry != parent.focus_get() else None)

    def on_show(self):
        self.name_var.set("")
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM questions")
            self.total = cursor.fetchone()[0]
            conn.close()
            self.num_var.set(str(self.total))
        except:
            self.total = 0
            self.num_var.set("")

    def start_quiz(self):
        name = self.name_var.get().strip()
        num_str = self.num_var.get().strip()

        if not name:
            messagebox.showwarning("Input Error", "Please provide the candidate's name.", parent=self)
            return

        if not num_str.isdigit():
            messagebox.showwarning("Input Error", "Please provide a valid question count limit.", parent=self)
            return

        num = int(num_str)
        if num < 1 or num > self.total:
            messagebox.showwarning("Out of Range", f"Select question limit between 1 and {self.total}.", parent=self)
            return

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM questions")
            records = cursor.fetchall()
            conn.close()

            selected = random.sample(records, num)

            self.controller.shared_data['quiz_name'] = name
            self.controller.shared_data['quiz_questions'] = selected
            self.controller.shared_data['quiz_score'] = 0
            self.controller.shared_data['current_q_index'] = 0

            self.controller.show_frame("QuizFrame")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data: {e}", parent=self)


class QuizFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Main frame layout
        main_container = tk.Frame(self, bg="#F1F5F9")
        main_container.pack(fill="both", expand=True, padx=40, pady=30)

        # Top Header Status details
        top_panel = tk.Frame(main_container, bg="#FFFFFF", highlightbackground="#E2E8F0", highlightthickness=1)
        top_panel.pack(fill="x", pady=(0, 20), ipady=12)

        self.name_lbl = tk.Label(top_panel, text="Candidate:  -", font=("Segoe UI Semibold", 11), fg="#0F172A", bg="#FFFFFF")
        self.name_lbl.pack(side="left", padx=20, pady=(12, 0))

        self.progress_lbl = tk.Label(top_panel, text="Question 0 of 0", font=("Segoe UI Semibold", 11), fg="#475569", bg="#FFFFFF")
        self.progress_lbl.pack(side="right", padx=20, pady=(12, 0))

        # Progress bar Canvas
        self.progress_canvas = tk.Canvas(top_panel, bg="#FFFFFF", bd=0, highlightthickness=0, height=8)
        self.progress_canvas.pack(fill="x", padx=20, pady=(15, 0))

        def draw_progress_bar(event=None, ratio=0.0):
            self.progress_canvas.delete("all")
            w = self.progress_canvas.winfo_width()
            h = self.progress_canvas.winfo_height()
            if w <= 0 or h <= 0:
                return
            self.progress_canvas.create_rectangle(0, 0, w, h, fill="#F1F5F9", outline="")
            fill_w = w * ratio
            self.progress_canvas.create_rectangle(0, 0, fill_w, h, fill="#3B82F6", outline="")

        self.progress_canvas.bind("<Configure>", lambda e: draw_progress_bar())
        self.progress_canvas.update_progress = lambda ratio: draw_progress_bar(ratio=ratio)

        # Question prompt card
        q_card_outer = tk.Frame(main_container, bg="#E2E8F0", bd=0, highlightthickness=0)
        q_card_outer.pack(fill="both", expand=True, pady=(0, 20))

        q_card_inner = tk.Frame(q_card_outer, bg="#FFFFFF", bd=0, highlightthickness=1, highlightbackground="#E2E8F0")
        q_card_inner.pack(fill="both", expand=True, padx=(0, 2), pady=(0, 2))
        q_card_inner.config(padx=30, pady=30)

        self.q_text_lbl = tk.Label(q_card_inner, text="Question Prompt Context Details", font=("Segoe UI Semibold", 14), fg="#0F172A", bg="#FFFFFF", justify="left", wraplength=900)
        self.q_text_lbl.pack(anchor="w", fill="x", expand=True)

        # Options layout container
        self.opts_container = tk.Frame(main_container, bg="#F1F5F9")
        self.opts_container.pack(fill="x", pady=(0, 20))

        self.opts_container.columnconfigure(0, weight=1)
        self.opts_container.columnconfigure(1, weight=1)

        self.selected_ans = None
        self.opt_cards = {}
        coords = [(0, 0), (0, 1), (1, 0), (1, 1)]
        for idx, key in enumerate(["A", "B", "C", "D"]):
            r, c = coords[idx]

            canvas = tk.Canvas(self.opts_container, bg="#F1F5F9", bd=0, highlightthickness=0, height=85)
            canvas.grid(row=r, column=c, sticky="nsew", padx=10 if c == 0 else (0, 10), pady=(10, 0))

            self.opt_cards[key] = {
                "canvas": canvas,
                "text": f"Option {key} parameter text content",
                "is_hovered": False
            }

            def bind_events(k=key, canv=canvas):
                canv.bind("<Configure>", lambda e: self.draw_option_card(k))

                def on_enter(e):
                    self.opt_cards[k]["is_hovered"] = True
                    self.draw_option_card(k)
                def on_leave(e):
                    self.opt_cards[k]["is_hovered"] = False
                    self.draw_option_card(k)
                def on_click(e):
                    self.select_option(k)

                canv.bind("<Enter>", on_enter)
                canv.bind("<Leave>", on_leave)
                canv.bind("<Button-1>", on_click)

            bind_events(key, canvas)

        # Action layout panel
        action_panel = tk.Frame(main_container, bg="#F1F5F9")
        action_panel.pack(fill="x")

        self.prev_btn = tk.Button(
            action_panel,
            text="← Previous",
            font=("Segoe UI Bold", 11),
            bg="#FFFFFF",
            fg="#475569",
            activebackground="#E2E8F0",
            activeforeground="#0F172A",
            relief="flat",
            bd=0,
            padx=25,
            pady=12,
            cursor="hand2",
            command=self.prev_question
        )
        self.prev_btn.pack(side="left")
        self.prev_btn.bind("<Enter>", lambda e: self.prev_btn.config(bg="#E2E8F0"))
        self.prev_btn.bind("<Leave>", lambda e: self.prev_btn.config(bg="#FFFFFF"))

        self.next_btn = tk.Button(
            action_panel,
            text="Next Question →",
            font=("Segoe UI Bold", 11),
            bg="#3B82F6",
            fg="#FFFFFF",
            activebackground="#2563EB",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            padx=25,
            pady=12,
            cursor="hand2",
            command=self.next_question
        )
        self.next_btn.pack(side="right")
        self.next_btn.bind("<Enter>", lambda e: self.next_btn.config(bg="#2563EB"))
        self.next_btn.bind("<Leave>", lambda e: self.next_btn.config(bg="#3B82F6"))

    def draw_option_card(self, key):
        opt = self.opt_cards[key]
        canvas = opt["canvas"]
        text = opt["text"]
        is_hovered = opt["is_hovered"]
        is_selected = (self.selected_ans == key)

        canvas.delete("all")
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        if w <= 0 or h <= 0:
            return

        if is_selected:
            bg_color = "#EFF6FF"
            border_color = "#3B82F6"
            badge_bg = "#3B82F6"
            badge_fg = "#FFFFFF"
            text_fg = "#1E40AF"
            border_w = 2
            shadow_offset = 5
            card_offset = -1
        elif is_hovered:
            bg_color = "#F8FAFC"
            border_color = "#94A3B8"
            badge_bg = "#EFF6FF"
            badge_fg = "#3B82F6"
            text_fg = "#0F172A"
            border_w = 1.5
            shadow_offset = 4
            card_offset = -1
        else:
            bg_color = "#FFFFFF"
            border_color = "#E2E8F0"
            badge_bg = "#EFF6FF"
            badge_fg = "#3B82F6"
            text_fg = "#334155"
            border_w = 1
            shadow_offset = 2.5
            card_offset = 0

        # Draw shadow
        draw_rounded_rect(canvas, 3 + shadow_offset + card_offset, 3 + shadow_offset + card_offset, w - 3 + card_offset, h - 3 + card_offset, radius=10, fill_color="#CBD5E1")
        # Draw main card
        draw_rounded_rect(canvas, card_offset, card_offset, w - 3 - shadow_offset + card_offset, h - 3 - shadow_offset + card_offset, radius=10, fill_color=bg_color, border_color=border_color, border_width=border_w)

        card_w = w - 3 - shadow_offset + card_offset
        card_h = h - 3 - shadow_offset + card_offset

        # Draw Badge
        badge_x = 20 + card_offset
        badge_y = card_h / 2 + card_offset

        canvas.create_oval(badge_x, badge_y - 15, badge_x + 30, badge_y + 15, fill=badge_bg, outline="")
        canvas.create_text(badge_x + 15, badge_y, text=key, font=("Segoe UI Bold", 10), fill=badge_fg)

        # Draw Option Text
        canvas.create_text(badge_x + 45, badge_y, text=text, font=("Segoe UI Semibold", 10), fill=text_fg, anchor="w", width=card_w - badge_x - 65)

    def select_option(self, key):
        self.selected_ans = key
        for k in self.opt_cards.keys():
            self.draw_option_card(k)

    def on_show(self):
        self.name = self.controller.shared_data.get('quiz_name', 'Unknown')
        self.questions = self.controller.shared_data.get('quiz_questions', [])
        self.name_lbl.config(text=f"Candidate Name:  {self.name}")

        self.index = 0
        self.answers = [None] * len(self.questions)
        self.selected_ans = None

        self.load_question_index()

    def load_question_index(self):
        ratio = (self.index + 1) / len(self.questions) if len(self.questions) > 0 else 0.0
        self.progress_canvas.update_progress(ratio)

        self.progress_lbl.config(text=f"Question {self.index + 1} of {len(self.questions)}")

        q_data = self.questions[self.index]
        self.q_text_lbl.config(text=q_data[1])

        options = ["A", "B", "C", "D"]
        for idx, key in enumerate(options):
            self.opt_cards[key]["text"] = q_data[2 + idx]

        self.selected_ans = self.answers[self.index]
        for key in options:
            self.draw_option_card(key)

        if self.index == 0:
            self.prev_btn.pack_forget()
        else:
            self.prev_btn.pack(side="left")

        if self.index == len(self.questions) - 1:
            self.next_btn.config(text="Submit Exam Results ✓", bg="#10B981")
            self.next_btn.bind("<Enter>", lambda e: self.next_btn.config(bg="#059669"))
            self.next_btn.bind("<Leave>", lambda e: self.next_btn.config(bg="#10B981"))
        else:
            self.next_btn.config(text="Next Question →", bg="#3B82F6")
            self.next_btn.bind("<Enter>", lambda e: self.next_btn.config(bg="#2563EB"))
            self.next_btn.bind("<Leave>", lambda e: self.next_btn.config(bg="#3B82F6"))

    def prev_question(self):
        self.answers[self.index] = self.selected_ans
        if self.index > 0:
            self.index -= 1
            self.load_question_index()

    def next_question(self):
        if not self.selected_ans:
            messagebox.showwarning("Incomplete Answer", "Please choose an answer choice card option before proceeding.", parent=self)
            return

        self.answers[self.index] = self.selected_ans

        if self.index < len(self.questions) - 1:
            self.index += 1
            self.load_question_index()
        else:
            score = 0
            for idx, q in enumerate(self.questions):
                correct = q[6]
                if self.answers[idx] == correct:
                    score += 1

            perc = int((score / len(self.questions)) * 100)

            try:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO quiz_scores (name, total_questions, score, percentage)
                    VALUES (?, ?, ?, ?)
                """, (self.name, len(self.questions), score, perc))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"Failed to record score: {e}")

            self.controller.shared_data['quiz_score'] = score
            self.controller.shared_data['final_percentage'] = perc
            self.controller.show_frame("QuizResultFrame")


class QuizResultFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Center card container using Frame
        card_outer = tk.Frame(self, bg="#E2E8F0", bd=0, highlightthickness=0)
        card_outer.place(relx=0.5, rely=0.5, anchor="center", width=500, height=480)

        card_inner = tk.Frame(card_outer, bg="#FFFFFF", bd=0, highlightthickness=1, highlightbackground="#E2E8F0")
        card_inner.pack(fill="both", expand=True, padx=(0, 3), pady=(0, 3))
        card_inner.config(padx=40, pady=40)

        # Header Details
        tk.Label(card_inner, text="Quiz Submission Complete", font=("Segoe UI", 18, "bold"), fg="#0F172A", bg="#FFFFFF").pack(pady=(5, 5))
        self.desc_lbl = tk.Label(card_inner, text="Candidate results have been recorded to file.", font=("Segoe UI", 10), fg="#64748B", bg="#FFFFFF")
        self.desc_lbl.pack(pady=(0, 15))

        # Circular Progress ring Canvas
        self.progress_ring = tk.Canvas(card_inner, bg="#FFFFFF", bd=0, highlightthickness=0, width=150, height=150)
        self.progress_ring.pack(pady=15)

        def draw_progress_ring(event=None, val=0, color="#10B981"):
            self.progress_ring.delete("all")
            w = self.progress_ring.winfo_width()
            h = self.progress_ring.winfo_height()
            if w <= 0 or h <= 0:
                return
            x0, y0 = 15, 15
            x1, y1 = w - 15, h - 15
            self.progress_ring.create_arc(x0, y0, x1, y1, start=0, extent=359.9, outline="#E2E8F0", width=12, style="arc")
            extent_val = - (360.0 * (val / 100.0))
            self.progress_ring.create_arc(x0, y0, x1, y1, start=90, extent=extent_val, outline=color, width=12, style="arc")
            self.progress_ring.create_text(w / 2, h / 2, text=f"{val}%", font=("Segoe UI", 24, "bold"), fill=color)

        self.progress_ring.bind("<Configure>", lambda e: draw_progress_ring())
        self.progress_ring.update_value = lambda val, color: draw_progress_ring(val=val, color=color)

        self.badge_lbl = tk.Label(card_inner, text="🏆", font=("Segoe UI Semibold", 11), bg="#FFFFFF")
        self.badge_lbl.pack(pady=(0, 5))

        self.raw_lbl = tk.Label(card_inner, text="Correct: 0 of 0", font=("Segoe UI Semibold", 12), fg="#475569", bg="#FFFFFF")
        self.raw_lbl.pack(pady=(0, 25))

        return_btn = tk.Button(
            card_inner,
            text="Return to Dashboard",
            font=("Segoe UI Bold", 11),
            bg="#3B82F6",
            fg="#FFFFFF",
            activebackground="#2563EB",
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            pady=12,
            cursor="hand2",
            command=lambda: controller.show_frame("HomeDashboard")
        )
        return_btn.pack(fill="x", padx=40)
        return_btn.bind("<Enter>", lambda e: return_btn.config(bg="#2563EB"))
        return_btn.bind("<Leave>", lambda e: return_btn.config(bg="#3B82F6"))

    def on_show(self):
        score = self.controller.shared_data.get('quiz_score', 0)
        total = len(self.controller.shared_data.get('quiz_questions', []))
        perc = self.controller.shared_data.get('final_percentage', 0)

        self.raw_lbl.config(text=f"Correct Answers:  {score} out of {total}")

        if perc >= 80:
            color = "#10B981"
            self.badge_lbl.config(text="🏆 Excellent Performance!")
        elif perc >= 50:
            color = "#F59E0B"
            self.badge_lbl.config(text="✨ Good Attempt!")
        else:
            color = "#EF4444"
            self.badge_lbl.config(text="📝 Needs Improvement")

        self.progress_ring.update_value(perc, color)


class LeaderboardFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Header banner Canvas
        self.header = tk.Canvas(self, bg="#F1F5F9", bd=0, highlightthickness=0, height=110)
        self.header.pack(fill="x", padx=40, pady=(35, 15))

        def draw_header(event=None):
            self.header.delete("all")
            w = self.header.winfo_width()
            h = self.header.winfo_height()
            if w <= 0 or h <= 0:
                return

            draw_rounded_gradient(self.header, 0, 0, w - 3, h - 3, radius=12, color1="#1E293B", color2="#2563EB")
            draw_rounded_border(self.header, 0, 0, w - 3, h - 3, radius=12, border_color="#E2E8F0")

            self.header.create_oval(w - 180, -60, w + 60, h + 60, outline="#FFFFFF", width=1)
            self.header.create_oval(w - 140, -30, w + 30, h + 30, outline="#FFFFFF", width=1)
            self.header.create_text(30, h / 2 - 14, text="🏆  Leaderboard Standings", font=("Segoe UI", 18, "bold"), fill="#FFFFFF", anchor="w")
            self.header.create_text(30, h / 2 + 18, text="Top student performance rankings and evaluation scores.", font=("Segoe UI", 10), fill="#E2E8F0", anchor="w")

        self.header.bind("<Configure>", draw_header)

        # Podium frame container
        self.podium_frame = tk.Frame(self, bg="#F1F5F9")
        self.podium_frame.pack(fill="x", padx=40, pady=(0, 20))

        # Remainder standings list card
        card_outer = tk.Frame(self, bg="#E2E8F0", bd=0, highlightthickness=0)
        card_outer.pack(fill="both", expand=True, padx=40, pady=(0, 40))

        card_inner = tk.Frame(card_outer, bg="#FFFFFF", bd=0, highlightthickness=1, highlightbackground="#E2E8F0")
        card_inner.pack(fill="both", expand=True, padx=(0, 2), pady=(0, 2))
        card_inner.config(padx=20, pady=20)

        card_inner.columnconfigure(0, weight=1)
        card_inner.rowconfigure(1, weight=1)

        accent = tk.Frame(card_inner, bg="#3B82F6", height=4)
        accent.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 15))

        # Scrollbar
        scroll = ttk.Scrollbar(card_inner, orient="vertical", style="Vertical.TScrollbar")
        scroll.grid(row=1, column=1, sticky="ns")

        # Treeview
        self.tree = ttk.Treeview(card_inner, columns=("rank", "name", "score"), show="headings", yscrollcommand=scroll.set)
        self.tree.grid(row=1, column=0, sticky="nsew")
        scroll.config(command=self.tree.yview)

        headers = {
            "rank": ("RANK PLACE", 120, "center", "center"),
            "name": ("CANDIDATE NAME", 550, "w", "w"),
            "score": ("EVALUATION SCORE", 150, "center", "center")
        }

        for col, (text, width, h_anchor, r_anchor) in headers.items():
            self.tree.heading(col, text=text, anchor=h_anchor)
            self.tree.column(col, width=width, anchor=r_anchor, stretch=(col == "name"))

        self.tree.tag_configure('evenrow', background="#FFFFFF", foreground="#0F172A")
        self.tree.tag_configure('oddrow', background="#F8FAFC", foreground="#0F172A")
        self.tree.tag_configure('hover', background="#EFF6FF", foreground="#2563EB")

        self.tree.bind("<Motion>", self.on_tree_hover)
        self.tree.bind("<Leave>", self.on_leave_tree)

    def build_podium_card(self, name, score, rank_num, icon, col):
        canvas = tk.Canvas(self.podium_frame, bg="#F1F5F9", bd=0, highlightthickness=0, height=170)
        canvas.grid(row=0, column=col, sticky="nsew", padx=10)

        canvas.is_hovered = False

        # Card theme configs based on ranking place
        if rank_num == 1:
            bg_color = "#FFFBEB"
            border_color = "#F59E0B"
            score_color = "#D97706"
            label_text = "👑 Champion"
            radius = 14
        elif rank_num == 2:
            bg_color = "#EFF6FF"
            border_color = "#3B82F6"
            score_color = "#1E40AF"
            label_text = "🥈 Runner Up"
            radius = 12
        else:
            bg_color = "#F5F3FF"
            border_color = "#8B5CF6"
            score_color = "#6D28D9"
            label_text = "🥉 Third Place"
            radius = 12

        def draw_podium(event=None):
            canvas.delete("all")
            w = canvas.winfo_width()
            h = canvas.winfo_height()
            if w <= 0 or h <= 0:
                return

            if canvas.is_hovered:
                shadow_offset = 6
                card_offset = -2
                curr_shadow = "#CBD5E1"
                curr_border = border_color
                border_w = 2
            else:
                shadow_offset = 3
                card_offset = 0
                curr_shadow = "#E2E8F0"
                curr_border = border_color
                border_w = 1

            # Draw Shadow & Card bg
            draw_rounded_rect(canvas, 3 + shadow_offset + card_offset, 3 + shadow_offset + card_offset, w - 3 + card_offset, h - 3 + card_offset, radius=radius, fill_color=curr_shadow)
            draw_rounded_rect(canvas, card_offset, card_offset, w - 3 - shadow_offset + card_offset, h - 3 - shadow_offset + card_offset, radius=radius, fill_color=bg_color, border_color=curr_border, border_width=border_w)

            card_w = w - 3 - shadow_offset + card_offset
            card_h = h - 3 - shadow_offset + card_offset

            # Text drawings
            canvas.create_text(card_w / 2, 38 + card_offset, text=icon, font=("Segoe UI", 26), anchor="center")
            canvas.create_text(card_w / 2, 78 + card_offset, text=name, font=("Segoe UI Bold", 12), fill="#0F172A", anchor="center")
            canvas.create_text(card_w / 2, 108 + card_offset, text=score, font=("Segoe UI Semibold", 18), fill=score_color, anchor="center")
            canvas.create_text(card_w / 2, 138 + card_offset, text=label_text, font=("Segoe UI Semibold", 9), fill="#64748B", anchor="center")

        canvas.bind("<Configure>", draw_podium)

        def on_enter(e):
            canvas.is_hovered = True
            draw_podium()
        def on_leave(e):
            canvas.is_hovered = False
            draw_podium()

        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)

    def on_tree_hover(self, event):
        item = self.tree.identify_row(event.y)
        for child in self.tree.get_children():
            tags = list(self.tree.item(child, "tags") or [])
            if 'hover' in tags:
                tags.remove('hover')
                self.tree.item(child, tags=tuple(tags))

        if item:
            self.tree.config(cursor="hand2")
            tags = list(self.tree.item(item, "tags") or [])
            if 'hover' not in tags:
                tags.append('hover')
                self.tree.item(item, tags=tuple(tags))
        else:
            self.tree.config(cursor="")

    def on_leave_tree(self, event):
        self.tree.config(cursor="")
        for item in self.tree.get_children():
            tags = list(self.tree.item(item, "tags") or [])
            if 'hover' in tags:
                tags.remove('hover')
                self.tree.item(item, tags=tuple(tags))

    def on_show(self):
        self.podium_frame.columnconfigure((0, 1, 2), weight=1)

        for item in self.tree.get_children():
            self.tree.delete(item)

        for widget in self.podium_frame.winfo_children():
            widget.destroy()

        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, percentage
                FROM quiz_scores
                ORDER BY percentage DESC, id ASC
                LIMIT 8
            """)
            records = cursor.fetchall()
            conn.close()

            podium_data = {1: ("-", "0%", "🥈"), 2: ("-", "0%", "🥇"), 3: ("-", "0%", "🥉")}

            for idx in range(min(len(records), 3)):
                name = records[idx][0]
                score = f"{records[idx][1]}%"

                if idx == 0:
                    podium_data[2] = (name, score, "🥇")
                elif idx == 1:
                    podium_data[1] = (name, score, "🥈")
                elif idx == 2:
                    podium_data[3] = (name, score, "🥉")

            self.build_podium_card(podium_data[1][0], podium_data[1][1], 2, podium_data[1][2], 0)
            self.build_podium_card(podium_data[2][0], podium_data[2][1], 1, podium_data[2][2], 1)
            self.build_podium_card(podium_data[3][0], podium_data[3][1], 3, podium_data[3][2], 2)

            for index, row in enumerate(records):
                rank_num = index + 1
                name = row[0]
                perc = f"{row[1]}%"

                tag = 'evenrow' if rank_num % 2 == 0 else 'oddrow'
                self.tree.insert("", "end", values=(f"  #{rank_num}", name, perc), tags=(tag,))

        except Exception as e:
            print(f"Failed to load leaderboard standings: {e}")

if __name__ == "__main__":
    app = QuizApp()
    app.mainloop()
