import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier

# Color Palette
BG_DARK = "#8a7b66"
BG_LIGHT = "#D8A1CC"
ACCENT = "#0a3374"
TEXT_COLOR = "#0f111a"
SPAM_COLOR = "#cb003a"
SAFE_COLOR = "#1eb746"

class ModernSpamDetector:
    def __init__(self, root):
        self.root = root
        self.root.title("Nexus AI | Spam Sentinel")
        self.root.geometry("900x600")
        self.root.configure(bg=BG_DARK)
        
        # Database & ML Setup
        self.conn = sqlite3.connect("spam_project.db")
        self.cursor = self.conn.cursor()
        self.create_db()
        self.vectorizer = TfidfVectorizer(max_features=1000)
        self.model = self.train_initial_model()

        self.setup_styles()
        self.setup_ui()

    def create_db(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS spam_logs 
                            (id INTEGER PRIMARY KEY, content TEXT, verdict TEXT, confidence REAL)''')
        self.conn.commit()

    def train_initial_model(self):
        data = {
            'text': ['Get rich quick!', 'Hello friend', 'Winner winner', 'Meeting tomorrow', 'Click this link', 'Invoice attached'],
            'label': [1, 0, 1, 0, 1, 0]
        }
        df = pd.DataFrame(data)
        X = self.vectorizer.fit_transform(df['text'])
        rf = RandomForestClassifier(n_estimators=100)
        rf.fit(X, df['label'])
        return rf

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TProgressbar", thickness=10, troughcolor=BG_LIGHT, background=ACCENT, borderwidth=0)
        style.configure("Vertical.TScrollbar", gripcount=0, background=BG_LIGHT, troughcolor=BG_DARK, borderwidth=0)

    def setup_ui(self):
        # --- LEFT SIDEBAR (History) ---
        self.sidebar = tk.Frame(self.root, bg=BG_LIGHT, width=300)
        self.sidebar.pack_propagate(False)
        self.sidebar.pack(side="left", fill="y")
        
        tk.Label(self.sidebar, text="RECENT SCANS", bg=BG_LIGHT, fg=ACCENT, font=("Segoe UI", 10, "bold")).pack(pady=20)
        
        self.history_list = tk.Listbox(self.sidebar, bg=BG_LIGHT, fg=TEXT_COLOR, bd=0, highlightthickness=0, font=("Segoe UI", 9))
        self.history_list.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh_history()

        # --- MAIN CONTENT AREA ---
        self.main_container = tk.Frame(self.root, bg=BG_DARK)
        self.main_container.pack(side="right", fill="both", expand=True, padx=40)

        # Header
        header = tk.Label(self.main_container, text="SPAM EMAIL DETECTION SYSTEM", bg=BG_DARK, fg="white", font=("Segoe UI", 24, "bold"))
        header.pack(pady=(40, 5))
        
        subheader = tk.Label(self.main_container, text="Enterprise-grade email security scanner", bg=BG_DARK, fg="#6c7086", font=("Segoe UI", 10))
        subheader.pack(pady=(0, 30))

        # Text Input Area
        input_frame = tk.Frame(self.main_container, bg=BG_LIGHT, padx=15, pady=15)
        input_frame.pack(fill="x")

        tk.Label(input_frame, text="PASTE MESSAGE CONTENT", bg=BG_LIGHT, fg=TEXT_COLOR, font=("Segoe UI", 8, "bold")).pack(anchor="w")
        self.text_input = tk.Text(input_frame, height=10, bg=BG_DARK, fg="white", insertbackground="white", bd=0, font=("Consolas", 11))
        self.text_input.pack(fill="x", pady=10)

        # Action Button
        self.btn_analyze = tk.Button(self.main_container, text="RUN ANALYSIS", command=self.analyze, 
                                     bg=ACCENT, fg=BG_DARK, font=("Segoe UI", 10, "bold"), 
                                     activebackground="#b4befe", bd=0, cursor="hand2", pady=10)
        self.btn_analyze.pack(fill="x", pady=20)

        # Results Panel
        self.results_frame = tk.Frame(self.main_container, bg=BG_DARK)
        self.results_frame.pack(fill="x")

        self.verdict_label = tk.Label(self.results_frame, text="WAITING FOR INPUT...", bg=BG_DARK, fg="#6c7086", font=("Segoe UI", 14, "bold"))
        self.verdict_label.pack()

        self.prob_bar = ttk.Progressbar(self.results_frame, length=400, mode='determinate')
        self.prob_bar.pack(pady=15)

    def analyze(self):
        content = self.text_input.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Empty Input", "Please provide email content to analyze.")
            return

        # ML Logic
        vec = self.vectorizer.transform([content])
        pred = self.model.predict(vec)[0]
        prob = self.model.predict_proba(vec)[0][1] * 100

        # UI Response
        if pred == 1:
            res_text, res_color = "THREAT DETECTED: SPAM", SPAM_COLOR
        else:
            res_text, res_color = "SYSTEM SECURE: HAM", SAFE_COLOR

        self.verdict_label.config(text=res_text, fg=res_color)
        self.animate_progress(prob)
        
        # Data persistence
        self.cursor.execute("INSERT INTO spam_logs (content, verdict, confidence) VALUES (?, ?, ?)", 
                            (content[:50], res_text, prob))
        self.conn.commit()
        self.refresh_history()

    def animate_progress(self, target):
        """Creates a smooth filling effect for the progress bar"""
        current = 0
        def step():
            nonlocal current
            if current <= target:
                self.prob_bar['value'] = current
                current += 2
                self.root.after(10, step)
        step()

    def refresh_history(self):
        self.history_list.delete(0, tk.END)
        self.cursor.execute("SELECT verdict, content FROM spam_logs ORDER BY id DESC LIMIT 15")
        for row in self.cursor.fetchall():
            self.history_list.insert(tk.END, f"• {row[0]}: {row[1]}...")

if __name__ == "__main__":
    window = tk.Tk()
    app = ModernSpamDetector(window)
    
    def shutdown():
        app.conn.close()
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", shutdown)
    window.mainloop()