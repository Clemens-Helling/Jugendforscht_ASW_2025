from assets.widgets import AlarmWidget
from tkinter import *

root = Tk()
root.title("Alarm Widget")
root.geometry("800x600")

# Liste der Elemente, für die Widgets erstellt werden sollen
elements = ["Element1", "Element2", "Element3", "Element4", "Element5", "Element6", "Element7", "Element8", "Element9"]

# Erstellen und Platzieren der Widgets
for i, element in enumerate(elements):
    widget = AlarmWidget(root, element)
    row = i // 4
    col = i % 4
    relx = col * 0.33 + 0.05  # 0.33 relative Breite pro Widget + 0.05 relativer Abstand
    rely = row * 0.33 + 0.01  # 0.33 relative Höhe pro Widget + 0.05 relativer Abstand
    widget.place(relx=relx, rely=rely, relwidth=0.28, relheight=0.28)  # Platzieren Sie  # Platzieren Sie das Widget mit einem Abstand von 10 Pixeln

root.mainloop()