import tkinter as tk
from tkinter import ttk
from Alert.alarm import alarm
from tkinter import messagebox
class MultiPageApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Mehrseitige Tkinter Anwendung")
        self.geometry("800x600")
        
        # Container für die Seiten (Frames)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        
        # Stelle sicher, dass der Container den gesamten Platz ausfüllt
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Frames speichern
        self.frames = {}
        
        for F in (StartPage, MenuPage, PageTwo):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            
            # Alle Frames im selben Container stapeln und den Platz ausfüllen
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Starte mit der Startseite
        self.show_frame("StartPage")
    
    def show_frame(self, page_name):
        '''Zeigt den Frame für die gegebene Seite'''
        frame = self.frames[page_name]
        frame.tkraise()

# Erste Seite
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.unclear_situation_checkbox_state = tk.IntVar()
        self.other_checkbox_state = tk.IntVar()
        def resize(self,event):
    # Wenn das Fenster skaliert wird, aktualisiere die Position und Größe der Widgets
            self.label.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.8, relheight=0.2)
            self.button1.place(relx=0.5, rely=0.8, anchor='center', relwidth=0.5, relheight=0.1)


        # Stelle sicher, dass der Frame den gesamten Platz ausfüllt
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Erstelle ein zentriertes Frame für Inhalte
        content_frame = tk.Frame(self)
        content_frame.grid(row=0, column=0, sticky="nsew")  # Inhalt ausfüllen
        
        label = tk.Label(content_frame, text="Notifyer", font=("Arial", 24))
        label.place(relx = 0.5, rely= 0.1, anchor="center")  # Abstand nach oben
        
        menu_button = tk.Button(content_frame, text="Menu",command=lambda: controller.show_frame("MenuPage"))
        menu_button.place(relx = 0.05, rely= 0.05, anchor= "center")  # Abstand nach oben
        
        self.first_name_insert = ttk.Entry(content_frame, text= "Vorname")
        self.first_name_insert.insert(0, "Vorname")
        self.first_name_insert.place(relx = 0.5, rely= 0.3, anchor= "center")  # Abstand nach oben
        self.first_name_insert.bind("<FocusIn>", lambda event: self.clear_placeholder(event, "Vorname"))
        self.first_name_insert.bind("<FocusOut>", lambda event: self.add_placeholder(event, "Vorname"))
        self.first_name_insert.place(relx = 0.5, rely= 0.3, anchor= "center")
        
        self.last_name_insert = ttk.Entry(content_frame, text= "Nachname")
        self.last_name_insert.insert(0, "Nachname")
        self.last_name_insert.place(relx = 0.5, rely= 0.3, anchor= "center")  # Abstand nach oben
        self.last_name_insert.bind("<FocusIn>", lambda event: self.clear_placeholder(event, "Nachname"))
        self.last_name_insert.bind("<FocusOut>", lambda event: self.add_placeholder(event, "Nachname"))
        self.last_name_insert.place(relx = 0.5, rely= 0.35, anchor= "center")

        self.symptoms = ttk.Combobox(content_frame, text= "Symptome", values=["Bauchschmerzen", "Kopfschmerzen", "Akutes Abdomen",
        "Intox","Tee","Wärmflasche","ACS","Atemnot","Fraktur", "Sportverletzung","Synkope","Panikatake" , "Anaphilaktischer Schock"])
        self.symptoms.set("Wählen Sie eine Krankheit")
        self.symptoms.place(relx = 0.5, rely= 0.4, anchor= "center")

        unclear_situation_checkbox = ttk.Checkbutton(content_frame, text="Unklare Lage", variable=self.unclear_situation_checkbox_state)
        unclear_situation_checkbox.place(relx = 0.5, rely= 0.45, anchor= "center")
        
        self.other_checkbox_state = tk.BooleanVar()
        other_checkbox = ttk.Checkbutton(content_frame, text="Sonstige", variable=self.other_checkbox_state, command=self.toggle_textfield)
        other_checkbox.place(relx=0.5, rely=0.5, anchor="center")
        
        self.other_entry = ttk.Entry(content_frame)
        
        alert_button = tk.Button(content_frame, text="Alarmieren", command = self.get_alarm, font=("Arial", 20), bg="red", fg="white")
        alert_button.place(relx = 0.5, rely= 0.6, anchor= "center")
    def toggle_textfield(self):
        if self.other_checkbox_state.get():
            self.other_entry.place(relx=0.5, rely=0.55, anchor="center")  # Zeigt das Textfeld an
        else:
            self.other_entry.place_forget()  # Versteckt das Textfeld
    def clear_placeholder(self, event, placeholder):
        if event.widget.get() == placeholder:
            event.widget.delete(0, tk.END)
            event.widget.config(foreground='black')

    def add_placeholder(self, event, placeholder):
        current_text = event.widget.get()
        if current_text == "" or current_text == placeholder:
            event.widget.delete(0, tk.END)
            event.widget.insert(0, placeholder)
            event.widget.config(foreground='grey')

    def show_error(self, message):
        messagebox.showerror("Fehler", message)
          # Abstand nach oben
    def get_alarm(self):
        print("Alarmieren")  # Debugging-Ausgabe
        erkankung = self.symptoms.get()
        name = self.first_name_insert.get()
        last_name = self.last_name_insert.get()
        if self.unclear_situation_checkbox_state.get():
            erkankung = "Unklare Lage"
            
        elif self.other_checkbox_state.get():
            erkankung = self.other_entry.get()
        
        result = alarm(erkankung, name, last_name )
    
        if result == "keine Krankheit ausgewählt":
                print("Fehler: Keine Krankheit ausgewählt")  # Debugging-Ausgabe
                self.show_error("Bitte wählen Sie eine Krankheit")
       
# Zweite Seite
class MenuPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        content_frame = tk.Frame(self)
        content_frame.grid(row=0, column=0, sticky="nsew")
        
        label = tk.Label(content_frame, text="Menu",font=("Arial", 24))
        label.place(relx = 0.5, rely= 0.1, anchor="center") 
        
        button = tk.Button(content_frame, text="Zurück zur Startseite", 
                           command=lambda: controller.show_frame("StartPage"))
        button.place(relx = 0.5, rely= 0.2, anchor="center")

        button2 = tk.Button(content_frame, text="Seite 2 anzeigen", 
                           command=lambda: controller.show_frame("PageTwo"))
        button2.place(relx = 0.5, rely= 0.3, anchor="center")

# Dritte Seite
class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        content_frame = tk.Frame(self)
        content_frame.grid(row=0, column=0, sticky="nsew")
        
        label = tk.Label(content_frame, text="Das ist Seite 2", font=("Arial", 24))
        label.place(relx = 0.5, rely= 0.1, anchor="center")
        
        button = tk.Button(content_frame, text="Menu",
                           command=lambda: controller.show_frame("MenuPage"))
        button.place(relx = 0.05, rely= 0.1, anchor="center")

        first_name_entry = ttk.Entry(content_frame)
        first_name_entry.place(relx = 0.5, rely= 0.3, anchor="center")

        last_name_entry = ttk.Entry(content_frame)
        last_name_entry.place(relx = 0.5, rely= 0.4, anchor="center")

if __name__ == "__main__":
    app = MultiPageApp()
    app.mainloop()
