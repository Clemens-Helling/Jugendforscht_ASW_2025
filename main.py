import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("DiLer Medic")
root.geometry("800x600")

# Erstellen Sie ein Frame-Widget
frame = tk.Frame(root)
frame.place(relx=0.5, rely=0.5, anchor='center')

Titele = ttk.Label(frame, text="DiLer Medic", font=("Arial", 20))
Titele.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

Erkrankung_label = tk.Label(frame, text="Symptome")
Erkrankung_label.grid(row=1, column=0, padx=10, pady=10)

Erkrankung = ttk.Combobox(frame, text= "Symptome", values=["Herzinfarkt", "Schlaganfall", "Kreislaufstillstand"])
Erkrankung.set("Wählen Sie eine Krankheit")  # Setzt den Standardwert
Erkrankung.grid(row=1, column=0, padx=10, pady=10)

name_label = ttk.Label(frame, text="Name")
name_label.grid(row=2, column=0, padx=10, pady=10)

name = ttk.Entry(frame, text= "Name")
name.insert(0,"Name")  # Fügt den Text "Name" am Anfang des Entry-Widgets ein
name.grid(row=2, column=0, padx=10, pady=10)

Alarm = tk.Button(frame, text="Alarmieren", command=lambda: print(Erkrankung.get()))
Alarm.grid(row=3, column=0, padx=10, pady=10)

root.mainloop()