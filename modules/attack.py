import tkinter as tk
from tkinter import ttk

class AttackModule(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=True)
        ttk.Label(self, text="Moduł Ataku (W Budowie)", font=('Arial', 20)).pack(pady=50)
