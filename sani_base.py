import tkinter as tk
from tkinter import ttk
from Alert.alarm import alarm
from tkinter import messagebox
from Data.database import search_alerts, get_all_active_alerts, add_health_data, add_alert_data, check_accsess_premission
from assets.widgets import AlarmWidget
from rfid import RFIDReader
class AlarmApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Notifier Sanibase")
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
        
        for F in (LoginPage, StartPage, MenuPage, AlertsPage, HealthDataPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            
            # Alle Frames im selben Container stapeln und den Platz ausfüllen
            frame.grid(row=0, column=0, sticky="nsew")

            self.Login("AlertsPage")
    def Login(self, zielseite):

        # Starte mit der Startseite
        login_page = self.frames["LoginPage"]
        login_page.set_target_site(zielseite)
        self.show_frame("LoginPage")

    def set_login_target_site(self, target_site):
        login_page = self.frames["LoginPage"]
        login_page.set_target_site(target_site)

    def show_frame(self, page_name: str):
        '''Zeigt den Frame für die gegebene Seite'''
        frame = self.frames[page_name]
        frame.tkraise()
    

# Erste Seite
class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        # Benutzername und Passwort für den Login sind nur für Testzwecke festgelegt
        # und werden in zukunft durch eine Datenbank ersetzt

        self.controller = controller
        self.unclear_situation_checkbox_state = tk.IntVar()
        self.other_checkbox_state = tk.IntVar()
        self.target_site = ""
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
        
        label = tk.Label(content_frame, text="Notifier", font=("Arial", 24))
        label.place(relx = 0.5, rely= 0.1, anchor="center")  # Abstand nach oben
        
        

        label2 = tk.Label(content_frame, text="Benutzername")
        label2.place(relx = 0.5, rely= 0.3, anchor="center")

        self.username_entry = ttk.Entry(content_frame)
        self.username_entry.place(relx = 0.5, rely= 0.35, anchor="center")

        self.label3 = tk.Label(content_frame, text="Passwort")
        self.label3.place(relx = 0.5, rely= 0.4, anchor="center")

        self.password_entry = ttk.Entry(content_frame, show="*")
        self.password_entry.place(relx = 0.5, rely= 0.45, anchor="center")

        login_button = tk.Button(content_frame, text="Login", command=lambda: self.login(self.target_site))
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
    def login(self, target_site: str):
        """Überprüft die eingegebenen Daten und zeigt die Startseite an, wenn sie korrekt sind.
        """
        reader = RFIDReader()
        self.uuid = reader.read_data()
        if check_accsess_premission(self.uuid):
            self.controller.show_frame(target_site)
        else:
            self.show_error("Karte nicht erkannt")
    def set_target_site(self, target_site):
        self.target_site = target_site 
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

        health_data_button = tk.Button(content_frame, text="Gesundheitsdaten erfassen", command = self.take_health_data)
        health_data_button.place(relx = 0.3, rely= 0.6, anchor="center")

        send_button = tk.Button(content_frame, text="Protokoll senden", command = lambda: add_alert_data(alert_id= self.controller.aktueller_einsatz ,teacher=lb_entry.get(), measures=maßnahme_entry.get()))
        send_button.place(relx = 0.5, rely= 0.6, anchor="center")

        send_to_operations_maneger_button = tk.Button(content_frame, text="An Einsatzleitung senden",)
        send_to_operations_maneger_button.place(relx = 0.7, rely= 0.6, anchor="center")

        close_alert_button = tk.Button(content_frame, text="Einsatz beenden",)
        close_alert_button.place(relx = 0.5, rely= 0.7, anchor="center")

    def take_health_data(self):
        """Nimmt die Gesundheitsdaten auf und speichert sie in der Datenbank."""
        self.controller.set_login_target_site("HealthDataPage")
        self.controller.show_frame("LoginPage")
        

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

class HealthDataPage(tk.Frame):
    def __init__ (self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        content_frame = tk.Frame(self)
        content_frame.grid(row=0, column=0, sticky="nsew")

        label =  tk.Label(content_frame, text="Gesundheitsdaten", font=("Arial", 24))
        label.place(relx=0.5, rely=0.1, anchor="center")

        label2 = tk.Label(content_frame, text="Puls in bpm")
        label2.place(relx=0.5, rely=0.2, anchor="center")

        puls_entry = tk.Entry(content_frame)
        puls_entry.place(relx=0.5, rely=0.25, anchor="center")

        label3 = tk.Label(content_frame, text="Sauerstoffsättigung in %")
        label3.place(relx=0.5, rely=0.3, anchor="center")

        sauerstoff_entry = tk.Entry(content_frame)
        sauerstoff_entry.place(relx=0.5, rely=0.35, anchor="center")

        label4 = tk.Label(content_frame, text="Temperatur in °C")
        label4.place(relx=0.5, rely=0.4, anchor="center")

        temperatur_entry = tk.Entry(content_frame)
        temperatur_entry.place(relx=0.5, rely=0.45, anchor="center")

        label5 = tk.Label(content_frame, text="Blutdruck in mmHg")
        label5.place(relx=0.5, rely=0.5, anchor="center")

        blutdruck_entry = tk.Entry(content_frame)
        blutdruck_entry.place(relx=0.5, rely=0.55, anchor="center")

        label6 = tk.Label(content_frame, text="Schmerz in Skala von 1-10")
        label6.place(relx=0.5, rely=0.6, anchor="center")

        schmerz_entry = tk.Entry(content_frame)
        schmerz_entry.place(relx=0.5, rely=0.65, anchor="center")

        label7 = tk.Label(content_frame, text="Blutzucker in mg/dl")
        label7.place(relx=0.5, rely=0.7, anchor="center")

        blutzucker_entry = tk.Entry(content_frame)
        blutzucker_entry.place(relx=0.5, rely=0.75, anchor="center")
        
        button = tk.Button(content_frame, text="Zurück zur Startseite", 
                           command=lambda: controller.show_frame("StartPage"))
        button.place(relx = 0.5, rely= 0.85, anchor="center")

        send_button = tk.Button(content_frame, text="Senden", command=lambda: add_health_data(alert_id= self.controller.aktueller_einsatz ,pulse = puls_entry.get(), spo2 = sauerstoff_entry.get(), temperature= temperatur_entry.get(),  blood_pressure=blutdruck_entry.get(), pain=schmerz_entry.get(), blood_suger=blutzucker_entry.get()))
        send_button.place(relx = 0.5, rely= 0.9, anchor="center")




if __name__ == "__main__":
    app = AlarmApp()
    app.mainloop()
