from tkinter import *


class AlarmWidget(Frame):
    def __init__(self, parent, controller, alarm_name, alarm_id):
        super().__init__(parent)
        actuel_alarm = ""
        self.alarm_id = alarm_id
        self.controller = controller
        # Frame mit größerem Rahmen
        widget_frame = Frame(
            self, width=400, height=50, bg="#8af20a", bd=1, relief=SUNKEN
        )
        widget_frame.pack_propagate(False)  # Verhindert automatische Größenanpassung
        widget_frame.pack(padx=10, pady=10)  # Abstand um den Frame

        self.label = Label(widget_frame, text=alarm_name, bg="#8af20a")
        self.label.pack(side=LEFT, padx=5, pady=5)

        self.button = Button(widget_frame, text="übernehmen", command=self.accept_alarm)
        self.button.pack(side=RIGHT, padx=5, pady=5)

    def accept_alarm(self):
        print("Alarm angenommen")
        self.controller.aktueller_einsatz = self.alarm_id
        self.controller.show_frame("StartPage")
        return "accepted"


# Hauptfenster
