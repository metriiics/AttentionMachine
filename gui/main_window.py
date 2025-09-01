import tkinter as tk
from tkinter import ttk
from gui.accounts_tab import AccountsTab
from gui.inviter_tab import InviterTab
from gui.parser_tab import ParserTab
from gui.sender_tab import SenderTab

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AttractionMachine")
        self.geometry("1000x700")
        self.resizable(False, False)

        self.style = ttk.Style()
        self.style.configure("TNotebook.Tab", font=("Arial", 14, "bold"), padding=[20, 10]) 
        self.style.map("TNotebook.Tab", foreground=[("selected", "lightblue")])

        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both")

        self.accounts_tab = AccountsTab(notebook)
        self.inviter_tab = InviterTab(notebook)
        self.parser_tab = ParserTab(notebook)
        self.sender_tab = SenderTab(notebook)

        notebook.add(self.parser_tab, text="Парсинг")
        notebook.add(self.sender_tab, text="Рассылка")
        notebook.add(self.inviter_tab, text="Инвайтер")
        notebook.add(self.accounts_tab, text="Аккаунты")