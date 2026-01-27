import datetime
import os
import tkinter.font as tkFont
from tkinter import filedialog, messagebox

import dotenv
import ttkbootstrap as tb
from click import command
from pyprinter import Printer
from ttkbootstrap import DateEntry
from ttkbootstrap.constants import *

from Data.setup_database import db_connection_error
from Alert import alarm

if db_connection_error:
    import sys
    print(f"FEHLER: Keine Datenbankverbindung: {db_connection_error}", file=sys.stderr)
    # Die tkinter MessageBox wird in der App-Klasse angezeigt

from Data import (alerts_crud, materials_crud, patient_crud, protokoll_crud,
              users_crud, settings_crud)
from Data.materials_crud import get_material_id_by_name, get_materials_by_protokoll_id, add_material_quantity
from Data.protokoll_crud import convert_alert_to_protokoll_id
from PDF.pdf import main
from rfid.rfid import read_rfid_uid


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
        super().__init__(themename="litera")
        self.title("SaniLink")
        self.geometry("1200x800")
        
        # Datenbankverbindung prüfen
        if db_connection_error:
            messagebox.showerror(
                "Datenbankfehler",
                f"Keine Verbindung zur Datenbank möglich:\n\n{db_connection_error}\n\n"
                "Bitte überprüfen Sie:\n"
                "- MySQL Server läuft\n"
                "- Zugangsdaten korrekt\n"
                "- Netzwerkverbindung"
            )
            self.destroy()
            return
        
        selected_alert = None
        self.selected_open_alert = None

        navbar = tb.Frame(self, style="dark")
        navbar.pack(side=TOP, fill=X)

        style = tb.Style("litera")
        style.configure(
            "Custom.TLabel",
            background="#263238",
            foreground="#ffffff",
            font=("Exo 2", 16, "bold")
        )

        tb.Label(
            navbar,
            text="SaniLink",
            font=("Exo 2 Black", 16),
            style="Custom.TLabel",
        ).pack(side=LEFT, padx=5, pady=5)

        tb.Button(
            navbar,
            text="Alarmierung",
            style="dark",
            command=lambda: self.show_frame("AlertPage"),
        ).pack(side=LEFT, padx=(100, 10), pady=5)

        tb.Button(
            navbar,
            text="Offene Einsätze",
            style="dark",
            command=lambda: self.show_frame("OpenAlertsPage"),
        ).pack(side=LEFT, padx=5, pady=5)

        tb.Button(
            navbar,
            text="Alarmsuche",
            style="dark",
            command=lambda: self.show_frame("AboutPage"),
        ).pack(side=LEFT, padx=5, pady=5)

        tb.Button(
            navbar,
            text="Benutzerverwaltung",
            style="dark",
            command=lambda: self.show_frame("UserManagementPage"),
        ).pack(side=LEFT, padx=5, pady=5)
        tb.Button(
            navbar,
            text="Materialverwaltung",
            style="dark",
            command=lambda: self.show_frame("MaterialManagementPage"),
        ).pack(side=LEFT, padx=5, pady=5)
        tb.Button(
            navbar,
            text="Einstellungen",
            style="dark",
            command=lambda: self.show_frame("SettingsPage"),
        ).pack(side=LEFT, padx=5, pady=5)

        tb.Button(navbar, text="Beenden", style="danger", command=self.destroy).pack(
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
        for F in (
            AlertPage,
            AboutPage,
            DetailPage,
            ElDataPage,
            UserManagementPage,
            MaterialManagementPage,
            SettingsPage,
            OpenAlertsPage,
            MaterialReturnPage
        ):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        # Startseite anzeigen
        self.show_frame("AlertPage")

    def show_frame(self, page_name):
        """Zeigt die gewünschte Seite an"""
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

        self.birth_entry = DateEntry(self)

        self.birth_entry.pack(pady=10)

        symptom_combobox = tb.Combobox(
            self, values=["Bauchweh", "Schwindel", "Erbrechen", "Übelkeit", "Kopfschmerzen", "Nasenbluten", "Verletzung Extimitäten"]
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


class AboutPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tb.Label(self, text="Alarmsuche", font=("Exo 2 ExtraBold", 16)).pack(pady=20)

        search_name_entry = PlaceholderEntry(self, "Name")
        search_name_entry.pack(pady=10)
        search_name_entry.focus()
        search_last_name_entry = PlaceholderEntry(self, "Nachname")
        search_last_name_entry.pack(pady=10)
        self.search_birthdate_entry = DateEntry(self)
        self.search_birthdate_entry.pack(pady=10)
        self.search_birthdate_entry.bind("<Return>",  self.search_alerts)

        tb.Button(
            self,
            text="Suchen",
            style="Custom.TButton",
            width=10,
            command=self.search_alerts,
        ).pack(pady=10)

        self.result_table = tb.Treeview(
            self, columns=("Name", "Nachname", "operation_end"), show="headings"
        )
        self.result_table.heading("Name", text="Name")
        self.result_table.heading("Nachname", text="Nachname")

        self.result_table.heading("operation_end", text="Einsatzende")
        self.result_table.pack(pady=10)

        # Scrollbar hinzufügen
        scrollbar = tb.Scrollbar(
            self, orient="vertical", command=self.result_table.yview
        )
        self.result_table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.result_table.pack(side="left", fill="both", expand=True)
        self.result_table.bind("<ButtonRelease-1>", self.on_row_click)

        self.protokoll_data_by_item = (
            {}
        )  # Mapping von Treeview-Item-ID zu Protokoll-Daten

    def search_alerts(self, event=None):
        for item in self.result_table.get_children():
            self.result_table.delete(item)
        self.protokoll_data_by_item.clear()
        first_name = self.children["!placeholderentry"].get()
        last_name = self.children["!placeholderentry2"].get().strip()
        birth_date = datetime.datetime.strptime(
            self.search_birthdate_entry.entry.get(), "%d.%m.%Y"
        ).strftime("%d.%m.%Y")
        print(
            f"Suche nach Protokollen für: {first_name} {last_name}, Geburtsdatum: {birth_date}"
        )
        if not first_name or not last_name or not birth_date:
            print("Bitte füllen Sie alle Felder aus.")
            return
        protokolls = protokoll_crud.get_protokolls_by_name(
            first_name, last_name, birth_date
        )
        if not protokolls:
            print("Keine Protokolle gefunden.")
            return
        else:
            for protokoll in protokolls:
                item_id = self.result_table.insert(
                    "",
                    "end",
                    values=(
                        patient_crud.get_patient_by_pseudonym(protokoll["pseudonym"])[
                            "real_name"
                        ],
                        patient_crud.get_patient_by_pseudonym(protokoll["pseudonym"])[
                            "real_last_name"
                        ],
                        protokoll["operation_end"],
                    ),
                )
                self.protokoll_data_by_item[item_id] = protokoll

    def on_row_click(self, event):
        item_id = self.result_table.identify_row(event.y)
        if item_id and item_id in self.protokoll_data_by_item:
            protokoll = self.protokoll_data_by_item[item_id]
            self.controller.show_frame("DetailPage")
            detail_page = self.controller.frames["DetailPage"]
            detail_page.show_details(protokoll)


# python
class DetailPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.current_protokoll = None  # Attribut initialisieren

        tb.Label(self, text="Protokolldetails", font=("Exo 2 ExtraBold", 16)).pack(
            pady=20
        )
        self.detail_label = tb.Label(self, text="Details werden hier angezeigt")
        self.detail_label.pack(pady=10)
        self.pdf_button = tb.Button(
            self, text="Als PDF speichern", command=self.save_as_pdf
        )
        self.pdf_button.pack(pady=10)
        self.el_data_button = tb.Button(
            self, text="Einsatzleit-Protokol", command=self.save_el_data
        )
        self.el_data_button.pack(pady=10)
        self.back_button = tb.Button(self, text="Back", command=self.show_back)
        self.back_button.pack(pady=10)

    def show_details(self, protokoll):
        # Protokoll merken (Kopie) und anzeigen
        self.current_protokoll = dict(protokoll)
        details = "\n".join(f"{k}: {v}" for k, v in self.current_protokoll.items())
        self.detail_label.config(text=details)

    def show_back(self):
        self.back_button.config(command=lambda: self.controller.show_frame("AboutPage"))

    def save_as_pdf(self):
        if not self.current_protokoll:
            print("Kein Protokoll geladen.")
            return

        alert_id = self.current_protokoll.get("alert_id")

        if alert_id:

            self.current_protokoll["alert_id"] = alert_id
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Dateien", "*.pdf")],
                initialfile="einsatz_protokoll.pdf",
                title="Speicherort für PDF wählen",
            )
            main(alert_id, file_path)
            if os.path.exists(file_path):
                if messagebox.askyesno(
                    "Öffnen", "PDF wurde erstellt. Möchten Sie die Datei öffnen?"
                ):
                    os.startfile(file_path)
        else:
            print(
                "Warnung: Keine alert_id gefunden. PDF wird trotzdem mit vorhanden Daten erstellt."
            )

    def save_el_data(self):
        self.controller.selected_alert = self.current_protokoll.get("alert_id")
        self.controller.show_frame("ElDataPage")


class ElDataPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tb.Label(self, text="Einsatzleit-Protokol", font=("Exo 2 ExtraBold", 16)).pack(
            pady=20
        )
        PlaceholderEntry(self, "Eltern benachrichtigt von").pack(pady=10)
        PlaceholderEntry(self, "Eltern benachrichtigt um").pack(pady=10)
        measure_combobox = tb.Combobox(
            self,
            values=["Rettungsdienst", "Taxifahrt ins KH/zum Arzt", "Aleine nach hause"],
        )
        measure_combobox.set("Maßnahme")
        measure_combobox.bind("<<ComboboxSelected>>", self.on_selection)
        measure_combobox.pack(pady=10)
        self.escort_person_entry = PlaceholderEntry(self, "Begleitperson")
        self.hospital_entry = PlaceholderEntry(self, "Krankenhaus")
        tb.Button(
            self, text="Speichern", style="success", width=10, command=self.save_data
        ).pack(pady=10)

    def on_selection(self, event):
        selection = event.widget.get()
        if selection == "Rettungsdienst":
            self.hospital_entry.pack(pady=10)
            self.escort_person_entry.forget()
        elif selection == "Taxifahrt ins KH/zum Arzt":
            self.escort_person_entry.pack(pady=10)
            self.hospital_entry.forget()
        else:
            self.escort_person_entry.forget()
            self.hospital_entry.forget()

    def save_data(self):
        notified_by = self.children["!placeholderentry"].get()
        notified_time = self.children["!placeholderentry2"].get()
        measure = self.children["!combobox"].get()
        escort_person = self.escort_person_entry.get()
        hospital = self.hospital_entry.get()
        time_obj = datetime.datetime.strptime(notified_time, "%H:%M").time()

        # Mit heutigem Datum kombinieren
        dt = datetime.datetime.combine(datetime.date.today(), time_obj)
        if measure == "Taxifahrt ins KH/zum Arzt":
            updatet_measure = f"{measure} mit {escort_person}"
            protokoll_crud.add_pickup_measure_to_protokoll(
                self.controller.selected_alert, updatet_measure, notified_by, dt
            )
        elif measure == "Rettungsdienst":
            protokoll_crud.add_pickup_measure_to_protokoll(
                self.controller.selected_alert, measure, notified_by, dt
            )
            protokoll_crud.add_hospital_to_protokoll(
                self.controller.selected_alert, hospital
            )
        else:
            protokoll_crud.add_pickup_measure_to_protokoll(
                self.controller.selected_alert, measure, notified_by, dt
            )


class UserManagementPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.selected_user = None
        self.controller = controller
        lehrer_liste = users_crud.get_all_teachers()
        tb.Label(self, text="Benutzerverwaltung", font=("Exo 2 ExtraBold", 16)).pack(
            pady=20
        )
        first_name_entry = PlaceholderEntry(self, "Vorname")
        first_name_entry.pack(pady=10)
        last_name_entry = PlaceholderEntry(self, "Nachname")
        last_name_entry.pack(pady=10)
        lb_combobox = tb.Combobox(self, values=lehrer_liste)
        lb_combobox.set("Lehrkraft")
        lb_combobox.pack(pady=10)
        card_number_entry = PlaceholderEntry(self, "Kartennummer")
        card_number_entry.pack(pady=10)
        card_number_entry.bind("<FocusIn>", self.read_card_number)
        role_combobox = tb.Combobox(self, values=["Admin", "User", "Junior"])
        role_combobox.set("Rolle")
        role_combobox.pack(pady=10)
        self.button_frame = tb.Frame(self)
        self.button_frame.pack(pady=10)
        self.add_user_button = tb.Button(
            self,
            text="Benutzer hinzufügen",
            style="success",
            width=20,
            command=self.add_user,
        )
        self.add_user_button.pack(pady=10)
        self.update_user_button = tb.Button(
            self,
            text="Benutzer aktualisieren",
            style="warning",
            width=20,
            command=self.update_user,
        )
        self.delete_user_button = tb.Button(
            self,
            text="Benutzer löschen",
            style="danger",
            width=20,
            command=self.delete_user,
        )

        self.user_table = tb.Treeview(
            self,
            columns=("ID", "Vorname", "Nachname", "Lehrkraft", "Kartennummer", "Rolle"),
            show="headings",
        )

        self.user_table.heading("ID", text="ID")
        self.user_table.heading("Vorname", text="Vorname")
        self.user_table.heading("Nachname", text="Nachname")
        self.user_table.heading("Lehrkraft", text="Lehrkraft")
        self.user_table.heading("Kartennummer", text="Kartennummer")
        self.user_table.heading("Rolle", text="Rolle")
        self.user_table.pack(pady=10, fill=BOTH, expand=True)
        self.load_users()
        self.user_table.bind("<ButtonRelease-1>", self.on_row_click)
        self.user_table.bind("<Double-1>", self.on_double_click)

    # Python
    def load_users(self):
        self.user_table.delete(*self.user_table.get_children())
        users = users_crud.get_all_active_users()
        for user in users:
            if isinstance(user, dict):
                # Werte in der Reihenfolge der Spalten extrahieren
                safe_values = [
                    str(user.get("User_ID", "")),
                    str(user.get("name", "")),
                    str(user.get("last_name", "")),
                    str(user.get("lernbegleiter", "")),
                    str(user.get("karten_nummer", "")),
                    str(user.get("permission", "")),
                ]
            elif isinstance(user, str):
                safe_values = user.split(",")
            else:
                safe_values = [str(v) for v in user]
                # Alle Einträge löschen

            self.user_table.insert("", "end", values=safe_values)

    def add_user(self):
        first_name = self.children["!placeholderentry"].get().strip()
        last_name = self.children["!placeholderentry2"].get().strip()
        lernbegleiter = self.children["!combobox"].get().strip()
        if " " in lernbegleiter:
            lernbegleiter_first_name, lernbegleiter_last_name = lernbegleiter.split()
            teacher = users_crud.get_teacher_by_name(
                lernbegleiter_first_name, lernbegleiter_last_name
            )
        else:
            teacher = users_crud.get_teacher_by_name(lernbegleiter)
        teacher_id = teacher["teacher_id"] if teacher else None
        card_number = self.children["!placeholderentry3"].get().strip()
        role = self.children["!combobox2"].get().strip()

        if (
            not first_name
            or not last_name
            or lernbegleiter == "Lehrkraft"
            or not card_number
            or role == "Rolle"
        ):
            messagebox.showerror("Fehler", "Bitte füllen Sie alle Felder aus.")
            return

        existing_user = users_crud.get_user_by_card_number(card_number)
        if existing_user:
            messagebox.showerror(
                "Fehler", "Ein Benutzer mit dieser Kartennummer existiert bereits."
            )

        users_crud.add_user(first_name, last_name, teacher_id, card_number, role)
        messagebox.showinfo("Erfolg", "Benutzer erfolgreich hinzugefügt.")
        self.user_table.delete(*self.user_table.get_children())
        self.load_users()

    # Python
    def on_row_click(self, event):
        item_id = self.user_table.identify_row(event.y)
        if item_id:
            selected_user_data = self.user_table.item(item_id, "values")
            self.selected_user = selected_user_data[0]
            print(self.selected_user)
            if users_crud.get_teacher_name_by_id(selected_user_data[3]):
                lernbegleiter_name = users_crud.get_teacher_name_by_id(
                    selected_user_data[3]
                )
            else:
                lernbegleiter_name = "Nicht zugewiesen"

            # Daten in die Entry-Felder einsetzen
            self.children["!placeholderentry"].delete(0, "end")
            self.children["!placeholderentry"].insert(0, selected_user_data[1])
            self.children["!placeholderentry2"].delete(0, "end")
            self.children["!placeholderentry2"].insert(0, selected_user_data[2])
            self.children["!combobox"].set(lernbegleiter_name)
            self.children["!placeholderentry3"].delete(0, "end")
            self.children["!placeholderentry3"].insert(0, selected_user_data[4])
            self.children["!combobox2"].set(selected_user_data[5])

            # Vorherige Buttons entfernen
            for widget in self.button_frame.winfo_children():
                widget.pack_forget()
            # Buttons jetzt sichtbar machen
            self.update_user_button.pack(in_=self.button_frame, side=LEFT, padx=5)
            self.delete_user_button.pack(in_=self.button_frame, side=LEFT, padx=5)

    # Python
    def on_double_click(self, event):
        # Alle Selektionen aufheben
        for item in self.user_table.selection():
            self.user_table.selection_remove(item)

        # selected_user zurücksetzen
        self.selected_user = None

        # Buttons verstecken
        for widget in self.button_frame.winfo_children():
            widget.pack_forget()

    def update_user(self):  # Ohne (self, event)
        if self.selected_user:
            print(f"Benutzer aktualisieren: {self.selected_user}")
            first_name = self.children["!placeholderentry"].get().strip()
            last_name = self.children["!placeholderentry2"].get().strip()
            lernbegleiter = self.children["!combobox"].get().strip()
            if lernbegleiter != "Lehrkraft":
                if " " in lernbegleiter:
                    lernbegleiter_first_name, lernbegleiter_last_name = (
                        lernbegleiter.split()
                    )
                    teacher = users_crud.get_teacher_by_name(
                        lernbegleiter_first_name, lernbegleiter_last_name
                    )
                else:
                    teacher = users_crud.get_teacher_by_name(lernbegleiter)
                teacher_id = teacher["teacher_id"] if teacher else None
            else:
                teacher_id = None

            card_number = self.children["!placeholderentry3"].get().strip()
            role = self.children["!combobox2"].get().strip()

            users_crud.update_user(
                self.selected_user, first_name, last_name, teacher_id, card_number, role
            )

    def delete_user(self):  # Ohne (self, event)
        if self.selected_user:
            print(f"Benutzer löschen: {self.selected_user}")
            users_crud.delete_user(self.selected_user)
            self.load_users()
        else:
            print("Kein Benutzer ausgewählt")

    def read_card_number(self, event):

        card_number = read_rfid_uid()
        if card_number:
            self.children["!placeholderentry3"].delete(0, "end")
            self.children["!placeholderentry3"].insert(0, card_number)
        else:
            messagebox.showerror("Fehler", "Keine Kartennummer gelesen.")

class SettingsPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tb.Label(self, text="Einstellungen", font=("Exo 2 ExtraBold", 16)).pack(
            pady=20
        )

        api_frame = tb.LabelFrame(self, text="API")
        api_frame.pack(pady=10, padx=10, fill="x")
        radio_frame = tb.Frame(api_frame)
        radio_frame.pack(pady=10, padx=10, fill="x")
        self.selected_option = tb.StringVar(value="Option 1")
        tb.Radiobutton(
            radio_frame,
            text="Divera 24/7",
            variable=self.selected_option,
            value="Option 1",
            bootstyle="info",
            command= self.on_Radiobutton_select
        ).pack(pady=10, anchor="w")

        tb.Radiobutton(
            radio_frame,
            text="ntfy",
            variable=self.selected_option,
            value="Option 2",
            bootstyle="info",
            command= self.on_Radiobutton_select
        ).pack(pady=10, anchor="w")

        key_frame = tb.Frame(api_frame)
        key_frame.pack(pady=10, padx=10, fill="x")

        self.key_label = (tb.Label(key_frame, text="API-Schlüssel:"))
        self.key_label.pack(side="left", padx=10, pady=10)

        self.api_entry = tb.Entry(key_frame, width=50, )
        self.api_entry.pack(side="left", padx=10, pady=10)



        rci = tb.Frame(api_frame)
        rci.pack(pady=10, padx=10, fill="x")

        self.rci_label = tb.Label(rci, text="RCI:")


        self.rci_entry = tb.Entry(rci, width=50, )


        tb.Button(
            api_frame,
            text="Speichern",
            style="success",
            command= self.save_settings,
        ).pack(side="left", padx=10, pady=10)


    def save_settings(self):
        method = self.selected_option.get()
        api_key = self.api_entry.get().strip()
        if method == "Option 1":
            divera_ric = self.rci_entry.get().strip()
            settings_crud.add_divera_settings(api_key, divera_ric)
        else:
            settings_crud.add_ntfy_settings(api_key)
        settings_crud.add_notification_method(method)
        messagebox.showinfo("Erfolg", "Einstellungen erfolgreich gespeichert.")

    def on_Radiobutton_select(self):
        selected = self.selected_option.get()
        print(selected)
        if selected == "Option 1":
            print("Divera 24/7 ausgewählt")
            self.rci_label.pack(side="left", padx=10, pady=10)
            self.rci_entry.pack(side="left", padx=63, pady=10)
            self.key_label.config(text="API-Schlüssel:")

        else:
            print("ntfy ausgewählt")
            self.rci_entry.forget()
            self.rci_label.forget()
            self.key_label.configure(text="Ntfy Topic:")



class MaterialManagementPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.selected_material = None
        self.is_reuseable = tb.BooleanVar()
        tb.Label(self, text="Materialverwaltung", font=("Exo 2 ExtraBold", 16)).pack(
            pady=20
        )
        # Weitere Widgets und Logik für die Materialverwaltung hier hinzufügent
        left_frame = tb.Frame(self)
        left_frame.pack(side="left", fill="both", expand=True)

        # Rechter Frame mit Treeview
        right_frame = tb.Frame(self)
        right_frame.pack(side="right", fill="both", expand=True)
        self.material_treeview = tb.Treeview(right_frame)
        self.material_treeview.pack(pady=10, fill=BOTH)

        scrollbar = tb.Scrollbar(
            right_frame, orient="vertical", command=self.material_treeview.yview
        )
        self.material_treeview.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.material_treeview.pack(side="left", fill="both", expand=True)
        self.material_treeview.bind("<<TreeviewSelect>>", self.on_row_click)
        self.material_treeview.bind("<Button-3>", self.deselect_all)
        # Spalten definieren
        self.material_treeview["columns"] = (
            "ID",
            "Name",
            "Menge",
            "Mindestvorrat",
            "Ablaufdatum",
        )
        self.material_treeview["show"] = (
            "headings"  # Blendet die erste leere Spalte aus
        )

        # Spaltenbreiten mit column() (nicht columnconfigure!)
        self.material_treeview.column("ID", width=50, minwidth=50, stretch=False)
        self.material_treeview.column("Name", width=150, minwidth=100, stretch=True)
        self.material_treeview.column("Menge", width=100, minwidth=80, stretch=False)
        self.material_treeview.column(
            "Mindestvorrat", width=100, minwidth=80, stretch=False
        )
        self.material_treeview.column(
            "Ablaufdatum", width=150, minwidth=100, stretch=True
        )

        # Überschriften
        self.material_treeview.heading("ID", text="ID")
        self.material_treeview.heading("Name", text="Name")
        self.material_treeview.heading("Menge", text="Menge")
        self.material_treeview.heading("Mindestvorrat", text="Mindestvorrat")
        self.material_treeview.heading("Ablaufdatum", text="Ablaufdatum")

        self.name_entry = PlaceholderEntry(left_frame, "Materialname")
        self.name_entry.pack(pady=10)

        self.quantity_entry = PlaceholderEntry(left_frame, "Menge")
        self.quantity_entry.pack(pady=10)

        self.min_quantity_entry = PlaceholderEntry(left_frame, "Mindestvorrat")
        self.min_quantity_entry.pack(pady=10)

        self.expiration_entry = DateEntry(left_frame)
        self.expiration_entry.pack(pady=10)

        self.reusable_button = tb.Checkbutton(left_frame, bootstyle="round-toggle" , text="Wiederverwendbar", variable=self.is_reuseable, command=self.on_is_reuseable_change)
        self.reusable_button.pack(pady=10)

        # Button-Frame für die Aktionen
        button_frame = tb.Frame(left_frame)
        button_frame.pack(pady=10, padx=100)

        add_button = tb.Button(
            button_frame,
            text="Hinzufügen",
            style="success",
            width=15,
            command=self.add_material,
        )
        add_button.pack(pady=5)

        update_button = tb.Button(
            button_frame,
            text="Aktualisieren",
            style="warning",
            width=15,
            command=self.update_material,
        )
        update_button.pack(pady=5)

        delete_button = tb.Button(
            button_frame,
            text="Löschen",
            style="danger",
            width=15,
            command=self.delete_material,
        )
        delete_button.pack(pady=5)

        clear_button = tb.Button(
            button_frame,
            text="Felder leeren",
            style="secondary",
            width=15,
            command=self.clear_fields,
        )
        clear_button.pack(pady=5)

        self.load_materials(self.material_treeview)

    def load_materials(self, treeview):
        treeview.delete(*treeview.get_children())
        materials = materials_crud.get_all_materials()

        # Tag für rote Schrift definieren
        treeview.tag_configure("low_stock", foreground="red")
        treeview.tag_configure("expired", foreground="#FFA500")
        current_date = datetime.datetime.now().date()
        for material in materials:
            if isinstance(material, dict):
                safe_values = [
                    str(material.get("material_id", "")),
                    str(material.get("material_name", "")),
                    str(material.get("quantity", "")),
                    str(material.get("minimum_stock", "")),
                    str(material.get("expires_at", "")),
                ]
            elif isinstance(material, str):
                safe_values = material.split(",")
            else:
                safe_values = [str(v) for v in material]

            tags = []

            if int(safe_values[2]) <= int(safe_values[3]):  # Menge <= Mindestvorrat
                tags.append("low_stock")

            # Ablaufdatum prüfen und parsen
            if safe_values[4] and safe_values[4] != "None":
                try:
                    expiration_date = datetime.datetime.strptime(safe_values[4], "%Y-%m-%d %H:%M:%S").date()
                    if expiration_date < current_date:
                        tags.append("expired")
                except ValueError:
                    print(f"Ungültiges Datumsformat: {safe_values[4]}")
            else:
                expiration_date = None

            treeview.insert("", "end", values=safe_values, tags=tuple(tags))







    def on_row_click(self, event):
        selected = self.material_treeview.selection()
        if selected:
            selected_material_data = self.material_treeview.item(selected[0], "values")
            self.selected_material = selected_material_data[0]

            # Felder füllen
            self.name_entry.delete(0, "end")
            self.name_entry.insert(0, selected_material_data[1])

            self.quantity_entry.delete(0, "end")
            self.quantity_entry.insert(0, selected_material_data[2])

            self.min_quantity_entry.delete(0, "end")
            self.min_quantity_entry.insert(0, selected_material_data[3])

            # Datum konvertieren: von YYYY-MM-DD HH:MM:SS zu DD.MM.YY
            date_str = str(selected_material_data[4])
            try:
                date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                formatted_date = date_obj.strftime("%d.%m.%y")
                self.expiration_entry.entry.delete(0, "end")
                self.expiration_entry.entry.insert(0, formatted_date)
            except ValueError:
                self.expiration_entry.entry.delete(0, "end")
                self.expiration_entry.entry.insert(0, date_str)

            print(f"Ausgewähltes Material: {self.selected_material}")

    def deselect_all(self, event):
        # Prüfen ob auf leeren Bereich geklickt wurde
        item_id = self.material_treeview.identify_row(event.y)
        if not item_id:
            # Auf leeren Bereich geklickt -> alles deselektieren
            self.material_treeview.selection_remove(self.material_treeview.selection())
            self.selected_material = None
            self.clear_fields()
            print("Auswahl aufgehoben")

    def clear_fields(self):
        """Leert alle Eingabefelder"""
        self.name_entry.delete(0, "end")
        self.name_entry._add_placeholder(None)

        self.quantity_entry.delete(0, "end")
        self.quantity_entry._add_placeholder(None)

        self.min_quantity_entry.delete(0, "end")
        self.min_quantity_entry._add_placeholder(None)

        self.expiration_entry.entry.delete(0, "end")
        self.selected_material = None

    def add_material(self):
            """Fügt ein neues Material hinzu"""
            try:
                name = self.name_entry.get().strip()
                is_reuseable = self.is_reuseable.get()
                if not name or name == "Materialname":
                    messagebox.showerror("Fehler", "Bitte geben Sie einen Materialnamen ein.")
                    return

                quantity_str = self.quantity_entry.get().strip()
                if not quantity_str or quantity_str == "Menge":
                    messagebox.showerror("Fehler", "Bitte geben Sie eine Menge ein.")
                    return
                quantity = int(quantity_str)

                min_quantity_str = self.min_quantity_entry.get().strip()
                if not min_quantity_str or min_quantity_str == "Mindestvorrat":
                    messagebox.showerror("Fehler", "Bitte geben Sie einen Mindestvorrat ein.")
                    return
                min_quantity = int(min_quantity_str)

                expiration = self.expiration_entry.entry.get().strip()
                if not expiration and not is_reuseable:
                    messagebox.showerror("Fehler", "Bitte geben Sie ein Ablaufdatum ein.")
                    return

                if expiration and not is_reuseable:
                    expiration_date = datetime.datetime.strptime(expiration, "%d.%m.%y").date()
                else:
                    expiration_date = None



                # Material hinzufügen
                materials_crud.add_material(name, quantity, min_quantity, expiration_date, is_reuseable)
                messagebox.showinfo("Erfolg", "Material erfolgreich hinzugefügt.")
                self.load_materials(self.material_treeview)
                self.clear_fields()

            except ValueError as e:
                error_msg = str(e)
                if "invalid literal for int()" in error_msg:
                    messagebox.showerror("Fehler", "Menge und Mindestvorrat müssen Zahlen sein.")
                elif "time data" in error_msg or "does not match format" in error_msg:
                    messagebox.showerror("Fehler", "Ungültiges Datumsformat. Verwenden Sie TT.MM.JJ (z.B. 25.12.24)")
                else:
                    messagebox.showerror("Fehler", f"Ungültige Eingabe: {error_msg}")
            except Exception as e:
                messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten: {str(e)}")

    def update_material(self):
        """Aktualisiert ein ausgewähltes Material"""
        if not self.selected_material:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Material aus der Liste aus.")
            return

        try:
            name = self.name_entry.get().strip()
            if not name or name == "Materialname":
                messagebox.showerror("Fehler", "Bitte geben Sie einen Materialnamen ein.")
                return

            quantity_str = self.quantity_entry.get().strip()
            if not quantity_str or quantity_str == "Menge":
                messagebox.showerror("Fehler", "Bitte geben Sie eine Menge ein.")
                return
            quantity = int(quantity_str)

            min_quantity_str = self.min_quantity_entry.get().strip()
            if not min_quantity_str or min_quantity_str == "Mindestvorrat":
                messagebox.showerror("Fehler", "Bitte geben Sie einen Mindestvorrat ein.")
                return
            min_quantity = int(min_quantity_str)

            expiration = self.expiration_entry.entry.get().strip()
            if not expiration:
                messagebox.showerror("Fehler", "Bitte geben Sie ein Ablaufdatum ein.")
                return

            # Datum in das richtige Format konvertieren
            expiration_date = datetime.datetime.strptime(expiration, "%d.%m.%y").strftime("%Y-%m-%d")

            # Material aktualisieren
            materials_crud.update_material(
                self.selected_material,
                name,
                quantity,
                expiration_date,
                min_quantity
            )
            messagebox.showinfo("Erfolg", "Material erfolgreich aktualisiert.")
            self.load_materials(self.material_treeview)
            self.clear_fields()

        except ValueError as e:
            error_msg = str(e)
            if "invalid literal for int()" in error_msg:
                messagebox.showerror("Fehler", "Menge und Mindestvorrat müssen Zahlen sein.")
            elif "time data" in error_msg or "does not match format" in error_msg:
                messagebox.showerror("Fehler", "Ungültiges Datumsformat. Verwenden Sie TT.MM.JJ (z.B. 25.12.24)")
            else:
                messagebox.showerror("Fehler", f"Ungültige Eingabe: {error_msg}")
        except Exception as e:
            messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten: {str(e)}")

    def delete_material(self):
        """Löscht ein ausgewähltes Material"""
        if not self.selected_material:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Material aus der Liste aus.")
            return

        # Bestätigung vom Benutzer einholen
        selected = self.material_treeview.selection()
        if selected:
            selected_material_data = self.material_treeview.item(selected[0], "values")
            material_name = selected_material_data[1]

            confirm = messagebox.askyesno(
                "Löschen bestätigen",
                f"Möchten Sie das Material '{material_name}' wirklich löschen?"
            )

            if confirm:
                try:
                    materials_crud.delete_material(self.selected_material)
                    messagebox.showinfo("Erfolg", "Material erfolgreich gelöscht.")
                    self.load_materials(self.material_treeview)
                    self.clear_fields()
                except Exception as e:
                    messagebox.showerror("Fehler", f"Fehler beim Löschen: {str(e)}")

    def on_is_reuseable_change(self):
        if self.is_reuseable.get():
            self.expiration_entry.entry.delete(0, "end")
            self.expiration_entry.state(["disabled"])  # Zustand auf "disabled" setzen
        else:
            self.expiration_entry.state(["!disabled"])  # Zustand auf "normal" setzen

class OpenAlertsPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tb.Label(self, text="Offene Alarme", font=("Exo 2 ExtraBold", 16)).pack(
            pady=20
        )
        self.meter_frame = tb.Frame(self)
        self.meter_frame.pack(pady=10)

        self.open_alerts_meter = tb.Meter(self.meter_frame, bootstyle="success", subtext="Offene Alarme", amountused=5, amounttotal=10)
        self.open_alerts_meter.pack(pady=10, side="left", padx=20)

        self.waiting_alerts_meter = tb.Meter(self.meter_frame, bootstyle="warning", subtext="Wartende Alarme", amountused=2, amounttotal=10)
        self.waiting_alerts_meter.pack(pady=10, )



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
        self.result_table.bind("<<TreeviewSelect>>", self.on_row_click)
        self.load_open_alerts()

        self.protokoll_data_by_item = {}

        self.refresh_button = tb.Button(
            self, text="Aktualisieren", command=self.load_open_alerts)
        self.refresh_button.pack(pady=10)
    def load_open_alerts(self):
        self.result_table.delete(*self.result_table.get_children())
        open_alerts = protokoll_crud.get_all_open_protokolls()
        waiting_alerts = []
        for protokoll in open_alerts:
            if isinstance(protokoll, dict):
                safe_values = (
                    str(protokoll.get("alert_id", "")),
                    str(protokoll.get("name", "")),
                    str(protokoll.get("symptom", "")),
                    str(protokoll.get("teacher", "")),
                    str(protokoll.get("status", "")),
                )
            elif isinstance(protokoll, str):
                safe_values = protokoll.split(",")
            else:
                safe_values = [str(v) for v in protokoll]#
            if safe_values[4].startswith("wf"):
                waiting_alerts.append(protokoll)

            item_id = self.result_table.insert(
                "",
                "end",
                values=safe_values,
            )
        self.open_alerts_meter.configure(amountused=len(open_alerts))
        self.waiting_alerts_meter.configure(amountused=len(waiting_alerts))

    def on_row_click(self, event):
        print("on_row_click")
        # Verwende selection() anstatt identify_row() für TreeviewSelect-Events
        selected_items = self.result_table.selection()
        print(f"Selected items: {selected_items}")

        if selected_items:
            item_id = selected_items[0]  # Erstes ausgewähltes Element
            selected_alert_data = self.result_table.item(item_id, "values")
            print(selected_alert_data[4])
            if selected_alert_data[4].startswith("wf"):
                self.controller.selected_open_alert = selected_alert_data[0]
                print(f"Ausgewählter Alert: {self.controller.selected_open_alert}")
                self.controller.show_frame("MaterialReturnPage")

class MaterialReturnPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
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

    def tkraise(self, aboveThis=None):
        """Überschreibt tkraise um Materialien zu laden wenn die Seite angezeigt wird"""
        super().tkraise(aboveThis)
        self.load_materials()

    def load_materials(self):
        # Bestehende Einträge löschen
        for item in self.result_table.get_children():
            self.result_table.delete(item)

        # Materialien laden wenn selected_open_alert gesetzt ist
        if hasattr(self.controller, 'selected_open_alert') and self.controller.selected_open_alert:
            materials = get_materials_by_protokoll_id(convert_alert_to_protokoll_id(self.controller.selected_open_alert), True)
            for material in materials:
                self.result_table.insert("", "end", values=(material['name'], material['quantity']))

    def complete_return(self):
        rerturned_mats = []
        for item in self.result_table.get_children():
            material_name, menge = self.result_table.item(item, "values")
            rerturned_mats.append((material_name, int(menge)))
            matrial_id = get_material_id_by_name(material_name)
            if matrial_id:
                add_material_quantity(matrial_id, int(menge))
        protokoll_crud.update_status(self.controller.selected_open_alert, "geschlossen")
        OpenAlertsPage.load_open_alerts()
        self.controller.show_frame("OpenAlertsPage")

if __name__ == "__main__":
    dotenv.load_dotenv(dotenv_path=r"C:\Users\cleme\Desktop\JugendForscht\Jugendforscht_ASW_2025\sanilink.env")
    app = App()
    app.mainloop()

