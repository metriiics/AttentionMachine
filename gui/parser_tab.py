from tkinter import ttk
import tkinter as tk
from datetime import datetime

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
    # просто используем фиксированный bg, не parent["bg"]
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

        ttk.Label(self, text="Парсинг", font=("Arial", 14, "bold")).pack(pady=10)

        # --- карточка для парсинга ---
        parsing_card = create_rounded_frame(self, width=800, height=180, radius=15, bg="#e0f7fa")

        # --- Верхняя панель: тип парсинга + лимит + аккаунт ---
        top_panel = tk.Frame(parsing_card, bg="#e0f7fa")
        top_panel.pack(fill="x", pady=5)

        self.parse_selector = CustomSelector(top_panel, ["Канал", "Группа", "МультиПарсинг"], callback=self.on_parse_type_change)
        self.parse_selector.pack(side="left", padx=5)

        # Лимит
        limit_frame = tk.Frame(top_panel, bg="#e0f7fa")
        limit_frame.pack(side="left", padx=20)
        ttk.Label(limit_frame, text="Лимит:", background="#e0f7fa").pack(anchor="w")
        self.limit_entry = ttk.Entry(limit_frame, width=10)
        self.limit_entry.pack(anchor="w", pady=2)

        # Аккаунт
        account_frame = tk.Frame(top_panel, bg="#e0f7fa")
        account_frame.pack(side="right", padx=5)
        ttk.Label(account_frame, text="Аккаунт:", background="#e0f7fa").pack(side="left")
        self.account_combo = ttk.Combobox(account_frame, values=["Аккаунт1", "Аккаунт2", "Аккаунт3"], state="readonly", width=15)
        self.account_combo.pack(side="left")
        self.account_combo.current(0)

        # --- Поле ссылки или мультиссылок ---
        self.input_frame = tk.Frame(parsing_card, bg="#e0f7fa")
        self.input_frame.pack(fill="x", pady=5)

        self.single_label = ttk.Label(self.input_frame, text="Ссылка на канал:", background="#e0f7fa")
        self.single_label.pack(anchor="w", pady=2)
        self.channel_entry = ttk.Entry(self.input_frame, width=50)
        self.channel_entry.pack(anchor="w", pady=2)

        self.multi_button = ttk.Button(self.input_frame, text="Добавить ссылки", command=self.open_multi_window)
        self.multi_button.pack(anchor="w", pady=2)
        self.multi_button.pack_forget()

        # --- кнопка запуска ---
        ttk.Button(parsing_card, text="Начать парсинг", command=self.start_parsing).pack(anchor="w", pady=5)

        # --- История ---
        ttk.Label(self, text="История", font=("Arial", 14, "bold")).pack(pady=10)
        history_card = create_rounded_frame(self, width=800, height=250, radius=15, bg="#fff3e0")

        self.history_tree = ttk.Treeview(history_card, columns=("time", "type", "source", "limit", "account"), show="headings")
        self.history_tree.heading("time", text="Время")
        self.history_tree.heading("type", text="Тип")
        self.history_tree.heading("source", text="Источник")
        self.history_tree.heading("limit", text="Лимит")
        self.history_tree.heading("account", text="Аккаунт")
        self.history_tree.pack(expand=True, fill="both", pady=5)

        self.multi_links = []

    # --- обработка смены режима ---
    def on_parse_type_change(self, selected_type):
        if selected_type == "МультиПарсинг":
            self.channel_entry.pack_forget()
            self.single_label.pack_forget()
            self.multi_button.pack(anchor="w", pady=2)
        else:
            self.multi_button.pack_forget()
            self.single_label.pack(anchor="w", pady=2)
            self.channel_entry.pack(anchor="w", pady=2)

    # --- окно мультиссылок ---
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

    # --- запуск парсинга ---
    def start_parsing(self):
        parse_type = self.parse_selector.get()
        sources = self.multi_links if parse_type == "МультиПарсинг" else [self.channel_entry.get()]
        limit = self.limit_entry.get()
        account = self.account_combo.get()
        now = datetime.now().strftime("%H:%M:%S")
        for s in sources:
            if s:
                self.history_tree.insert("", "end", values=(now, parse_type, s, limit, account))
