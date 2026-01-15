import datetime
import threading
import time
import tkinter.font as tkFont
import tkinter.messagebox as mbox

import ttkbootstrap as tb
import winsound
from ttkbootstrap import DateEntry
from ttkbootstrap.constants import *

from Alert import alarm
from Data import alerts_crud, patient_crud, protokoll_crud, users_crud
from Data.materials_crud import add_material_to_protokoll, get_all_material_names, subtract_material_quantity, \
    get_material_id_by_name, check_low_stock, get_material, get_material_name_by_id, get_materials_by_protokoll_id, \
    add_material_quantity
from Data.protokoll_crud import update_status, convert_alert_to_protokoll_id
from Data.users_crud import check_user_permisson
from rfid.rfid import read_rfid_uid
from easy_logger.easy_logger import EasyLogger

logger = EasyLogger("SaniRaspiApp")

class ScrollableFrame(tb.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        canvas = tb.Canvas(self, borderwidth=0)
        scrollbar = tb.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tb.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

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

        # Zusätzlich für Windows-Taskleiste

        # Benutzer startet als nicht eingeloggt
        self.is_logged_in = True
        self.alert_id = None
        self.current_sani1 = None
        self.current_sani2 = None
        # alert_id für die Rückgabedes Materials+
        self.selected_alert = None
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
            text="Alarme",
            style="dark",
            command=lambda: self.show_frame("AlertsPage"),
        ).pack(side=LEFT, padx=5, pady=5)

        tb.Button(
            self.navbar,
            text="Wartende Einsätze",
            style="dark",
            command=lambda: self.show_frame("WaitingForMaterialPage"),
        ).pack(side=LEFT, padx=5, pady=5)


        tb.Button(
            self.navbar, text="Beenden", style="danger", command=self.destroy
        ).pack(side=RIGHT, padx=5, pady=5)
        tb.Button(self.navbar, text="Logout", style="danger", command=self.logout).pack(
            side=RIGHT, padx=5, pady=5
        )
        tb.Button(
            self.navbar, text="SOS", style="danger", command=self.trigger_sos_alarm
        ).pack(side=RIGHT, padx=5, pady=5)
        tb.Button(
            self.navbar, text="Reanimation", style="danger", command=lambda: self.show_frame("HLWPage")
        ).pack(side=RIGHT, padx=5, pady=5)

        # Container für alle Seiten
        container = tb.Frame(self)
        container.pack(side=TOP, fill=BOTH, expand=True)

        # Gewichtung für Zeilen und Spalten setzen
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Dictionary für Frames (Seiten)
        self.frames = {}

        # Seiten initialisieren und in dict speichern
        for F in (
            AlertPage,
            LoginPage,
            AlertsPage,
            ProtokollPage,
            RegisterPatientPage,
            HealthDataPage,
            MaterialPage,
            WaitingForMaterialPage,
            MaterialReturnPage,
            HLWPage
        ):
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
        if page_name == "AlertsPage":
            self.frames[page_name].load_alerts()
        if page_name == "MaterialReturnPage":
            self.frames[page_name].load_materials()

        frame = self.frames[page_name]
        frame.tkraise()

    def logout(self):
        self.is_logged_in = False
        self.current_sani1 = None
        self.current_sani2 = None
        self.alert_id = None
        self.show_frame("LoginPage")

    def trigger_sos_alarm(self):
        mbox.showinfo("SOS Alarm", "SOS Alarm wird ausgelöst!")
        alarm.send_alert("Alarm aus dem Sani Raum")


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

        self.birth_entry = DateEntry(self)

        self.birth_entry.pack(pady=10)

        symptom_combobox = tb.Combobox(
            self, values=["Symptom 1", "Symptom 2", "Symptom 3"]
        )
        symptom_combobox.set("Symptome")
        symptom_combobox.pack(pady=10)

        alert_type_combobox = tb.Combobox(
            self, values=["Unfall", "Erkrankung", "Sonstiges"]
        )
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
            self, text="Alarm ohne Name", variable=self.alert_without_name_var
        )
        alert_without_name.pack(pady=10)
        tb.Button(
            self,
            text="Alarmieren",
            style="Custom.TButton",
            width=10,
            command=self.on_alarm_button_click,
        ).pack(pady=10)

    def on_alarm_button_click(self):
        name = self.children["!placeholderentry"].get()
        last_name = self.children["!placeholderentry2"].get()

        symptom = self.children["!combobox"].get()
        alert_type = self.children["!combobox2"].get()
        is_alert_without_name = self.alert_without_name_var.get()

        if symptom == "Symptome" or alert_type == "Alarmtyp":
            print("Bitte wählen Sie ein Symptom und einen Alarmtyp aus.")
            return

        if is_alert_without_name:
            alert_id = alarm.add_alert(symptom, alert_type)

            protokoll_crud.update_status(alert_id, "ohne Name")
            print("Alarm ohne Name ausgelöst.")
        else:
            birthday = datetime.datetime.strptime(
                self.birth_entry.entry.get(), "%d.%m.%Y"
            ).strftime("%d.%m.%Y")
            alert_id = alarm.add_alert(symptom, alert_type)
            print(f"Alert ID in  {alert_id}")
            patient_crud.add_patient(name, last_name, birthday, alert_id)
            print(
                f"Alarm ausgelöst für {name} {last_name} mit Symptom: {symptom} und Alarmtyp: {alert_type}"
            )


class LoginPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tb.Label(self, text="Login", font=("Exo 2 ExtraBold", 16)).pack(pady=20)

        tb.Button(
            self, text="Anmelden", style="Custom.TButton", width=10, command=self.login
        ).pack(pady=10)

    def login(self, event=None):

        mbox.showinfo("Anmeldung", "Bitte Karte an das Lesegerät halten")
        card_id = read_rfid_uid()
        print(f"Gelesene Karten-ID: {card_id}")

        user = users_crud.get_user_by_card_number(str(card_id))
        if (
            users_crud.check_user_permisson(str(card_id), "User")
            or users_crud.check_user_permisson(str(card_id), "Junior")
            or users_crud.check_user_permisson(str(card_id), "Admin")
        ):
            print(f"Willkommen {user['name']} {user['last_name']}!")
            self.controller.is_logged_in = True
            self.controller.show_frame("AlertsPage")
            self.controller.current_sani1 = card_id
            return
        else:
            print("Karte nicht erkannt.")


class AlertsPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tb.Label(self, text="Aktive Alarme", font=("Exo 2 ExtraBold", 16)).pack(pady=20)

        self.alerts_frame = tb.Frame(self)
        self.alerts_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)

        tb.Button(
            self, text="Aktualisieren", bootstyle="secondary", command=self.load_alerts
        ).pack(side=BOTTOM, pady=10)
        self.load_alerts()

    def load_alerts(self):
        print("=== load_alerts wird aufgerufen ===")

        # Bestehende Widgets zählen und entfernen
        existing_widgets = self.alerts_frame.winfo_children()
        print(f"Anzahl bestehender Widgets: {len(existing_widgets)}")

        for widget in existing_widgets:
            print(f"Entferne Widget: {widget}")
            widget.destroy()

        # Frame aktualisieren
        self.alerts_frame.update_idletasks()
        self.update()

        # Aktive Alarme abrufen
        alerts = alerts_crud.get_all_active_alerts()
        print(f"Anzahl geladener Alerts: {len(alerts)}")

        for alert in alerts:
            print(f"Alert: ID={alert['id']}, Symptom={alert['symptom']}, Type={alert['alert_type']}")

        if not alerts:
            label = tb.Label(
                self.alerts_frame,
                text="Keine aktiven Alarme vorhanden",
                font=("Exo 2", 16),
                bootstyle="secondary",
            )
            label.grid(row=0, column=0, columnspan=4, pady=50)
            print("Keine Alarme - Label erstellt")
            return

        # Grid-Spalten konfigurieren
        for i in range(4):
            self.alerts_frame.columnconfigure(i, weight=1)

        # Alarm-Widgets erstellen
        for i, alert in enumerate(alerts):
            row = i // 4
            col = i % 4

            print(f"Erstelle Widget {i}: row={row}, col={col}")

            widget = AlarmWidget(
                parent=self.alerts_frame,
                controller=self.controller,
                alert_id=alert["id"],
                symptom=alert["symptom"],
                alert_type=alert["alert_type"],
            )
            widget.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            print(f"Widget {i} erstellt und platziert")

        print("=== load_alerts beendet ===\n")



class ProtokollPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tb.Label(self, text="Protokoll", font=("Exo 2 ExtraBold", 16)).pack(pady=20)
        lehrer_liste = (
            users_crud.get_all_teachers()
        )  # z.B. ["Herr Müller", "Frau Schmidt"]

        self.teacher_combobox = tb.Combobox(self, values=lehrer_liste)
        self.teacher_combobox.set("Lehrer")
        self.teacher_combobox.pack(pady=10)
        self.setup_searchable_combobox(self.teacher_combobox, lehrer_liste)

        self.measure_combobox = tb.Combobox(
            self, values=["Tee", "Traubenzucker", "Wärmfalsche", "Kälteanwendung", "Wundversorgung", "Ruhepause"]
        )
        self.measure_combobox.set("Maßnahme")
        self.measure_combobox.pack(pady=10)
        tb.Button(
            self,
            text="Sanitäter hinzufügen",
            bootstyle="danger",
            width=20,
            command=self.add_medic,
        ).pack(pady=10)
        tb.Button(
            self,
            text="Gesundheitsdaten",
            width=20,
            bootstyle="primary",
            command=self.add_health_data,
        ).pack(pady=10)
        tb.Button(
            self,
            text="Protokoll speichern",
            width=20,
            style="Custom.TButton",
            command=self.save_protokoll,
        ).pack(pady=10)

    def add_health_data(self):
        if (
                self.controller.current_sani1
                and check_user_permisson(self.controller.current_sani1, "Admin")
        ) or (
                self.controller.current_sani1
                and check_user_permisson(self.controller.current_sani1, "User")
        ) or (
                self.controller.current_sani2
                and check_user_permisson(self.controller.current_sani2, "Admin")
        ) or (
                self.controller.current_sani2
                and check_user_permisson(self.controller.current_sani2, "User")
        ):
            print("Zugriff auf Gesundheitsdaten erlaubt.")
            self.controller.show_frame("HealthDataPage")
        else:
            print("Zugriff verweigert. Keine Berechtigung.")

    def protokoll_medic(self):
        sani1 = self.controller.current_sani1
        sani2 = self.controller.current_sani2
        alert_id = self.controller.alert_id
        if sani1:
            users_crud.add_sani1_by_id(sani1, alert_id)
        if sani2:
            users_crud.add_sani2_by_id(sani2, alert_id)

        sani_protokoll_id = protokoll_crud.get_sani_protokoll_id_by_alert_id(alert_id)

        return sani_protokoll_id

    def save_protokoll(self):
        teacher_name = self.teacher_combobox.get()
        measure = self.measure_combobox.get()
        split_result = teacher_name.split(" ", 1)
        first_name = split_result[0]
        last_name = split_result[1] if len(split_result) > 1 else ""
        teacher = users_crud.get_teacher_by_name(first_name, last_name)
        if teacher:
            teacher_id = teacher["teacher_id"]
            protokoll_crud.add_teacher_to_protokoll(
                self.controller.alert_id, teacher_id
            )
        else:
            print("Lehrer nicht gefunden.")

        protokoll_crud.add_measure_to_protokoll(self.controller.alert_id, measure)
        users_crud.add_sani1(self.controller.current_sani1, self.controller.alert_id)
        users_crud.add_sani2(self.controller.current_sani2, self.controller.alert_id)
        print("Protokoll gespeichert")
        self.controller.show_frame("MaterialPage")

    def add_medic(self):

        mbox.showinfo("Anmeldung", "Bitte Karte an das Lesegerät halten")
        card_id = read_rfid_uid()
        print(f"Gelesene Karten-ID: {card_id}")
        user = users_crud.get_user_by_card_number(str(card_id))
        if user:
            mbox.showinfo(
                "Erfolgreich", f"Willkommen {user['name']} {user['last_name']}!"
            )
            print(f"Willkommen {user['name']} {user['last_name']}!")
            self.controller.current_sani2 = card_id
            return
        else:
            mbox.showerror("Fehler", "Karte nicht erkannt.")
            print("Karte nicht erkannt.")

    def setup_searchable_combobox(self, combobox, values):
        """Macht die Combobox durchsuchbar während du tippst"""

        def on_keyrelease(event):
            # Aktuellen eingegebenen Text holen
            typed = combobox.get().lower()

            # Wenn nichts eingegeben, alle Werte zeigen
            if typed == '':
                combobox['values'] = values
            else:
                # Filtern nach eingegebenem Text
                filtered = [item for item in values if typed in item.lower()]
                combobox['values'] = filtered

        # KeyRelease Event binden
        combobox.bind('<KeyRelease>', on_keyrelease)


class RegisterPatientPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tb.Label(self, text="Patient registrieren", font=("Exo 2 ExtraBold", 16)).pack(
            pady=20
        )
        PlaceholderEntry(self, "Vorname").pack(pady=10)
        PlaceholderEntry(self, "Nachname").pack(pady=10)
        self.birth_entry = DateEntry(self)
        self.birth_entry.pack(pady=10)


        tb.Button(
            self,
            text="Patient registrieren",
            style="Custom.TButton",
            width=20,
            command=self.register_patient,
        ).pack(pady=10)

    def register_patient(self):
        first_name = self.children["!placeholderentry"].get()
        last_name = self.children["!placeholderentry2"].get()
        birthday = datetime.datetime.strptime(
            self.birth_entry.entry.get(), "%d.%m.%Y"
        ).strftime("%d.%m.%Y")

        patient_crud.add_patient(
            first_name, last_name, birthday, self.controller.alert_id
        )
        self.controller.show_frame("ProtokollPage")


class MaterialPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        material_list = get_all_material_names()
        tb.Label(self, text="Material", font=("Exo 2 ExtraBold", 16)).pack(pady=20)
        material_combobox = tb.Combobox(self, values=material_list)
        material_combobox.set("Material")
        material_combobox.pack(pady=10)
        PlaceholderEntry(self, "Menge").pack(pady=10)
        tb.Button(
            self,
            text="Material hinzufügen",
            bootstyle="danger",
            width=20,
            command=self.add_material,
        ).pack(pady=10)
        tb.Button(
            self,
            text="Material speichern",
            bootstyle="danger",
            width=20,
            command=self.save_materials,
        ).pack(pady=10)

        self.material_treeview = tb.Treeview(
            self, columns=("Material", "Menge"), show="headings"
        )
        self.material_treeview.heading("Material", text="Material")
        self.material_treeview.heading("Menge", text="Menge")
        self.material_treeview.pack(fill=BOTH, expand=True, padx=20, pady=20)

    def add_material(self):
        material = self.children["!combobox"].get()
        menge = self.children["!placeholderentry"].get()
        if material == "Material" or not menge.isdigit():
            print("Bitte gültiges Material und Menge eingeben.")
            return
        self.material_treeview.insert("", "end", values=(material, menge))

    def save_materials(self):
        reusable_found = False  # Variable muss initialisiert werden
        for item in self.material_treeview.get_children():
            material, menge = self.material_treeview.item(item, "values")
            material_id = get_material_id_by_name(material)
            material_info = get_material(material)
            if material_id is None:
                print(f"Material '{material}' nicht gefunden.")
                continue
            if material_info['is_reuseable']:
                reusable_found = True
                update_status(self.controller.alert_id, f"wf {get_material_name_by_id(material_id)}")
            add_material_to_protokoll(self.controller.alert_id, material, int(menge))
            subtract_material_quantity(material_id, int(menge))
            low_materials = check_low_stock()
            if material in low_materials:
                for low_material in low_materials[material]:
                    alarm.add_material_alert(low_material["material_name"], "Material")

        if not reusable_found:  # Nur schließen wenn kein wiederverwendbares Material gefunden wurde

            protokoll_crud.close_alert(self.controller.alert_id)
            print("Materialien gespeichert")

        else:
            print("Wiederverwendbares Material gefunden - Alarm bleibt offen für Reinigung")
        self.controller.show_frame("AlertsPage")




class HealthDataPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        scroll_frame = ScrollableFrame(self)
        scroll_frame.pack(fill="both", expand=True)

        container = scroll_frame.scrollable_frame

        tb.Label(container, text="Gesundheitsdaten", font=("Exo 2 ExtraBold", 16)).pack(
            pady=20
        )
        self.temperature_entry = PlaceholderEntry(container, "Körpertemperatur (°C)")
        self.temperature_entry.pack(pady=10)
        self.blood_pressure_entry = PlaceholderEntry(container, "Blutdruck (mmHg)")
        self.blood_pressure_entry.pack(pady=10)
        self.heart_rate_entry = PlaceholderEntry(container, "Herzfrequenz (BPM)")
        self.heart_rate_entry.pack(pady=10)
        self.blood_sugar_entry = PlaceholderEntry(container, "Blutzucker")
        self.blood_sugar_entry.pack(pady=10)
        self.spo2_entry = PlaceholderEntry(container, "Sauerstoffsättigung (%)")
        self.spo2_entry.pack(pady=10)
        self.pain_entry = PlaceholderEntry(container, "Schmerzen 1-10")
        self.pain_entry.pack(pady=10)

        tb.Button(
            container,
            text="Daten speichern",
            bootstyle="danger",
            width=20,
            command=self.save_health_data,
        ).pack(pady=10)

    def get_entry_value(self, entry, placeholder):
        value = entry.get()
        return None if value == placeholder else value

    def save_health_data(self):
        print("Gesundheitsdaten gespeichert")
        pulse = self.get_entry_value(self.heart_rate_entry, "Herzfrequenz (BPM)")
        spo2 = self.get_entry_value(self.spo2_entry, "Sauerstoffsättigung (%)")
        blood_pressure = self.get_entry_value(self.blood_pressure_entry, "Blutdruck (mmHg)")
        temperature = self.get_entry_value(self.temperature_entry, "Körpertemperatur (°C)")
        blood_sugar = self.get_entry_value(self.blood_sugar_entry, "Blutzucker")
        pain = self.get_entry_value(self.pain_entry, "Schmerzen 1-10")

        protokoll_crud.add_health_data_to_protokoll(
            self.controller.alert_id,
            pulse,
            spo2,
            blood_pressure,
            temperature,
            blood_sugar,
            pain,
        )
        self.controller.show_frame("ProtokollPage")

class WaitingForMaterialPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tb.Label(self, text="Warte auf Material", font=("Exo 2 ExtraBold", 16)).pack(
            pady=20
        )

        self.result_table = tb.Treeview(
            self,
            columns=("Alert ID", "Name", "Symptom", "Lehrkraft", "Status"),
            show="headings",
        )

        self.result_table.heading("Alert ID", text="Alert ID")
        self.result_table.heading("Name", text="Name")
        self.result_table.heading("Symptom", text="Symptom")
        self.result_table.heading("Lehrkraft", text="Lehrkraft")
        self.result_table.heading("Status", text="Status")
        self.result_table.pack(pady=10, fill=BOTH, expand=True)

        self.result_table.column("Alert ID", width=80, minwidth=50)
        self.result_table.column("Name", width=150, minwidth=100)
        self.result_table.column("Symptom", width=120, minwidth=80)
        self.result_table.column("Lehrkraft", width=150, minwidth=100)
        self.result_table.column("Status", width=100, minwidth=80)
        self.result_table.bind("<<TreeviewSelect>>", self.on_row_select)
        self.load_open_alerts()

        self.protokoll_data_by_item = {}

        self.refresh_button = tb.Button(
            self, text="Aktualisieren", command=self.load_open_alerts)
        self.refresh_button.pack(pady=10)

    def load_open_alerts(self):
                self.result_table.delete(*self.result_table.get_children())
                open_alerts = protokoll_crud.get_all_open_protokolls()
                for protokoll in open_alerts:
                    if isinstance(protokoll, dict):
                        status = str(protokoll.get("status", ""))
                        # Nur Einträge laden, deren Status mit "wf" beginnt
                        if not status.startswith("wf"):
                            continue

                        safe_values = (
                            str(protokoll.get("alert_id", "")),
                            str(protokoll.get("name", "")),
                            str(protokoll.get("symptom", "")),
                            str(protokoll.get("teacher", "")),
                            status,
                        )
                    elif isinstance(protokoll, str):
                        safe_values = protokoll.split(",")
                        # Status ist normalerweise das letzte Element
                        if len(safe_values) >= 5 and not safe_values[4].startswith("wf"):
                            continue
                    else:
                        safe_values = [str(v) for v in protokoll]
                        # Status ist normalerweise das 5. Element (Index 4)
                        if len(safe_values) >= 5 and not safe_values[4].startswith("wf"):
                            continue

                    item_id = self.result_table.insert(
                        "",
                        "end",
                        values=safe_values,
                    )

    def on_row_select(self, event):
        selected_item = self.result_table.focus()
        if selected_item:
            item_values = self.result_table.item(selected_item, "values")
            alert_id = item_values[0]
            print(f"Ausgewählter Alert ID: {alert_id}")
            self.controller.selected_alert = alert_id
            self.controller.show_frame("MaterialReturnPage")

class MaterialReturnPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        print(f"self.controller.selected_alert in MaterialReturnPage: {self.controller.selected_alert}")
        tb.Label(self, text="Material Rückgabe", font=("Exo 2 ExtraBold", 16)).pack(
            pady=20
        )
        self.result_table = tb.Treeview(self, columns=("Material", "Menge"), show="headings")
        self.result_table.pack(fill=BOTH, expand=True, padx=20, pady=20)
        self.result_table.heading("Material", text="Material")
        self.result_table.heading("Menge", text="Menge")
        tb.Button(
            self,
            text="einsatz abschließen",
            bootstyle="danger",
            width=20,
            command=self.complete_return,
        ).pack(pady=10)

    def load_materials(self):
        # Bestehende Einträge löschen
        for item in self.result_table.get_children():
            self.result_table.delete(item)

        # Materialien laden wenn selected_alert gesetzt ist
        if hasattr(self.controller, 'selected_alert') and self.controller.selected_alert:
            materials = get_materials_by_protokoll_id(convert_alert_to_protokoll_id(self.controller.selected_alert), True)
            for material in materials:
                self.result_table.insert("", "end", values=(material['name'], material['quantity']))

    def complete_return(self):#
        rerturned_mats = []
        for item in self.result_table.get_children():
            material_name, menge = self.result_table.item(item, "values")
            rerturned_mats.append((material_name, int(menge)))
            matrial_id = get_material_id_by_name(material_name)
            if matrial_id:
                add_material_quantity(matrial_id, int(menge))
        protokoll_crud.update_status(self.controller.selected_alert, "geschlossen")
        self.controller.show_frame("WaitingForMaterialPage")

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
        widget_frame.pack_propagate(True)  # Verhindert automatische Größenanpassung
        widget_frame.pack(padx=10, pady=10, expand=True)

        # Alarm-Informationen anzeigen (mit weißer Schrift)
        tb.Label(
            widget_frame,
            text=f"Alarm #{alert_id}",
            font=("Exo 2 Bold", 8),
            foreground="white",
            background=self.get_background_color(alert_type),
        ).pack(
            side=TOP, padx=5, pady=0
        )  # Reduzierter Abstand nach unten

        tb.Button(
            widget_frame,
            text="Einsatz übernehmen",
            bootstyle=f"{bg_color}",
            command=self.accept_alarm,
        ).pack(
            side=TOP, padx=5, pady=0
        )  # Reduzierter Abstand

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
            "info": "#0dcaf0",  # Blau
        }
        return colors.get(style_name, "#ffffff")


class HLWPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tb.Label(self, text="HLW Anleitung", font=("Exo 2 ExtraBold", 16)).pack(pady=20)
        instructions = (
            "1. Prüfen Sie die Umgebung auf Sicherheit.\n"
            "2. Überprüfen Sie die Atmung der Person.\n"
            "3. Rufen Sie den Notruf 112 an.\n"
            "4. Beginnen Sie mit der Herzdruckmassage:\n"
            "   - Platzieren Sie Ihre Hände in der Mitte der Brust.\n"
            "   - Drücken Sie kräftig und schnell (ca. 100-120 Mal pro Minute).\n"
            "5. Verwenden Sie einen Defibrillator, wenn verfügbar.\n"
            "6. Fahren Sie fort, bis professionelle Hilfe eintrifft."
        )
        tb.Label(self, text=instructions, font=("Exo 2", 12), justify=LEFT).pack(pady=10, padx=20)

        tb.Button(
            self,
            text="Start",
            bootstyle="primary",
            command=self.start_hlw,
        ).pack(pady=10)

    import time
    import threading
    import winsound

    import time
    import threading
    import winsound

    def start_hlw(self):
        print("HLW gestartet")

        # Hilfsfunktion: Spielt den Ton in einem eigenen Thread,
        # damit der Haupt-Rhythmus NICHT angehalten wird.
        def play_async_beep():
            try:
                # Daemon=True sorgt dafür, dass der Thread stirbt, wenn das Hauptprogramm endet
                threading.Thread(target=winsound.Beep, args=(800, 80), daemon=True).start()
            except:
                pass

        def hlw_loop():
            try:
                bpm = 100
                interval = 60.0 / bpm

                self.hlw_running = True

                # Startzeitpunkt
                next_beat_time = time.perf_counter()
                beat_count = 0

                # Wir berechnen die Zeiten VOR der Schleife vor, um Rechenzeit zu sparen
                while beat_count < 600 and self.hlw_running:

                    # --- 1. Warteschleife (Hybrid Sleep) ---
                    while True:
                        current_time = time.perf_counter()
                        remaining = next_beat_time - current_time

                        if remaining <= 0:
                            break

                        # Schlafen um CPU zu schonen, aber wach bleiben kurz vor Ziel
                        if remaining > 0.02:
                            time.sleep(remaining - 0.015)
                        else:
                            # Busy Wait für die letzten Millisekunden
                            pass

                    if not self.hlw_running:
                        break

                    # --- 2. Ton abfeuern (BLOCKIERT NICHT MEHR!) ---
                    # Wir rufen jetzt die asynchrone Funktion auf.
                    # Der Code läuft SOFORT weiter, ohne auf das Ende des Tons zu warten.
                    play_async_beep()

                    # Nächsten Zeitpunkt berechnen
                    beat_count += 1
                    next_beat_time += interval

            except Exception as e:
                print(f"HLW Fehler: {e}")
            finally:
                self.hlw_running = False
                print("HLW gestoppt")

        self.hlw_running = True
        # Der Haupt-Loop läuft in einem Thread, damit die GUI nicht einfriert
        hlw_thread = threading.Thread(target=hlw_loop, daemon=True)
        hlw_thread.start()

        def stop_hlw(self):
            if hasattr(self, 'hlw_running'):
                self.hlw_running = False
                print("HLW wird gestoppt...")
if __name__ == "__main__":
    app = App()
    app.mainloop()
