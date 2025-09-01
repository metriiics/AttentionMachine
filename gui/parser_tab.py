from tkinter import ttk
import tkinter as tk
from datetime import datetime
from core.accounts import AccountManager
from core.parser import Parser, HistoryManager
from tkinter import messagebox
import os

class CustomSelector(ttk.Frame):
    def __init__(self, parent, options, callback=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.options = options
        self.index = 0
        self.callback = callback

        self.label = ttk.Label(self, text=self.options[self.index], width=15, anchor="center")
        self.label.pack(side="left", padx=(0,2))

        self.button = ttk.Button(self, text=">", width=2, command=self.next_option)
        self.button.pack(side="left")

    def next_option(self):
        self.index = (self.index + 1) % len(self.options)
        self.label.config(text=self.options[self.index])
        if self.callback:
            self.callback(self.options[self.index])

    def get(self):
        return self.options[self.index]

def create_rounded_frame(parent, width, height, radius=15, bg="#f0f0f0"):
    canvas = tk.Canvas(parent, width=width, height=height, bg=bg, highlightthickness=0)
    canvas.pack(pady=10, fill="x")

    x0, y0, x1, y1 = 2, 2, width-2, height-2
    canvas.create_arc(x0, y0, x0+radius*2, y0+radius*2, start=90, extent=90, fill=bg, outline=bg)
    canvas.create_arc(x1-radius*2, y0, x1, y0+radius*2, start=0, extent=90, fill=bg, outline=bg)
    canvas.create_arc(x0, y1-radius*2, x0+radius*2, y1, start=180, extent=90, fill=bg, outline=bg)
    canvas.create_arc(x1-radius*2, y1-radius*2, x1, y1, start=270, extent=90, fill=bg, outline=bg)
    canvas.create_rectangle(x0+radius, y0, x1-radius, y1, fill=bg, outline=bg)
    canvas.create_rectangle(x0, y0+radius, x1, y1-radius, fill=bg, outline=bg)

    frame = tk.Frame(canvas, bg=bg)
    frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    return frame

class ParserTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.manager = AccountManager()
        self.history_manager = HistoryManager()

        ttk.Label(self, text="Парсинг", font=("Arial", 14, "bold")).pack(pady=10)

        # --- Карточка парсинга ---
        parsing_card = create_rounded_frame(self, width=800, height=180, radius=15, bg="#e0f7fa")
        top_panel = tk.Frame(parsing_card, bg="#e0f7fa")
        top_panel.pack(fill="x", pady=5)

        self.parse_selector = CustomSelector(top_panel, ["Канал", "Группа", "МультиПарсинг"], callback=self.on_parse_type_change)
        self.parse_selector.pack(side="left", padx=5)

        limit_frame = tk.Frame(top_panel, bg="#e0f7fa")
        limit_frame.pack(side="left", padx=20)
        ttk.Label(limit_frame, text="Лимит:", background="#e0f7fa").pack(anchor="w")
        self.limit_entry = ttk.Entry(limit_frame, width=10)
        self.limit_entry.pack(anchor="w", pady=2)

        account_frame = tk.Frame(top_panel, bg="#e0f7fa")
        account_frame.pack(side="right", padx=5)
        ttk.Label(account_frame, text="Аккаунт:", background="#e0f7fa").pack(side="left")
        accounts = self.manager.get_accounts()["name"].tolist()
        self.account_combo = ttk.Combobox(account_frame, values=accounts, state="readonly", width=15)
        self.account_combo.pack(side="left")
        if accounts:
            self.account_combo.current(0)

        self.input_frame = tk.Frame(parsing_card, bg="#e0f7fa")
        self.input_frame.pack(fill="x", pady=5)
        self.single_label = ttk.Label(self.input_frame, text="Ссылка на канал:", background="#e0f7fa")
        self.single_label.pack(anchor="w", pady=2)
        self.channel_entry = ttk.Entry(self.input_frame, width=50)
        self.channel_entry.pack(anchor="w", pady=2)

        self.multi_button = ttk.Button(self.input_frame, text="Добавить ссылки", command=self.open_multi_window)
        self.multi_button.pack(anchor="w", pady=2)
        self.multi_button.pack_forget()

        ttk.Button(parsing_card, text="Начать парсинг", command=self.start_parsing).pack(anchor="w", pady=5)

        # --- История ---
        ttk.Label(self, text="История", font=("Arial", 14, "bold")).pack(pady=10)
        history_card = create_rounded_frame(self, width=800, height=250, radius=15, bg="#fff3e0")

        self.history_tree = ttk.Treeview(history_card, columns=("id","name","quantity","type","time","source"), show="headings")
        self.history_tree.heading("id", text="№")
        self.history_tree.heading("name", text="Имя")
        self.history_tree.heading("quantity", text="Количество")
        self.history_tree.heading("type", text="Тип")
        self.history_tree.heading("time", text="Время")
        self.history_tree.heading("source", text="Источник")

        self.history_tree.column("id", width=40, minwidth=40, stretch=False)      
        self.history_tree.column("name", width=200, minwidth=200, stretch=False)
        self.history_tree.column("quantity", width=120, minwidth=120, stretch=False)
        self.history_tree.column("type", width=150, minwidth=100, stretch=False)
        self.history_tree.column("time", width=200, minwidth=80, stretch=False)
        self.history_tree.column("source", width=300, minwidth=250, stretch=False)

        self.history_tree.pack(expand=True, fill="both", pady=5)

        self.history_tree.bind("<Double-1>", self.open_participants_window)

        self.multi_links = []
        self.refresh_history()

    def on_parse_type_change(self, selected_type):
        if selected_type == "МультиПарсинг":
            self.channel_entry.pack_forget()
            self.single_label.pack_forget()
            self.multi_button.pack(anchor="w", pady=2)
        else:
            self.multi_button.pack_forget()
            self.single_label.pack(anchor="w", pady=2)
            self.channel_entry.pack(anchor="w", pady=2)

    def open_multi_window(self):
        multi_window = tk.Toplevel(self)
        multi_window.title("Добавить несколько ссылок")
        multi_window.geometry("400x300")
        multi_window.grab_set()
        multi_window.transient(self)

        tk.Label(multi_window, text="Введите ссылки (по одной в строке):").pack(pady=5)
        text_area = tk.Text(multi_window, width=50, height=10)
        text_area.pack(pady=5, padx=5)

        def save_links():
            self.multi_links = text_area.get("1.0", "end").strip().split("\n")
            multi_window.destroy()

        ttk.Button(multi_window, text="Сохранить", command=save_links).pack(pady=10)

    def start_parsing(self):
        parse_type = self.parse_selector.get()
        sources = self.multi_links if parse_type == "МультиПарсинг" else [self.channel_entry.get()]
        limit = self.limit_entry.get()
        account_name = self.account_combo.get()
        row = self.manager.get_accounts().query("name == @account_name").iloc[0]
        parser = Parser(row)
        now = datetime.now().strftime("%H:%M:%S")

        for s in sources:
            if s:
                try:
                    participants = parser.parse_group(s, limit, parse_type=parse_type, time=now)
                    self.refresh_history()
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Ошибка парсинга: {e}")

    def refresh_history(self):
        for row in self.history_tree.get_children():
            self.history_tree.delete(row)
        import pandas as pd
        if not os.path.exists("data/history.csv"):
            return
        df = pd.read_csv("data/history.csv")
        for _, row in df.iterrows():
            self.history_tree.insert("", "end", values=(row["id"], row["name"], row["quantity"], row["type"], row["time"], row["source"]))

    def open_participants_window(self, event):
        selected_item = self.history_tree.selection()
        if not selected_item:
            return
        item = self.history_tree.item(selected_item)
        history_id = item["values"][0]

        participants_window = tk.Toplevel(self)
        participants_window.title(f"Участники записи #{history_id}")
        participants_window.geometry("400x400")
        participants_window.grab_set()
        participants_window.transient(self)

        tree = ttk.Treeview(participants_window, columns=("user_id","username","first_name"), show="headings")
        tree.heading("user_id", text="ID")
        tree.heading("username", text="Username")
        tree.heading("first_name", text="Имя")
        tree.pack(expand=True, fill="both", pady=5)

        import pandas as pd
        df = pd.read_csv("data/participants.csv")
        df = df.query("history_id == @history_id")
        for _, row in df.iterrows():
            tree.insert("", "end", values=(row["user_id"], row["username"], row["first_name"]))
