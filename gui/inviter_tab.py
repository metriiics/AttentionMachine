from tkinter import ttk
import tkinter as tk

class InviterTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        label = ttk.Label(self, text="Inviter")
        label.pack(pady=20)
