import tkinter as tk
from tkinter import ttk
from Alert.alarm import alarm
from tkinter import messagebox
from Data.database import search_alerts, get_all_active_alerts
from assets.widgets import AlarmWidget
class AlarmApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Notifyer Sanibase")
        self.geometry("800x600")
        self.iconbitmap("sirene.ico")
        # Container für die Seiten (Frames)
        aktueller_einsatz = "" 
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        
        # Stelle sicher, dass der Container den gesamten Platz ausfüllt
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # Frames speichern
        self.frames = {}
        
        for F in (LoginPage, StartPage, MenuPage, AlertsPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            
            # Alle Frames im selben Container stapeln und den Platz ausfüllen
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Starte mit der Startseite
        self.show_frame("LoginPage")
    
    def show_frame(self, page_name: str):
        '''Zeigt den Frame für die gegebene Seite'''
        frame = self.frames[page_name]
        frame.tkraise()
   

# Erste Seite
class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.username = "Clemens"
        self.passwort = "1234"
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
        
        

        label2 = tk.Label(content_frame, text="Benutzername")
        label2.place(relx = 0.5, rely= 0.3, anchor="center")

        self.username_entry = ttk.Entry(content_frame)
        self.username_entry.place(relx = 0.5, rely= 0.35, anchor="center")

        self.label3 = tk.Label(content_frame, text="Passwort")
        self.label3.place(relx = 0.5, rely= 0.4, anchor="center")

        self.password_entry = ttk.Entry(content_frame, show="*")
        self.password_entry.place(relx = 0.5, rely= 0.45, anchor="center")

        login_button = tk.Button(content_frame, text="Login", command=lambda: self.login())
        login_button.place(relx = 0.5, rely= 0.55, anchor="center")
    

    def show_error(self, message: str):
        """Zeigt eine Fehlermeldung in einem separaten Fenster an.

        Parameters
        ----------
        message : str
            nachricht die angezeigt werden soll
        """
        messagebox.showerror("Fehler", message)
         # Abstand nach oben
    def login(self):
        """Überprüft die eingegebenen Daten und zeigt die Startseite an, wenn sie korrekt sind.
        """
        if self.username == self.username_entry.get() and self.passwort == self.password_entry.get():
            self.controller.show_frame("AlertsPage")
        else:
            self.show_error("Benutzername oder Passwort falsch")   
# Zweite Seite
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        content_frame = tk.Frame(self)
        content_frame.grid(row=0, column=0, sticky="nsew")
        
        label = tk.Label(content_frame, text="Datenerfassung",font=("Arial", 24))
        label.place(relx = 0.5, rely= 0.1, anchor="center") 
        
        button = tk.Button(content_frame, text="Menu", 
                           command=lambda: controller.show_frame("MenuPage"))
        button.place(relx = 0.1, rely= 0.1, anchor="center")

        lb_label = tk.Label(content_frame, text="Lernbegleiter")
        lb_label.place(relx = 0.5, rely= 0.2, anchor="center")

        lb_entry = tk.Entry(content_frame)
        lb_entry.place(relx = 0.5, rely= 0.25, anchor="center")

        maßnahme_label = tk.Label(content_frame, text="Maßnahme")
        maßnahme_label.place(relx = 0.5, rely= 0.4, anchor="center")

        maßnahme_entry = tk.Entry(content_frame)
        maßnahme_entry.place(relx = 0.5, rely= 0.45, anchor="center")

        health_data_button = tk.Button(content_frame, text="Gesundheitsdaten erfassen",)
        health_data_button.place(relx = 0.3, rely= 0.6, anchor="center")

        send_to_operations_maneger_button = tk.Button(content_frame, text="An Einsatzleitung senden",)
        send_to_operations_maneger_button.place(relx = 0.7, rely= 0.6, anchor="center")


        

# Dritte Seite
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

        button1 = tk.Button(content_frame, text="Alarme", 
                           command=lambda: controller.show_frame("AlertsPage"))
        button1.place(relx = 0.5, rely= 0.3, anchor="center")
       
class AlertsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        content_frame = tk.Frame(self)
        content_frame.grid(row=0, column=0, sticky="nsew")
        
        alerts_frame = tk.Frame(content_frame )
        alerts_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.8)

        label = tk.Label(content_frame, text="Alarme", font=("Arial", 24))
        label.place(relx=0.5, rely=0.1, anchor="center")

        alerts = get_all_active_alerts()

        for i, alert in enumerate(alerts):
            widget = AlarmWidget( parent= alerts_frame, controller=controller , alarm_name=alert["name"],  alarm_id= alert["id"])
            row = i // 3
            col = i % 3
            relx = col * 0.33 + 0.05  # 0.33 relative Breite pro Widget + 0.05 relativer Abstand
            rely = row * 0.33 + 0.05  # 0.33 relative Höhe pro Widget + 0.05 relativer Abstand
            widget.place(relx=relx, rely=rely, relwidth=0.28, relheight=0.28)  # Platzieren Sie das Widget mit relativen Koordinaten
              # Platzieren Sie das Widget mit relativen Koordinaten
        """Übernimmt den Alarm und setzt den Status auf 'behandelt'."""
        
if __name__ == "__main__":
    app = AlarmApp()
    app.mainloop()
