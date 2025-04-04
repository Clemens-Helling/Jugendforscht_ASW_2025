import tkinter as tk
from tkinter import ttk
from Alert.alarm import alarm
from tkinter import messagebox
from Data.database import search_alerts, add_accsess_key, add_el_data
from rfid.rfid import RFIDReader
class AlarmApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Notifyer Base")
        self.geometry("800x600")

        # Container für die Seiten (Frames)
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        
        # Stelle sicher, dass der Container den gesamten Platz ausfüllt
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Frames speichern
        self.frames = {}
        
        for F in (StartPage, MenuPage, PageTwo, RFIDPage, El_Page):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            
            # Alle Frames im selben Container stapeln und den Platz ausfüllen
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Starte mit der Startseite
        self.show_frame("StartPage")
    
    def show_frame(self, page_name):
        """Zeigt den Frame für die gegebene Seite

        Parameters
        ----------
        page_name : str
            Name des Frames
        """        
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
        
        self.symptoms = ttk.Combobox(content_frame, text= "Symptome", values=["Bauchschmerzen", "Kopfschmerzen", "Akutes Abdomen",
        "Intox","Tee","Wärmflasche","ACS","Atemnot","Fraktur", "Sportverletzung","Synkope","Panikatake" , "Anaphilaktischer Schock"])
        self.symptoms.set("Wählen Sie eine Krankheit")
        self.symptoms.place(relx = 0.5, rely= 0.4, anchor= "center")
        self.symptoms.bind("<Return>", lambda event: self.get_alarm)

        self.last_name_insert = ttk.Entry(content_frame, text= "Nachname")
        self.last_name_insert.insert(0, "Nachname")
        self.last_name_insert.place(relx = 0.5, rely= 0.3, anchor= "center")  # Abstand nach oben
        self.last_name_insert.bind("<FocusIn>", lambda event: self.clear_placeholder(event, "Nachname"))
        self.last_name_insert.bind("<FocusOut>", lambda event: self.add_placeholder(event, "Nachname"))
        self.last_name_insert.place(relx = 0.5, rely= 0.35, anchor= "center")
        self.last_name_insert.bind("<Return>", lambda event: self.symptoms.focus_set())

        self.first_name_insert = ttk.Entry(content_frame, text= "Vorname")
        self.first_name_insert.insert(0, "Vorname")
        self.first_name_insert.place(relx = 0.5, rely= 0.3, anchor= "center")  # Abstand nach oben
        self.first_name_insert.bind("<FocusIn>", lambda event: self.clear_placeholder(event, "Vorname"))
        self.first_name_insert.bind("<FocusOut>", lambda event: self.add_placeholder(event, "Vorname"))
        self.first_name_insert.place(relx = 0.5, rely= 0.3, anchor= "center")
        self.first_name_insert.bind("<Return>", lambda event: self.last_name_insert.focus_set())

        

        unclear_situation_checkbox = ttk.Checkbutton(content_frame, text="Unklare Lage", variable=self.unclear_situation_checkbox_state)
        unclear_situation_checkbox.place(relx = 0.5, rely= 0.45, anchor= "center")
        
        self.other_checkbox_state = tk.BooleanVar()
        other_checkbox = ttk.Checkbutton(content_frame, text="Sonstige", variable=self.other_checkbox_state, command=self.toggle_textfield)
        other_checkbox.place(relx=0.5, rely=0.5, anchor="center")
        
        self.other_entry = ttk.Entry(content_frame)
        
        alert_button = tk.Button(content_frame, text="Alarmieren", command = self.get_alarm, font=("Arial", 20), bg="red", fg="white")
        alert_button.place(relx = 0.5, rely= 0.65, anchor= "center")

        reset_button = tk.Button(content_frame, text="Reset", command = self.clear_entries, font=("Arial", 20))
        reset_button.place(relx = 0.7, rely= 0.65, anchor= "center")
    def toggle_textfield(self):
        """zeigt bei bedarf das Textfeld an oder versteckt es wieder
        """
        if self.other_checkbox_state.get():
            self.other_entry.place(relx=0.5, rely=0.55, anchor="center")  # Zeigt das Textfeld an
        else:
            self.other_entry.place_forget()  # Versteckt das Textfeld
    def clear_placeholder(self, event, placeholder):
        """Löscht die Platzhaltertexte, wenn das Entry-Widget fokussiert wird

        Parameters
        ----------
        event : tk.Event
            Das Event-Objekt
        placeholder : str
            Der Platzhaltertext
        """
        if event.widget.get() == placeholder:
            event.widget.delete(0, tk.END)
            event.widget.config(foreground='black')

    def add_placeholder(self, event, placeholder):
        """Fügt die Platzhaltertexte wieder hinzu, wenn das Entry-Widget den Fokus verliert

        Parameters
        ----------
        event : tk.Event
            Das Event-Objekt

        placeholder : str
            Der Platzhaltertext
        """
        current_text = event.widget.get()
        if current_text == "" or current_text == placeholder:
            event.widget.delete(0, tk.END)
            event.widget.insert(0, placeholder)
            event.widget.config(foreground='grey')

    def show_error(self, message):
        """Zeigt eine Fehlermeldung an

        Parameters
        ----------
        message : str
            Nachricht die angezeigt werden soll
        """
        messagebox.showerror("Fehler", message)
          # Abstand nach oben
    def get_alarm(self):
        """ Sendet den Alar, speichert die Daten und zeigt eine Erfolgsmeldung an
        """
        print("Alarmieren")
          # Debugging-Ausgabe
        erkankung = self.symptoms.get()
        name = self.first_name_insert.get()
        last_name = self.last_name_insert.get()
        if self.unclear_situation_checkbox_state.get():
            erkankung = "Unklare Lage"
            
        elif self.other_checkbox_state.get():
            erkankung = self.other_entry.get()
        stripped_name = name.replace(" ", "")
        stripped_last_name = last_name.replace(" ", "")
        result = alarm(erkankung, stripped_name, stripped_last_name )
        messagebox.showinfo("Alarm", "Alarm wurde gesendet")
        if result == "keine Krankheit ausgewählt":
                print("Fehler: Keine Krankheit ausgewählt")  # Debugging-Ausgabe
                self.show_error("Bitte wählen Sie eine Krankheit")

    def clear_entries(self):
        """Löscht die Eingaben in den Entry-Widgets
        """
        self.first_name_insert.delete(0, tk.END)
        self.last_name_insert.delete(0, tk.END)   
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

        button2 = tk.Button(content_frame, text="Alarmsuche", 
                           command=lambda: controller.show_frame("PageTwo"))
        button2.place(relx = 0.5, rely= 0.3, anchor="center")

        button3 = tk.Button(content_frame, text="RFID", command=lambda: controller.show_frame("RFIDPage"))
        button3.place(relx = 0.5, rely= 0.4, anchor="center")

        button4 = tk.Button(content_frame, text="EL Daten", command=lambda: controller.show_frame("El_Page"))
        button4.place(relx = 0.5, rely= 0.5, anchor="center")
