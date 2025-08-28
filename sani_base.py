import ttkbootstrap as tb
from ttkbootstrap import DateEntry
from ttkbootstrap.constants import *
import tkinter.font as tkFont
import tkinter.messagebox as mbox
from Alert import alarm
from Data import patient_crud, alerts_crud, protokoll_crud, users_crud
import datetime



class PlaceholderEntry(tb.Entry):
    def __init__(self, parent, placeholder, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.placeholder = placeholder
        self.default_fg_color = self["foreground"]
        self.insert(0, self.placeholder)
        self["foreground"] = "grey"
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

    def _clear_placeholder(self, event):
        if self.get() == self.placeholder:
            self.delete(0, "end")
            self["foreground"] = self.default_fg_color

    def _add_placeholder(self, event):
        if not self.get():
            self.insert(0, self.placeholder)
            self["foreground"] = "grey"



class App(tb.Window):
    def __init__(self):
        super().__init__(themename="sanilink-light")
        self.title("SaniLink")
        self.geometry("800x480")

        # Icon für Fenster und Taskleiste setzen
        icon_path = 'icon.ico'
        self.iconbitmap(icon_path)

        # Zusätzlich für Windows-Taskleiste

        # Benutzer startet als nicht eingeloggt
        self.is_logged_in = False
        self.alert_id = None

        # Navbar
        self.navbar = tb.Frame(self, style="dark")
        self.navbar.pack(side=TOP, fill=X)

        style = tb.Style()
        style.configure(
            "Custom.TLabel",
            background="#263238",
            foreground="#ffffff",
            font=("Exo 2 ExtraBold", 16),
        )

        tb.Label(
            self.navbar,
            text="SaniLink",
            font=("Exo 2 Black", 16),
            style="Custom.TLabel",
        ).pack(side=LEFT, padx=5, pady=5)
        tb.Button(
            self.navbar,
            text="Alarmierung",
            style="dark",
            command=lambda: self.show_frame("AlertPage"),
        ).pack(side=LEFT, padx=(100, 10), pady=5)
        tb.Button(
            self.navbar,
            text="Alarmsuche",
            style="dark",
            command=lambda: self.show_frame("AboutPage"),
        ).pack(side=LEFT, padx=5, pady=5)
        tb.Button(
            self.navbar,
            text="El Protokol",
            style="dark",
            command=lambda: self.show_frame("AboutPage"),
        ).pack(side=LEFT, padx=5, pady=5)
        tb.Button(
            self.navbar,
            text="Benutzerverwaltung",
            style="dark",
            command=lambda: self.show_frame("AboutPage"),
        ).pack(side=LEFT, padx=5, pady=5)
        tb.Button(
            self.navbar,
            text="Alarme",
            style="dark",
            command=lambda: self.show_frame("AlertsPage"),
        ).pack(side=LEFT, padx=5, pady=5)


        tb.Button(self.navbar, text="Beenden", style="danger", command=self.destroy).pack(
            side=RIGHT, padx=5, pady=5
        )

        # Container für alle Seiten
        container = tb.Frame(self)
        container.pack(side=TOP, fill=BOTH, expand=True)

        # Gewichtung für Zeilen und Spalten setzen
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Dictionary für Frames (Seiten)
        self.frames = {}

        # Seiten initialisieren und in dict speichern
        for F in (AlertPage, LoginPage, AlertsPage, ProtokollPage, RegisterPatientPage, HealthDataPage, MaterialPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        # Startseite anzeigen
        self.show_frame("LoginPage")



    def show_frame(self, page_name):
        # Überprüfe, ob der Benutzer eingeloggt ist, wenn er auf geschützte Seiten zugreifen möchte
        if page_name != "LoginPage" and not self.is_logged_in:
            print("Bitte zuerst einloggen")
            page_name = "LoginPage"

        frame = self.frames[page_name]
        frame.tkraise()


class AlertPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Stil für den Hintergrund definieren
        tb.Label(self, text="Alarmierung", font=("Exo 2 ExtraBold", 16)).pack(pady=20)

        name_entry = PlaceholderEntry(self, "Name")
        name_entry.pack(pady=10)
        name_entry.focus()

        last_name_entry = PlaceholderEntry(self, "Nachname")
        last_name_entry.pack(pady=10)

        self.birth_entry = DateEntry(self )

        self.birth_entry.pack(pady=10)

        symptom_combobox = tb.Combobox(
            self, values=["Symptom 1", "Symptom 2", "Symptom 3"]
        )
        symptom_combobox.set("Symptome")
        symptom_combobox.pack(pady=10)

        alert_type_combobox = tb.Combobox(
            self, values=["Unfall", "Erkrankung", "Sonstiges"])
        alert_type_combobox.set("Alarmtyp")
        alert_type_combobox.pack(pady=10)

        style = tb.Style()
        style.configure(
            "Custom.TButton",
            padding=(10, 5),
            font=("Helvetica", 20),
            background="#FF0000",
            foreground="#FFFFFF",
            borderwidth=0,
        )
        self.alert_without_name_var = tb.BooleanVar()
        alert_without_name = tb.Checkbutton(
            self,
            text="Alarm ohne Name",
            variable=self.alert_without_name_var
        )
        alert_without_name.pack(pady=10)
        tb.Button(self, text="Alarmieren", style="Custom.TButton", width=10, command=self.on_alarm_button_click).pack(
            pady=10
        )

    def on_alarm_button_click(self):
        name = self.children['!placeholderentry'].get()
        last_name = self.children['!placeholderentry2'].get()

        symptom = self.children['!combobox'].get()
        alert_type = self.children['!combobox2'].get()
        is_alert_without_name = self.alert_without_name_var.get()

        if symptom == "Symptome" or alert_type == "Alarmtyp":
            print("Bitte wählen Sie ein Symptom und einen Alarmtyp aus.")
            return

        if is_alert_without_name:
            alert_id = alarm.add_alert(symptom, alert_type)


            protokoll_crud.update_status(alert_id, "ohne Name")
            print("Alarm ohne Name ausgelöst.")
        else:
            birthday = datetime.datetime.strptime(self.birth_entry.entry.get(), "%d.%m.%Y").strftime("%d.%m.%Y")
            alert_id = alarm.add_alert(symptom, alert_type)
            print(f"Alert ID in  {alert_id}")
            patient_crud.add_patient(name, last_name, birthday, alert_id)
            print(f"Alarm ausgelöst für {name} {last_name} mit Symptom: {symptom} und Alarmtyp: {alert_type}")




class LoginPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tb.Label(self, text="Login", font=("Exo 2 ExtraBold", 16)).pack(pady=20)

        self.username_entry = PlaceholderEntry(self, "Benutzername")
        self.username_entry.pack(pady=10)
        self.password_entry = PlaceholderEntry(self, "Passwort", show="*")
        self.password_entry.pack(pady=10)
        self.password_entry.bind("<Return>", self.login)

        tb.Button(self, text="Anmelden", style="Custom.TButton", width=10, command=self.login).pack(pady=10)

    def login(self, event=None):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if username == "clemens" and password == "1712":
            self.controller.is_logged_in = True
            self.controller.show_frame("AlertsPage")
        else:
            mbox.showerror("Fehler", "Ungültige Anmeldedaten")
            print("Ungültige Anmeldedaten")


class AlertsPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tb.Label(self, text="Aktive Alarme", font=("Exo 2 ExtraBold", 16)).pack(pady=20)

        # Frame für die Alarme erstellen
        self.alerts_frame = tb.Frame(self)
        self.alerts_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        # Refresh-Button
        tb.Button(
            self,
            text="Aktualisieren",
            bootstyle="secondary",
            command=self.load_alerts
        ).pack(side=BOTTOM, pady=10)

        # Alarme laden
        self.load_alerts()

    def load_alerts(self):
        """Lädt aktive Alarme und zeigt sie als Widgets an"""
        # Bestehende Widgets entfernen
        for widget in self.alerts_frame.winfo_children():
            widget.destroy()

        # Alle aktiven Alarme abrufen
        alerts = alerts_crud.get_all_active_alerts()

        if not alerts:
            # Wenn keine aktiven Alarme vorhanden sind, Hinweis anzeigen
            tb.Label(
                self.alerts_frame,
                text="Keine aktiven Alarme vorhanden",
                font=("Exo 2", 16),
                bootstyle="secondary"
            ).pack(expand=True)
            return

        # Alarme als Grid von AlarmWidgets anzeigen
        # Mehr Spalten (4 statt 3) für kleinere Widgets
        cols_per_row = 4

        for i, alert in enumerate(alerts):
            # Alarm-Widget erstellen mit alert_id und symptom
            widget = AlarmWidget(
                parent=self.alerts_frame,
                controller=self.controller,
                alert_id=alert["id"],
                symptom=alert["symptom"],
                alert_type=alert["alert_type"]
            )

            # Grid-Layout berechnen (4 Spalten)
            row = i // cols_per_row
            col = i % cols_per_row

            # Relative Positionen berechnen mit kleineren Breiten/Höhen
            relx = col * 0.5 + 0.01
            rely = row * 0.5 + 0.01

            # Widget platzieren mit kleinerer Größe
            widget.place(relx=relx, rely=rely, relwidth=0.23, relheight=0.23)



class ProtokollPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tb.Label(self, text="Protokoll", font=("Exo 2 ExtraBold", 16)).pack(pady=20)
        lehrer_liste = users_crud.get_all_teachers()  # z.B. ["Herr Müller", "Frau Schmidt"]

        self.teacher_combobox = tb.Combobox(
            self, values=lehrer_liste
        )
        self.teacher_combobox.set("Lehrer")
        self.teacher_combobox.pack(pady=10)

        self.measure_combobox = tb.Combobox(
            self, values=["Maßnahme 1", "Maßnahme 2", "Maßnahme 3"]
        )
        self.measure_combobox.set("Maßnahme")
        self.measure_combobox.pack(pady=10)
        tb.Button(self, text="Sanitäter hinzufügen", bootstyle="danger", width=20, command=self.add_medic).pack(pady=10)
        tb.Button(self, text="Gesundheitsdaten",  width=20, bootstyle = "primary" ,command=self.add_health_data).pack(pady=10)
        tb.Button(self, text="Protokoll speichern" , width=20, style="Custom.TButton", command=self.save_protokoll).pack(pady=10)

    def add_health_data(self):
        self.controller.show_frame("HealthDataPage")

    def save_protokoll(self):
        teacher_name = self.teacher_combobox.get()
        measure = self.measure_combobox.get()
        split_result = teacher_name.split(" ", 1)
        first_name = split_result[0]
        last_name = split_result[1] if len(split_result) > 1 else ""
        teacher = users_crud.get_teacher_by_name(first_name, last_name)
        if teacher:
            teacher_id = teacher["teacher_id"]
            protokoll_crud.add_teacher_to_protokoll(self.controller.alert_id, teacher_id)
        else:
            print("Lehrer nicht gefunden.")
        print(f"Kommt an {measure}")
        protokoll_crud.add_measure_to_protokoll(self.controller.alert_id, measure)
        print("Protokoll gespeichert")
        self.controller.show_frame("MaterialPage")

    def add_medic(self):
        mbox.showinfo("Anmeldung", "Bitte Karte an das Lesegerät halten")
        print("Sanitäter hinzugefügt")






class RegisterPatientPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tb.Label(self, text="Patient registrieren", font=("Exo 2 ExtraBold", 16)).pack(pady=20)
        PlaceholderEntry(self, "Vorname").pack(pady=10)
        PlaceholderEntry(self, "Nachname").pack(pady=10)
        self.birth_entry = DateEntry(self)
        self.birth_entry.pack(pady=10)

        tb.Button(self, text="Patient registrieren", style="Custom.TButton", width=20, command=self.register_patient).pack(pady=10)

    def register_patient(self):
        first_name = self.children['!placeholderentry'].get()
        last_name = self.children['!placeholderentry2'].get()
        birthday = datetime.datetime.strptime(self.birth_entry.entry.get(), "%d.%m.%Y").strftime("%d.%m.%Y")

        patient_crud.add_patient(first_name, last_name, birthday, self.controller.alert_id)
        self.controller.show_frame("ProtokollPage")

class MaterialPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tb.Label(self, text="Material", font=("Exo 2 ExtraBold", 16)).pack(pady=20)
        material_combobox = tb.Combobox(
            self, values=["Material 1", "Material 2", "Material 3"]
        )
        material_combobox.set("Material")
        material_combobox.pack(pady=10)
        PlaceholderEntry(self, "Menge").pack(pady=10)
        tb.Button(self, text="Material hinzufügen", bootstyle="danger", width=20).pack(pady=10)

        material_treeview = tb.Treeview(self, columns=("Material", "Menge"), show="headings")
        material_treeview.heading("Material", text="Material")
        material_treeview.heading("Menge", text="Menge")
        material_treeview.pack(fill=BOTH, expand=True, padx=20, pady=20)

    def ad




class HealthDataPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tb.Label(self, text="Gesundheitsdaten", font=("Exo 2 ExtraBold", 16)).pack(pady=20)
        temperature_entry = PlaceholderEntry(self, "Körpertemperatur (°C)").pack(pady=10)
        blood_presure_entry = PlaceholderEntry(self, "Blutdruck (mmHg)").pack(pady=10)
        heart_rate_entry = PlaceholderEntry(self, "Herzfrequenz (BPM)").pack(pady=10)
        blood_sugar_entry = PlaceholderEntry(self, "Blutzucker").pack(pady=10)
        spo2_entry = PlaceholderEntry(self, "Sauerstoffsättigung (%)").pack(pady=10)
        pain_entry = PlaceholderEntry(self, "Schmerzen 1-10").pack(pady=10)
        tb.Button(self, text="Daten speichern", style="Custom.TButton", width=20, command=self.save_health_data).pack(pady=10)

    def get_entry_value(self, entry, placeholder):
        value = entry.get()
        return None if value == placeholder else value

    def save_health_data(self):
        print("Gesundheitsdaten gespeichert")
        pulse = self.get_entry_value(self.children['!placeholderentry3'], "Herzfrequenz (BPM)")
        spo2 = self.get_entry_value(self.children['!placeholderentry5'], "Sauerstoffsättigung (%)")
        blood_pressure = self.get_entry_value(self.children['!placeholderentry2'], "Blutdruck (mmHg)")
        temperature = self.get_entry_value(self.children['!placeholderentry'], "Körpertemperatur (°C)")
        blood_sugar = self.get_entry_value(self.children['!placeholderentry4'], "Blutzucker")
        pain = self.get_entry_value(self.children['!placeholderentry6'], "Schmerzen 1-10")

        protokoll_crud.add_health_data_to_protokoll(
            self.controller.alert_id,
            pulse,
            spo2,
            blood_pressure,
            temperature,
            blood_sugar,
            pain
        )
        self.controller.show_frame("ProtokollPage")


class AlarmWidget(tb.Frame):
    def __init__(self, parent, controller, alert_id, symptom, alert_type):
        super().__init__(parent)

        # Alarmdaten speichern
        self.alert_id = alert_id
        self.controller = controller

        # Farbe basierend auf Alarmtyp wählen
        bg_color = self.get_alert_color(alert_type)

        # Hauptframe mit Rahmen
        widget_frame = tb.Frame(
            self,
            bootstyle=bg_color,
            width=30,
            height=50,
        )
        widget_frame.pack_propagate(False)  # Verhindert automatische Größenanpassung
        widget_frame.pack(padx=10, pady=10, fill=BOTH, expand=True)

        # Alarm-Informationen anzeigen (mit weißer Schrift)
        tb.Label(
            widget_frame,
            text=f"Alarm #{alert_id}",
            font=("Exo 2 Bold", 8),
            foreground="white",
            background=self.get_background_color(alert_type)
        ).pack(side=TOP, padx=5, pady=(1, 0))  # Reduzierter Abstand nach unten


        tb.Button(
            widget_frame,
            text="Einsatz übernehmen",
            bootstyle=f"{bg_color}",
            command=self.accept_alarm
        ).pack(side=TOP, padx=5, pady=0)  # Reduzierter Abstand

    def get_alert_color(self, alert_type):
        """Bestimmt die Farbe basierend auf dem Alarmtyp"""
        if alert_type.lower() == "unfall":
            return "danger"
        elif alert_type.lower() == "erkrankung":
            return "warning"
        else:
            return "info"

    def get_background_color(self, alert_type):
        """Bestimmt die tatsächliche Hintergrundfarbe basierend auf dem Alarmtyp"""
        if alert_type.lower() == "unfall":
            return "#dc3545"  # Rot für Gefahr
        elif alert_type.lower() == "erkrankung":
            return "#ffc107"  # Gelb für Warnung
        else:
            return "#0dcaf0"  # Blau für Info

    def accept_alarm(self):
        """Alarm übernehmen und zur Startseite wechseln"""
        print(f"Alarm #{self.alert_id} übernommen")
        self.controller.aktueller_einsatz = self.alert_id
        protokoll = protokoll_crud.get_protokoll_by_alert_id(self.alert_id)
        if protokoll["status"] == "ohne Name":
            self.controller.show_frame("RegisterPatientPage")
        else:
            self.controller.show_frame("ProtokollPage")
        self.controller.alert_id = self.alert_id
        return "accepted"

    def get_color_from_style(self, style_name):
        """Konvertiert Bootstyle-Namen in tatsächliche Farbwerte"""
        colors = {
            "danger": "#dc3545",  # Rot
            "warning": "#ff9800",  # Gelb
            "info": "#0dcaf0"  # Blau
        }
        return colors.get(style_name, "#ffffff")

if __name__ == "__main__":
    app = App()
    app.mainloop()
