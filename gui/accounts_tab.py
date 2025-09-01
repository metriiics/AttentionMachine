from tkinter import ttk, filedialog, messagebox
import core.accounts as acc
import tkinter as tk
import os


class AccountsTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.manager = acc.AccountManager()

        self.label = ttk.Label(self, text="Аккаунты")
        self.label.pack(pady=20)
        
        frame = ttk.Frame(self)
        frame.pack(pady=5)

        ttk.Button(frame, text="Добавить", command=self.open_add_window).grid(row=0, column=1, padx=5)
        ttk.Button(frame, text="Чекер", command=self.check_all_accounts).grid(row=0, column=5, padx=10)
        ttk.Button(frame, text="Обновить", command=self.refresh_tree).grid(row=0, column=0, padx=10)

        self.tree = ttk.Treeview(self, columns=("name", "path", "status"), show="headings")
        self.tree.heading("name", text="Имя")
        self.tree.heading("path", text="Путь")
        self.tree.heading("status", text="Статус")
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        self.refresh_tree()

    def refresh_tree(self):
        """Обновляем Treeview из CSV"""
        for row in self.tree.get_children():
            self.tree.delete(row)
        df = self.manager.get_accounts()
        for _, row in df.iterrows():
            self.tree.insert("", "end", values=(row["name"], row["path"], row["status"]))
    
    def open_add_window(self):
        parent = self.winfo_toplevel()

        add_window = tk.Toplevel(parent)
        add_window.title("Добавить аккаунт")
        add_window.resizable(False, False)
        add_window.transient(parent)
        add_window.grab_set()

        w, h = 400, 220
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        x = parent_x + (parent_w - w) // 2
        y = parent_y + (parent_h - h) // 2
        add_window.geometry(f"{w}x{h}+{x}+{y}")

        path_var = tk.StringVar()
        path_entry = ttk.Entry(add_window, textvariable=path_var, width=40)
        path_entry.pack(pady=10, padx=20)

        def browse_json():
            file = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
            if file:
                path_var.set(file)

        def browse_tdata():
            folder = filedialog.askdirectory()
            if folder:
                path_var.set(folder)

        ttk.Button(add_window, text="Выбрать JSON (.json + .session)", command=browse_json).pack(pady=5)
        ttk.Button(add_window, text="Выбрать TData (папка)", command=browse_tdata).pack(pady=5)

        def save_account():
            if not path_var.get():
                messagebox.showwarning("Ошибка", "Выберите файл или папку")
                return
            self.manager.add_account(path_var.get())
            self.refresh_tree()
            add_window.destroy()

        ttk.Button(add_window, text="Сохранить", command=save_account).pack(pady=10)
        add_window.wait_window()

    def check_all_accounts(self):
        """Проверка всех аккаунтов и обновление статусов в Treeview"""
        for i in range(len(self.manager.get_accounts())):
            self.manager.check_account(i)
        self.refresh_tree()
        messagebox.showinfo("Готово", "Проверка аккаунтов завершена")