# Dritte Seite
class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        content_frame = tk.Frame(self)
        content_frame.grid(row=0, column=0, sticky="nsew")
        
        label = tk.Label(content_frame, text="Alarm Suche", font=("Arial", 24))
        label.place(relx = 0.5, rely= 0.1, anchor="center")
        
        button = tk.Button(content_frame, text="Menu",
                           command=lambda: controller.show_frame("MenuPage"))
        button.place(relx = 0.05, rely= 0.1, anchor="center")

        label = ttk.Label(content_frame, text="Vorname")
        label.place(relx = 0.5, rely= 0.2, anchor="center")

        self.entry= ttk.Entry(content_frame, text= "Vorname eingeben")
        self.entry.place(relx = 0.5, rely= 0.25, anchor= "center")
        self.entry.bind("<Return>", lambda event: self.entry1.focus_set())
        
        label1 = ttk.Label(content_frame, text="Nachname")
        label1.place(relx = 0.5, rely= 0.3, anchor="center")

        self.entry1= ttk.Entry(content_frame, text= "Nachname eingeben")
        self.entry1.place(relx = 0.5, rely= 0.35, anchor= "center")
        self.entry1.bind("<Return>", lambda event: self.load_data())

        search_button = tk.Button(content_frame, text="Suchen", command = self.load_data, font=("Arial", 20),  fg="black")
        search_button.place(relx = 0.3, rely= 0.4, anchor= "center")

        self.tree = ttk.Treeview(self, columns=("id","name", "lastname", "symptom", "medic","timestamp"), show='headings')
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("lastname", text="Last Name")
        self.tree.heading("symptom", text="Symptom")
        self.tree.heading("medic", text="Medic")
        self.tree.heading("timestamp", text="Timestamp")
        
        self.tree.place(relx = 0.5, rely= 0.7, anchor= "center",relwidth=0.8, relheight=0.3)
        
        # Daten abrufen und in Treeview einfügen
        self.load_data()

    def load_data(self):
        """Lädt die Daten in die Treeview
        """
        for item in self.tree.get_children():
            self.tree.delete(item)
        entry_value = self.entry.get().replace(" ", "").strip()
        entry1_value = self.entry1.get().replace(" ", "").strip()
        data = search_alerts(entry_value, entry1_value)
        if data:
            for item in data:
                self.tree.insert("", tk.END, values=(item["id"],item["name"], item["lastname"], item["symptom"], item["medic"], item["timestamp"]))
        else:
            print("No data found")

class RFIDPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        content_frame = tk.Frame(self)
        content_frame.grid(row=0, column=0, sticky="nsew")

        self.label = tk.Label(content_frame, text="Zugangskontrolle", font=("Arial", 24))
        self.label.place(relx = 0.5, rely= 0.1, anchor="center")

        self.button = tk.Button(content_frame, text="Menu",
                           command=lambda: controller.show_frame("MenuPage"))
        self.button.place(relx = 0.05, rely= 0.1, anchor="center")

        self.firstname_entry = ttk.Entry(content_frame, text="Vorname")
        self.firstname_entry.place(relx = 0.1, rely= 0.2, anchor="center")

        self.lastname_entry = ttk.Entry(content_frame, text="Nachname")
        self.lastname_entry.place(relx = 0.5, rely= 0.2, anchor="center")

        self.premisson_combobox = ttk.Combobox(content_frame, text="Berechtigung", values=["Admin", "User", "Sani", "Sani+","Juniorhelfer", "FSJ"])
        self.premisson_combobox.set("Berechtigung")
        self.premisson_combobox.place(relx = 0.9, rely= 0.2, anchor="center")

        self.treeview = ttk.Treeview(content_frame, columns=("Name", "Nachname", "Letzter Zugriff", "UUID"), show='headings')
        self.treeview.heading("Name", text="Name")
        self.treeview.heading("Nachname", text="Nachname")
        self.treeview.heading("Letzter Zugriff", text="Letzter Zugriff")
        self.treeview.heading("UUID", text="UUID")
        self.treeview.place(relx = 0.5, rely= 0.5, anchor="center")

        self.delete_accsess_button = tk.Button(content_frame, text="Zugriff löschen", font=("Arial", 15), bg="red", fg="white")
        self.delete_accsess_button.place(relx = 0.7, rely= 0.8, anchor="center")

        self.add_accsess_key_button = tk.Button(content_frame, text="RFID Chip hinzufügen", font=("Arial", 15), bg="green", fg="white", command= self.add_accsess_key)
        self.add_accsess_key_button.place(relx = 0.3, rely= 0.8, anchor="center")

    def add_accsess_key(self):
        self.reader = RFIDReader()
        self.key = self.reader.read_data()
        messagebox.showinfo("RFID",
                            f"Bitte halten sie den Chip von: {self.firstname_entry.get()} {self.lastname_entry.get()} an den Leser")
        # Annahme: add_accsess_key ist eine Methode zum Speichern des Schlüssels
        add_accsess_key(self.firstname_entry.get(), self.lastname_entry.get(), self.key, self.premisson_combobox.get())
        messagebox.showinfo("RFID", "Zugriffsschlüssel wurde hinzugefügt")




