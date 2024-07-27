import tkinter as tk
from tkinter import ttk
from main import frameS
error_label = None
def show_error(message):
        global error_label
        if error_label is None:
            error_label = tk.Label(frame, text=message, font=("Arial", 20), fg="red")
            error_label.grid(row=6, column=0, padx=10, pady=10)