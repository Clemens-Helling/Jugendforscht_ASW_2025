import tkinter as tk
from tkinter import ttk

def toggle_textfield(*args):
    """Funktion, die ausgeführt wird, wenn sich der Zustand der Checkbox ändert."""
    if checkbox_state.get():
        textfield.grid(row=4, column=0, padx=10, pady=10)  # Zeigt das Textfeld an
    else:
        textfield.grid_remove()  # Versteckt das Textfeld

root = tk.Tk()
root.title("Notifer Base")
root.geometry("800x600")

# Erstellen Sie ein Frame-Widget
frame = tk.Frame(root)
frame.place(relx=0.5, rely=0.5, anchor='center')

Titele = ttk.Label(frame, text="Notifer Base", font=("Arial", 20))
Titele.grid(row=0, column=0, columnspan=2, padx=10, pady=10)



Erkrankung = ttk.Combobox(frame, text= "Symptome", values=["Bauchschmerzen", "Kopfschmerzen", "Akutes Abdomen",
"Intox","tee","Wärmflasche","ACS","Atemnot","Fraktur", "Sportverletzung","Synkope","Panikatake" , "Anaphilaktischer Schock"])
Erkrankung.set("Wählen Sie eine Krankheit")  # Setzt den Standardwert
Erkrankung.grid(row=1, column=0, padx=10, pady=10)

unklare_lage_chackbox =ttk.Checkbutton(frame, text="Unklare Lage")
unklare_lage_chackbox.grid(row=2, column=0, padx=10, pady=10)



# Erstellen Sie eine IntVar, um den Zustand der Checkbox zu verfolgen
checkbox_state = tk.IntVar()

# Erstellen Sie die Checkbox
checkbox = ttk.Checkbutton(frame, text="Sonstige", variable=checkbox_state)
checkbox.grid(row=3, column=0, padx=10, pady=10)

# Erstellen Sie das Textfeld, aber zeigen Sie es zunächst nicht an
textfield = ttk.Entry(frame, text = "Einsatzstichwort")
# textfield.grid(row=5, column=0, padx=10, pady=10)  # Kommentiert aus, um das Textfeld zunächst zu verstecken

# Rufen Sie die Funktion toggle_textfield auf, wenn sich der Zustand der Checkbox ändert
checkbox_state.trace('w', toggle_textfield)



Alarm = tk.Button(frame, text="Alarmieren", command=lambda: print(Erkrankung.get()), font=("Arial", 20), bg="red", fg="white")
Alarm.grid(row=5, column=0, padx=10, pady=10)

root.mainloop()
