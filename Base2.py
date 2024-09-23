import tkinter as tk

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mehrseitige Anwendung")
        self.geometry("1000x600")

        # Hier wird ein Container erstellt, in dem alle Seiten platziert werden.
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        # Layout für den Container festlegen
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Hier wird ein Dictionary erstellt, das alle Seiten speichert.
        self.frames = {}

        # Initialisierung der verschiedenen Seiten
        for F in (LoginPage, PageOne, PageTwo):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # Die Seiten werden alle übereinander in das Grid gelegt
            frame.grid(row=0, column=0, sticky="nsew")

        # Erste Seite anzeigen
        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Zeige den Frame der angegebenen Seite an'''
        frame = self.frames[page_name]
        frame.tkraise()


class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = tk.Label(self, text="Startseite", font=('Helvetica', 18))
        label.pack(pady=10, padx=10)

        button1 = tk.Button(self, text="Gehe zu Seite 1",
                            command=lambda: controller.show_frame("PageOne"))
        button1.pack()

        button2 = tk.Button(self, text="Gehe zu Seite 2",
                            command=lambda: controller.show_frame("PageTwo"))
        button2.pack()


class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = tk.Label(self, text="Seite 1", font=('Helvetica', 18))
        label.pack(pady=10, padx=10)

        button = tk.Button(self, text="Zurück zur Startseite",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()


class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        label = tk.Label(self, text="Seite 2", font=('Helvetica', 18))
        label.pack(pady=10, padx=10)

        button = tk.Button(self, text="Zurück zur Startseite",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
