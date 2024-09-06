import tkinter as tk
from tkinter import ttk
from Alert.alarm import alarm


class AlarmApp:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root)
        self.frame.pack()

        self.unclear_situation_checkbox_state = tk.IntVar()
        self.other_state = tk.IntVar()
        self.frame.place(relx=0.5, rely=0.5, anchor='center')
        self.page = 1
        self.button_text ="Menu"
        self.button_text = tk.StringVar()
        self.show_page1()
        
    def show_page1(self):
        self.button_text = tk.StringVar()
        self.button_text.set("Menu")
        self.button1 = ttk.Button(root, textvariable= self.button_text, command=self.togle_page)
        self.button1.grid(row= 0, column=0, padx= 10, pady= 10)
        self.Titele = ttk.Label(self.frame, text="Notifer Base", font=("Arial", 20))
        self.Titele.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        self.symptoms = ttk.Combobox(self.frame, text= "Symptome", values=["Bauchschmerzen", "Kopfschmerzen", "Akutes Abdomen",
        "Intox","tee","Wärmflasche","ACS","Atemnot","Fraktur", "Sportverletzung","Synkope","Panikatake" , "Anaphilaktischer Schock"])

 
        self.symptoms.set("Wählen Sie eine Krankheit")  # Setzt den Standardwert
        self.symptoms.grid(row=2, column=0, padx=10, pady=10)
        # Erstellen der Checkbox für "Unklare Lage"
        self.unclear_situation_checkbox = ttk.Checkbutton(self.frame, text="Unklare Lage", variable=self.unclear_situation_checkbox_state)
        self.unclear_situation_checkbox.grid(row=3, column=0, padx=10, pady=10)

        # Erstellen der Checkbox für "Sonstige"
        self.checkbox = ttk.Checkbutton(self.frame, text="Sonstige", variable=self.other_state)
        self.checkbox.grid(row=4, column=0, padx=10, pady=10)

        # Erstellen des Textfelds, aber zunächst nicht anzeigen
        self.other_textfield = ttk.Entry(self.frame)
        # self.textfield.grid(row=3, column=0, padx=10, pady=10)  # Kommentiert aus, um das Textfeld zunächst zu verstecken

        # Rufen Sie die Funktion toggle_textfield auf, wenn sich der Zustand der Checkbox ändert
        self.other_state.trace('w', self.toggle_textfield)

        # Erstellen des Labels für Fehlermeldungen
        self.error_label = tk.Label(self.frame, text="Error:", font=("Arial", 20), fg="red")
        self.error_label.grid(row=0, column=0, padx=10, pady=10)
        self.error_label.grid_remove()

        # Erstellen des Buttons zum Auslösen des Alarms
        self.button = tk.Button(self.frame, text="Alarmieren", command = self.get_alarm, font=("Arial", 20), bg="red", fg="white")
        self.button.grid(row=6, column=0, padx=10, pady=10)

    def toggle_textfield(self, *args):
        if self.other_state.get():
            self.other_textfield.grid(row=5, column=0, padx=10, pady=10)  # Zeigt das Textfeld an
        else:
            self.other_textfield.grid_remove()  # Versteckt das Textfeld

    def get_alarm(self):
        print("Alarmieren")  # Debugging-Ausgabe
        erkankung = self.symptoms.get()
        if self.unclear_situation_checkbox_state.get():
            erkankung = "Unklare Lage"
            
        elif self.other_state.get():
            erkankung = self.other_textfield.get()
        
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
    def show_page2(self):
        self.button_text.set("Zurück")
        for widget in self.frame.winfo_children(): 
            widget.destroy()
        Titele = ttk.Label(self.frame, text="Menu", font=("Arial", 20))
        Titele.grid(row=0, column=0, columnspan=2, padx=10, pady=10)
    def togle_page(self):
        if self.page == 1:
            self.show_page2()
            self.page = 2
        
        else:
            self.show_page1()
            self.page = 1
if __name__ == "__main__":
    root = tk.Tk()
    app = AlarmApp(root)
    root.title("Notifer Base")
    root.geometry("800x600")
    
    button_text = tk.StringVar()
    root.mainloop()