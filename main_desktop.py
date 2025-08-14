import ttkbootstrap as tb
from ttkbootstrap import DateEntry
from ttkbootstrap.constants import *
import tkinter.font as tkFont
from Alert import alarm
from Data import patient_crud, alerts_crud



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
            text="El Protokol",
            style="dark",
            command=lambda: self.show_frame("AboutPage"),
        ).pack(side=LEFT, padx=5, pady=5)
        tb.Button(
            navbar,
            text="Benutzerverwaltung",
            style="dark",
            command=lambda: self.show_frame("AboutPage"),
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
        for F in (AlertPage, AboutPage):
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
        birthday = self.birth_entry.entry.get()
        symptom = self.children['!combobox'].get()
        alert_type = self.children['!combobox2'].get()
        is_alert_without_name = self.alert_without_name_var.get()

        if symptom == "Symptome" or alert_type == "Alarmtyp":
            print("Bitte wählen Sie ein Symptom und einen Alarmtyp aus.")
            return

        if is_alert_without_name:
            alert_id = alarm.add_alert(symptom, alert_type)
            print("Alarm ohne Name ausgelöst.")
        else:
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
        tb.Button(self, text="Suchen", style="Custom.TButton", width=10).pack(pady=10)

        self.result_table = tb.Treeview(
            self, columns=("Name", "Nachname", "Symptome"), show="headings"
        )
        self.result_table.heading("Name", text="Name")
        self.result_table.heading("Nachname", text="Nachname")
        self.result_table.heading("Symptome", text="Symptome")
        self.result_table.pack(pady=10)
        self.result_table.insert("", "end", values=("Max", "Mustermann", "Symptom 1"))
        self.result_table.insert("", "end", values=("Erika", "Mustermann", "Symptom 2"))
        self.result_table.insert("", "end", values=("Hans", "Mustermann", "Symptom 3"))

        # Scrollbar hinzufügen
        scrollbar = tb.Scrollbar(
            self, orient="vertical", command=self.result_table.yview
        )
        self.result_table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.result_table.pack(side="left", fill="both", expand=True)
        self.result_table.bind("<ButtonRelease-1>", self.on_row_click)

    def on_row_click(self, event):
        # Ermittelt die ID der angeklickten Zeile
        item_id = self.result_table.identify_row(event.y)
        if item_id:
            # Holt die Werte der angeklickten Zeile
            values = self.result_table.item(item_id, "values")
            print(f"Angeklickte Zeile: {values}")


if __name__ == "__main__":

    app = App()
    app.mainloop()
