from tkinter import ttk
import tkinter as tk
from core.accounts import AccountManager
from core.inviter import Inviter
from tkinter import messagebox

class InviterTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.manager = AccountManager()
        
        ttk.Label(self, text="Инвайтер", font=("Arial", 14, "bold")).pack(pady=10)

        # Выбор аккаунта
        account_frame = tk.Frame(self)
        account_frame.pack(pady=5)
        ttk.Label(account_frame, text="Аккаунт:").pack(side="left")
        accounts = self.manager.get_accounts()["name"].tolist()
        self.account_combo = ttk.Combobox(account_frame, values=accounts, state="readonly", width=20)
        self.account_combo.pack(side="left")
        if accounts:
            self.account_combo.current(0)

        # Выбор записи из истории
        history_frame = tk.Frame(self)
        history_frame.pack(pady=5)
        ttk.Label(history_frame, text="Выбрать историю:").pack(side="left")
        self.history_combo = ttk.Combobox(history_frame, state="readonly", width=40)
        self.history_combo.pack(side="left")
        self.load_history_records()

        # Ссылка на группу
        group_frame = tk.Frame(self)
        group_frame.pack(pady=5)
        ttk.Label(group_frame, text="Ссылка на группу:").pack(side="left")
        self.group_entry = ttk.Entry(group_frame, width=40)
        self.group_entry.pack(side="left")

        # Лимит
        limit_frame = tk.Frame(self)
        limit_frame.pack(pady=5)
        ttk.Label(limit_frame, text="Лимит:").pack(side="left")
        self.limit_entry = ttk.Entry(limit_frame, width=10)
        self.limit_entry.pack(side="left")

        # Кнопка запуска
        ttk.Button(self, text="Пригласить участников", command=self.start_invite).pack(pady=10)

    def load_history_records(self):
        records = Inviter.get_history_records()
        self.history_map = {f"#{r['id']} | {r['name']} | {r['time']}": r['id'] for r in records}
        self.history_combo['values'] = list(self.history_map.keys())
        if records:
            self.history_combo.current(0)

    def start_invite(self):
        account_name = self.account_combo.get()
        row = self.manager.get_accounts().query("name == @account_name").iloc[0]
        inviter = Inviter(row)

        group_link = self.group_entry.get()
        limit = self.limit_entry.get()

        history_key = self.history_combo.get()
        if not history_key:
            messagebox.showerror("Ошибка", "Выберите запись истории")
            return
        history_id = self.history_map[history_key]

        try:
            count = inviter.invite(group_link, history_id, limit)
            messagebox.showinfo("Готово", f"Приглашено участников: {count}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка инвайта: {e}")