class El_Page(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        content_frame = tk.Frame(self)
        content_frame.grid(row=0, column=0, sticky="nsew")

        self.menu_button = tk.Button(content_frame, text="Menu", command=lambda: controller.show_frame("MenuPage"))
        self.menu_button.place(relx = 0.05, rely= 0.05, anchor="center")
        self.label = tk.Label(content_frame, text="EL Daten", font=("Arial", 24))
        self.label.place(relx = 0.5, rely= 0.1, anchor="center")

        self.picked_up_checkbox_state = tk.BooleanVar()
        self.picked_up_checkbox = ttk.Checkbutton(content_frame, text="Abgeholt", variable=self.picked_up_checkbox_state)
        self.picked_up_checkbox.place(relx = 0.2, rely= 0.2, anchor="center")

        self.alone_at_home_checkbox_state = tk.BooleanVar()
        self.alone_at_home_checkbox = ttk.Checkbutton(content_frame, text="Alleine nach Hause", variable=self.alone_at_home_checkbox_state)
        self.alone_at_home_checkbox.place(relx = 0.2, rely= 0.3, anchor="center")

        self.taxi_checkbox_state = tk.BooleanVar()
        self.taxi_checkbox = ttk.Checkbutton(content_frame, text="Taxi zum Arzt ins KH", variable=self.taxi_checkbox_state)
        self.taxi_checkbox.place(relx = 0.2, rely= 0.4, anchor="center")

        self.ambulance_checkbox_state = tk.BooleanVar()
        self.ambulance_checkbox = ttk.Checkbutton(content_frame, text="Rettungsdienst", variable=self.ambulance_checkbox_state)
        self.ambulance_checkbox.place(relx = 0.2, rely= 0.5, anchor="center")

        self.hospital_checkbox_state = tk.BooleanVar()
        self.hospital_checkbox = ttk.Checkbutton(content_frame, text="Ins Krankenhaus", variable=self.hospital_checkbox_state)
        self.hospital_checkbox.place(relx = 0.2, rely= 0.6, anchor="center")

        self.notified_at_label = ttk.Label(content_frame, text="Eltern benachrichtigt um:")
        self.notified_at_label.place(relx = 0.5, rely= 0.7, anchor="center")

        self.notified_at_entry = ttk.Entry(content_frame)
        self.notified_at_entry.place(relx = 0.5, rely= 0.75, anchor="center")

        self.notified_by_label = ttk.Label(content_frame, text="Benachrichtigt durch:")
        self.notified_by_label.place(relx = 0.5, rely= 0.8, anchor="center")

        self.notified_by_entry = ttk.Entry(content_frame)
        self.notified_by_entry.place(relx = 0.5, rely= 0.85, anchor="center")

        self.alert_id_label = ttk.Label(content_frame, text="Alarm ID:")
        self.alert_id_label.place(relx = 0.5, rely= 0.9, anchor="center")

        self.alert_id_entry = ttk.Entry(content_frame)
        self.alert_id_entry.place(relx = 0.5, rely= 0.95, anchor="center")

        self.begleitperson_label = ttk.Label(content_frame, text="Begleitperson:")
        self.begleitperson_label.place(relx = 0.5, rely= 0.35, anchor="center")

        self.begleitperson_entry = ttk.Entry(content_frame)
        self.begleitperson_entry.place(relx = 0.5, rely= 0.4,  anchor="center")

        self.destination_label = ttk.Label(content_frame, text="Ziel:")
        self.destination_label.place(relx = 0.7, rely= 0.35, anchor="center")

        self.destination_entry = ttk.Entry(content_frame)
        self.destination_entry.place(relx = 0.7, rely= 0.4, anchor="center")

        self.hospital_label = ttk.Label(content_frame, text="Krankenhaus:")
        self.hospital_label.place(relx = 0.5, rely= 0.55, anchor="center")

        self.hospital_entry = ttk.Entry(content_frame)
        self.hospital_entry.place(relx = 0.5, rely= 0.6, anchor="center")

        self.submit_button = tk.Button(content_frame, text="Daten speichern", font=("Arial", 20), bg="green", fg="white", command=self.submit)
        self.submit_button.place(relx = 0.8, rely= 0.95, anchor="center")

    def submit(self):
        """Speichert die Daten in der Datenbank
        """
        abhol_massnahme = ""
        if self.picked_up_checkbox_state.get():
            abhol_massnahme = "Abgeholt"
        elif self.alone_at_home_checkbox_state.get():
            abhol_massnahme = "Alleine nach Hause"
        elif self.taxi_checkbox_state.get():
            abhol_massnahme = f"Taxi nach {self.destination_entry.get()} mit {self.begleitperson_entry.get()}"
        elif self.ambulance_checkbox_state.get():
            abhol_massnahme = "Rettungsdienst"
        elif self.hospital_checkbox_state.get():
            abhol_massnahme = f"Ins Krankenhaus {self.hospital_entry.get()}"
        else:
            messagebox.showerror(
                "Fehler",
                "Bitte wählen Sie eine Abholmaßnahme"
            )
            return
        add_el_data(self.alert_id_entry.get(), abhol_massnahme, self.notified_at_entry.get(), self.notified_by_entry.get(), self.hospital_entry.get())



    
        
if __name__ == "__main__":
    app = AlarmApp()
    app.mainloop()
