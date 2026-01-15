import ttkbootstrap as ttk
from ttkbootstrap.constants import *


def setup_searchable_combobox(combobox, values):
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


# Beispiel-Anwendung
root = ttk.Window(themename="darkly")

names = [
    "Anna Schmidt",
    "Andreas Schmidt",
    "Barbara Weber",
    "Bernd Fischer",
    "Christine Koch",
    "Christian Meyer",
    "Diana Schneider",
    "Frank Wagner"
]

# WICHTIG: state='normal' erlaubt Eingabe ins Entry
combo = ttk.Combobox(root, values=names, state='normal', width=30)
combo.pack(padx=20, pady=20)

# Suchfunktion aktivieren
setup_searchable_combobox(combo, names)

root.mainloop()