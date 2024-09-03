import tkinter as tk
from tkinter import ttk
from Alarm import alarm, error
class AlarmApp:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root)
        self.frame.pack()

        self.unklare_lage_chackbox_state = tk.IntVar()
        self.sonstiges_state = tk.IntVar()
        self.frame.place(relx=0.5, rely=0.5, anchor='center')
        self.create_widgets()
        
    def create_widgets(self):
        self.Titele = ttk.Label(self.frame, text="Notifer Base", font=("Arial", 20))
        self.Titele.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        self.Erkrankung = ttk.Combobox(self.frame, text= "Symptome", values=["Bauchschmerzen", "Kopfschmerzen", "Akutes Abdomen",
        "Intox","tee","Wärmflasche","ACS","Atemnot","Fraktur", "Sportverletzung","Synkope","Panikatake" , "Anaphilaktischer Schock"])

 
        self.Erkrankung.set("Wählen Sie eine Krankheit")  # Setzt den Standardwert
        self.Erkrankung.grid(row=2, column=0, padx=10, pady=10)
        # Erstellen der Checkbox für "Unklare Lage"
        self.unklare_lage_chackbox = ttk.Checkbutton(self.frame, text="Unklare Lage", variable=self.unklare_lage_chackbox_state)
        self.unklare_lage_chackbox.grid(row=3, column=0, padx=10, pady=10)

        # Erstellen der Checkbox für "Sonstige"
        self.checkbox = ttk.Checkbutton(self.frame, text="Sonstige", variable=self.sonstiges_state)
        self.checkbox.grid(row=4, column=0, padx=10, pady=10)

        # Erstellen des Textfelds, aber zunächst nicht anzeigen
        self.textfield = ttk.Entry(self.frame)
        # self.textfield.grid(row=3, column=0, padx=10, pady=10)  # Kommentiert aus, um das Textfeld zunächst zu verstecken

        # Rufen Sie die Funktion toggle_textfield auf, wenn sich der Zustand der Checkbox ändert
        self.sonstiges_state.trace('w', self.toggle_textfield)

        # Erstellen des Labels für Fehlermeldungen
        self.error_label = tk.Label(self.frame, text="Error:", font=("Arial", 20), fg="red")
        self.error_label.grid(row=0, column=0, padx=10, pady=10)
        self.error_label.grid_remove()

        # Erstellen des Buttons zum Auslösen des Alarms
        self.button = tk.Button(self.frame, text="Alarmieren", command = self.get_alarm, font=("Arial", 20), bg="red", fg="white")
        self.button.grid(row=6, column=0, padx=10, pady=10)

    def toggle_textfield(self, *args):
        if self.sonstiges_state.get():
            self.textfield.grid(row=5, column=0, padx=10, pady=10)  # Zeigt das Textfeld an
        else:
            self.textfield.grid_remove()  # Versteckt das Textfeld

    def get_alarm(self):
        print("Alarmieren")  # Debugging-Ausgabe
        erkankung = self.Erkrankung.get()
        if self.unklare_lage_chackbox_state.get():
            erkankung = "Unklare Lage"
            
        elif self.sonstiges_state.get():
            erkankung = self.textfield.get()
        
        result = alarm(erkankung)
    
        if result == "keine Krankheit ausgewählt":
                print("Fehler: Keine Krankheit ausgewählt")  # Debugging-Ausgabe
                self.show_error("Bitte wählen Sie eine Krankheit")
        else:
            self.error_label.grid_remove()

    

    

    def show_error(self, message):
        self.error_label.config(text="Error: " + message)
        print("Error: "+ message)
        self.error_label.grid(row=0, column=0, padx=10, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = AlarmApp(root)
    root.title("Notifer Base")
    root.geometry("800x600")
    
    button_text = tk.StringVar()
    root.mainloop()