import ttkbootstrap as tb
from click import command
from ttkbootstrap import DateEntry
from ttkbootstrap.constants import *
import tkinter.font as tkFont
from tkinter import filedialog, messagebox
from Alert import alarm
from Data import patient_crud, alerts_crud, protokoll_crud, users_crud
import datetime

from PDF.pdf import main
import os



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
        self.geometry("1200x800")
        selected_alert = None
        # Navbar

        navbar = tb.Frame(self, style="dark")
        navbar.pack(side=TOP, fill=X)

        style = tb.Style()
        style.configure(
            "Custom.TLabel",
            background="#263238",
            foreground="#ffffff",
            font=("Exo 2 ExtraBold", 16),
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
        for F in (AlertPage, AboutPage, DetailPage, ElDataPage, UserManagementPage):
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

        tb.Button(self, text="Suchen", style="Custom.TButton", width=10, command=self.search_alerts).pack(pady=10)

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


        self.protokoll_data_by_item = {}  # Mapping von Treeview-Item-ID zu Protokoll-Daten

    def search_alerts(self):
        for item in self.result_table.get_children():
            self.result_table.delete(item)
        self.protokoll_data_by_item.clear()
        first_name = self.children['!placeholderentry'].get()
        last_name = self.children['!placeholderentry2'].get().strip()
        birth_date = datetime.datetime.strptime(self.search_birthdate_entry.entry.get(), "%d.%m.%Y").strftime("%d.%m.%Y")
        print(f"Suche nach Protokollen für: {first_name} {last_name}, Geburtsdatum: {birth_date}")
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
                    "", "end",
                    values=(
                        patient_crud.get_patient_by_pseudonym(protokoll["pseudonym"])["real_name"],
                        patient_crud.get_patient_by_pseudonym(protokoll["pseudonym"])["real_last_name"],
                        protokoll["operation_end"]
                    )
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

        tb.Label(self, text="Protokolldetails", font=("Exo 2 ExtraBold", 16)).pack(pady=20)
        self.detail_label = tb.Label(self, text="Details werden hier angezeigt")
        self.detail_label.pack(pady=10)
        self.pdf_button = tb.Button(self, text="Als PDF speichern", command=self.save_as_pdf)
        self.pdf_button.pack(pady=10)
        self.el_data_button = tb.Button(self, text="Einsatzleit-Protokol", command= self.save_el_data)
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
                title="Speicherort für PDF wählen")
            main(alert_id, file_path)
            if os.path.exists(file_path):
                if messagebox.askyesno("Öffnen", "PDF wurde erstellt. Möchten Sie die Datei öffnen?"):
                    os.startfile(file_path)
        else:
            print("Warnung: Keine alert_id gefunden. PDF wird trotzdem mit vorhanden Daten erstellt.")

    def save_el_data(self):
        self.controller.selected_alert = self.current_protokoll.get("alert_id")
        self.controller.show_frame("ElDataPage")


class ElDataPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tb.Label(self, text="Einsatzleit-Protokol", font=("Exo 2 ExtraBold", 16)).pack(pady=20)
        PlaceholderEntry(self, "Eltern benachrichtigt von").pack(pady=10)
        PlaceholderEntry(self, "Eltern benachrichtigt um").pack(pady=10)
        measure_combobox = tb.Combobox(self, values=["Rettungsdienst", "Taxifahrt ins KH/zum Arzt","Aleine nach hause" ])
        measure_combobox.set("Maßnahme")
        measure_combobox.bind("<<ComboboxSelected>>",  self.on_selection)
        measure_combobox.pack(pady=10)
        self.escort_person_entry = PlaceholderEntry(self, "Begleitperson")
        self.hospital_entry = PlaceholderEntry(self, "Krankenhaus")
        tb.Button(self, text="Speichern", style="success", width=10, command=self.save_data).pack(pady=10)



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
        notified_by = self.children['!placeholderentry'].get()
        notified_time = self.children['!placeholderentry2'].get()
        measure = self.children['!combobox'].get()
        escort_person = self.escort_person_entry.get()
        hospital = self.hospital_entry.get()
        time_obj = datetime.datetime.strptime(notified_time, "%H:%M").time()

        # Mit heutigem Datum kombinieren
        dt = datetime.datetime.combine(datetime.date.today(), time_obj)
        if measure == "Taxifahrt ins KH/zum Arzt" :
            updatet_measure = f"{measure} mit {escort_person}"
            protokoll_crud.add_pickup_measure_to_protokoll(self.controller.selected_alert, updatet_measure, notified_by, dt)
        elif measure == "Rettungsdienst":
            protokoll_crud.add_pickup_measure_to_protokoll(self.controller.selected_alert, measure, notified_by, dt)
            protokoll_crud.add_hospital_to_protokoll(self.controller.selected_alert, hospital)
        else:
            protokoll_crud.add_pickup_measure_to_protokoll(self.controller.selected_alert, measure, notified_by, dt)

class UserManagementPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        lehrer_liste = users_crud.get_all_teachers()
        tb.Label(self, text="Benutzerverwaltung", font=("Exo 2 ExtraBold", 16)).pack(pady=20)
        first_name_entry = PlaceholderEntry(self, "Vorname")
        first_name_entry.pack(pady=10)
        last_name_entry = PlaceholderEntry(self, "Nachname")
        last_name_entry.pack(pady=10)
        lb_combobox = tb.Combobox(self, values=lehrer_liste)
        lb_combobox.set("Lehrkraft")
        lb_combobox.pack(pady=10)
        card_number_entry = PlaceholderEntry(self, "Kartennummer")
        card_number_entry.pack(pady=10)
        role_combobox = tb.Combobox(self, values=["Admin", "User", "Junior"])
        role_combobox.set("Rolle")
        role_combobox.pack(pady=10)
        tb.Button(self, text="Benutzer hinzufügen", style="success", width=15, command=self.add_user).pack(pady=10)
        self.user_table = tb.Treeview(
            self, columns=("Vorname", "Nachname", "Lehrkraft", "Kartennummer", "Rolle"), show="headings"
        )

        self.user_table.heading("Vorname", text="Vorname")
        self.user_table.heading("Nachname", text="Nachname")
        self.user_table.heading("Lehrkraft", text="Lehrkraft")
        self.user_table.heading("Kartennummer", text="Kartennummer")
        self.user_table.heading("Rolle", text="Rolle")
        self.user_table.pack(pady=10, fill=BOTH, expand=True)
        self.load_users()

    # Python
    def load_users(self):
        users = users_crud.get_all_users()
        for user in users:
            # Alle Werte in Strings umwandeln und geschweifte Klammern ersetzen
            safe_values = [str(v).replace("{", "(").replace("}", ")") for v in user]
            self.user_table.insert(
                "", "end",
                values=safe_values
            )

        # Hier können Sie die Benutzerverwaltungsfunktionen hinzufügen



    def add_user(self):
        pass


















if __name__ == "__main__":

    app = App()
    app.mainloop()
