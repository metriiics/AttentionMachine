from tkinter import ttk
import tkinter as tk

class SenderTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        label = ttk.Label(self, text="Sender")
        label.pack(pady=20)
