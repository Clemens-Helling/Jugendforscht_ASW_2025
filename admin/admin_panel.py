
# file: admin/admin_panel.py
import ttkbootstrap as tb
from ttkbootstrap import DateEntry
from ttkbootstrap.constants import *
import tkinter as tk

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
        selected_alert = None
        self.selected_open_alert = None

        navbar = tb.Frame(self, style="dark")
        navbar.pack(side=TOP, fill=X)

        style = tb.Style("litera")
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
            text="Metrics",
            style="dark",
            command=lambda: self.show_frame("MetricsPage"),
        ).pack(side=LEFT, padx=(100, 10), pady=5)

        tb.Button(
            navbar,
            text="Logs",
            style="dark",
            command=lambda: self.show_frame("LogPage"),
        ).pack(side=LEFT, padx=(100, 10), pady=5)

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
            MetricsHistoryPage,
            MetricsPage,
            LogPage,
        ):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        # Startseite anzeigen
        self.show_frame("MetricsPage")

    def show_frame(self, page_name):
        """Zeigt die gewünschte Seite an"""
        frame = self.frames[page_name]
        frame.tkraise()

class MetricsHistoryPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        from admin.data_client import create_dashboard

        SERVER = "http://192.168.178.112:5000/metrics"

        # Stil für den Hintergrund definieren
        tb.Label(self, text="Metrics", font=("Exo 2 ExtraBold", 16)).pack(pady=20)

        # top or left controls
        # use tkinter.Frame here because ttk frames don't accept the 'bg' option
        control_frame = tk.Frame(self, width=300, height=800, bg="#eee")
        control_frame.pack(side=LEFT, fill=Y)

        # main area where dashboard frames live
        main_frame = tk.Frame(self)
        main_frame.pack(side=RIGHT, fill=BOTH, expand=True)

        # create a frame for the graphs inside the main area
        graphs_frame = tk.Frame(main_frame)
        graphs_frame.pack(fill=BOTH, expand=True)

        # embed dashboard into graphs_frame
        canvas, ani = create_dashboard(graphs_frame, SERVER, interval=1000)

        # keep a reference to the animation to prevent garbage collection
        graphs_frame._ani = ani

class MetricsPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tb.Label(self, text="Metrics Page", font=("Exo 2 ExtraBold", 16)).pack(pady=20)

        self.cpu_meter = tb.Meter(
            self,
            metersize=200,
            amountused=0,
            metertype="full",
            subtext="CPU Usage",
            bootstyle="success",
            textright="%"
        )
        self.cpu_meter.pack(pady=20)

        self.ram_meter = tb.Meter(
            self,
            metersize=200,
            amountused=0,
            metertype="full",
            subtext="RAM Usage",
            bootstyle="success",
            textright="%"
        )
        self.ram_meter.pack(pady=20)

        self.history_button = tb.Button(self, text="Go to History", command=lambda: controller.show_frame("MetricsHistoryPage"))
        self.history_button.pack(pady=10)

        # start periodic updates
        self.update()

def update(self):
    """Refresh the meters every second with latest CPU and RAM values."""
    cpu = 0
    ram = 0
    try:
        import requests
        resp = requests.get("http://192.168.178.112:5000/metrics/cpu", timeout=1)
        data = resp.json()
        if isinstance(data, dict):
            cpu = data.get("cpu", 0)
            ram = data.get("ram", 0)
        else:
            cpu = data
            ram = 0
    except Exception:
        # keep defaults on any error (network/JSON/etc.)
        cpu = 0
        ram = 0

    try:
        self.cpu_meter.configure(amountused=float(cpu))
        self.ram_meter.configure(amountused=float(ram))
    except Exception:
        pass

        self.after(1000, self.update)

class LogPage(tb.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        tb.Label(self, text="Log Page", font=("Exo 2 ExtraBold", 16)).pack(pady=20)
        self.log_table = tb.Treeview(
            self, columns=("Time", "Level", "Message", "Client"), show="headings"
        )
        # Scrollbar hinzufügen
        scrollbar = tb.Scrollbar(
            self, orient="vertical", command=self.log_table.yview
        )
        self.log_table.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.log_table.pack(side="left", fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()
