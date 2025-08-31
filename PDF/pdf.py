#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Einsatzprotokoll Generator mit ReportLab
Erstellt ein ausgefülltes Einsatzprotokoll mit variablen Daten - mit zweiter Seite
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import black, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
import os


class EinsatzprotokollGenerator:
    def __init__(self):
        self.width, self.height = A4
        self.margin = 2 * cm

    def create_protocol(self, data, filename="einsatzprotokoll.pdf"):
        """Erstellt das Einsatzprotokoll mit den übergebenen Daten"""
        c = canvas.Canvas(filename, pagesize=A4)

        # Seite 1
        self.draw_page_1(c, data)

        # Neue Seite beginnen
        c.showPage()

        # Seite 2
        self.draw_page_2(c, data)

        c.save()
        print(f"Einsatzprotokoll wurde erstellt: {filename}")

    def draw_page_1(self, c, data):
        """Zeichnet die erste Seite"""
        # Header
        self.draw_header(c, "Seite 1")

        # Formular-Felder mit Daten
        self.draw_form_fields_page_1(c, data)

        # Footer für Seite 1
        self.draw_footer(c, 1)

    def draw_page_2(self, c, data):
        """Zeichnet die zweite Seite"""
        # Header für Seite 2
        self.draw_header(c, "Seite 2 - Fortsetzung")

        # Zusätzliche Felder für Seite 2
        self.draw_form_fields_page_2(c, data)

        # Footer für Seite 2
        self.draw_footer(c, 2)

    def draw_header(self, c, subtitle=""):
        """Zeichnet den Kopfbereich"""
        # Haupttitel
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(self.width / 2, self.height - 1 * cm, "EINSATZPROTOKOLL")

        # Untertitel
        c.setFont("Helvetica", 12)
        if subtitle:
            c.drawCentredString(self.width / 2, self.height - 1.8 * cm,
                                f"Dokumentation des Einsatzverlaufs - {subtitle}")
        else:
            c.drawCentredString(self.width / 2, self.height - 1.8 * cm, "Dokumentation des Einsatzverlaufs")

        # Linie unter Header
        c.setLineWidth(1)
        c.line(self.margin, self.height - 2.5 * cm,
               self.width - self.margin, self.height - 2.5 * cm)

    def draw_form_fields_page_1(self, c, data):
        """Zeichnet die Formularfelder der ersten Seite mit Daten"""
        y_pos = self.height - 3.5 * cm

        # Grunddaten
        self.draw_section(c, "1. PATIENT", y_pos)
        y_pos -= 0.5 * cm

        fields = [
            ("Name:", data.get("name", "")),
            ("Vorname:", data.get("vorname", "")),
            ("Geburtsdatum:", data.get("geburtsdatum", "")),
            ("Klassenlehrer:", data.get("klassenlehrer", ""))
        ]

        for i, (label, value) in enumerate(fields):
            if i % 2 == 0:  # Neue Zeile alle 2 Felder
                y_pos -= 1.2 * cm
            x_pos = self.margin if i % 2 == 0 else self.width / 2
            self.draw_field_with_value(c, label, value, x_pos, y_pos, width=8 * cm)

        y_pos -= 2 * cm

        # Alarmierung
        self.draw_section(c, "2. Alarmierung", y_pos)
        y_pos -= 1 * cm

        self.draw_field_with_value(c, "Symptom:",
                                   data.get("symptom", ""), self.margin, y_pos, width=12 * cm)
        y_pos -= 0.8 * cm
        self.draw_field_with_value(c, "Alarm typ:",
                                   data.get("alarm_typ", ""), self.margin, y_pos, width=8 * cm)
        self.draw_field_with_value(c, "Alarm eingegangen:",
                                   data.get("alarm_eingegangen", ""), self.width / 2, y_pos, width=8 * cm)

        y_pos -= 2 * cm

        # Vitalzeichen
        self.draw_section(c, "3. Vitalzeichen", y_pos)
        y_pos -= 0.5 * cm

        fields = [
            ("Puls:", data.get("puls", "")),
            ("SpO2:", data.get("spo2", "")),
            ("Blutdruck:", data.get("blutdruck", "")),
            ("Blutzucker:", data.get("blutzucker", "")),
            ("Körpertemperatur:", data.get("temperatur", "")),
            ("Schmerz:", data.get("schmerz", ""))
        ]

        for i, (label, value) in enumerate(fields):
            if i % 2 == 0:  # Neue Zeile alle 2 Felder
                y_pos -= 1.2 * cm
            x_pos = self.margin if i % 2 == 0 else self.width / 2
            self.draw_field_with_value(c, label, value, x_pos, y_pos, width=8 * cm)

        y_pos -= 2 * cm

        # Maßnahmen
        self.draw_section(c, "4. Maßnahmen", y_pos)
        y_pos -= 0.7 * cm

        fields = [
            ("Maßnahme:", data.get("massnahme", "")),
            ("Abholmaßnahme:", data.get("abholmassnahme", "")),
            ("Eltern benachrichtigt um:", data.get("eltern_zeit", "")),
            ("Eltern benachrichtigt von:", data.get("eltern_von", "")),
            ("Krankenhaus:", data.get("krankenhaus", ""))
        ]

        for i, (label, value) in enumerate(fields):
            if i % 2 == 0:  # Neue Zeile alle 2 Felder
                y_pos -= 1.2 * cm
            x_pos = self.margin if i % 2 == 0 else self.width / 2
            self.draw_field_with_value(c, label, value, x_pos, y_pos, width=8 * cm)

    def draw_form_fields_page_2(self, c, data):
        """Zeichnet die Formularfelder der zweiten Seite"""
        y_pos = self.height - 3.5 * cm

        # Personal
        self.draw_section(c, "5. Personal", y_pos)
        y_pos -= 1 * cm

        # Tabelle für Personal
        self.draw_personnel_table(c, y_pos, data.get("personal", []))
        y_pos -= 6 * cm

        # Einsatzverlauf (großes Textfeld)


    def draw_footer(self, c, page_number):
        """Zeichnet den Fußbereich"""
        y_pos = 4 * cm


        # Seitennummer
        c.setFont("Helvetica", 8)
        c.drawRightString(self.width - self.margin, 1 * cm,
                          f"Seite {page_number} - Erstellt am {datetime.now().strftime('%d.%m.%Y %H:%M')}")

    def draw_section(self, c, title, y_pos):
        """Zeichnet eine Sektionsüberschrift"""
        c.setFont("Helvetica-Bold", 12)
        c.drawString(self.margin, y_pos, title)
        # Linie unter Überschrift
        c.setLineWidth(0.5)
        c.line(self.margin, y_pos - 0.3 * cm,
               self.width - self.margin, y_pos - 0.3 * cm)

    def draw_field_with_value(self, c, label, value, x_pos, y_pos, width=6 * cm):
        """Zeichnet ein Eingabefeld mit Wert"""
        c.setFont("Helvetica", 10)
        c.drawString(x_pos, y_pos, label)

        # Linie für Eingabe
        c.setLineWidth(0.5)
        c.line(x_pos + 0.1 * cm, y_pos - 0.5 * cm,
               x_pos + width, y_pos - 0.5 * cm)

        # Wert eintragen
        if value:
            c.setFont("Helvetica", 9)
            c.drawString(x_pos + 0.2 * cm, y_pos - 0.4 * cm, str(value))

    def draw_text_area_with_content(self, c, label, content, x_pos, y_pos, width=10 * cm, height=3 * cm):
        """Zeichnet ein größeres Textfeld mit Inhalt"""
        c.setFont("Helvetica", 10)
        c.drawString(x_pos, y_pos, label)

        # Rechteck für Textbereich
        c.setLineWidth(0.5)
        c.rect(x_pos, y_pos - height, width, height, stroke=1, fill=0)

        # Linien im Textbereich
        line_spacing = 0.6 * cm
        for i in range(1, int(height / line_spacing)):
            y_line = y_pos - (i * line_spacing)
            c.line(x_pos, y_line, x_pos + width, y_line)

        # Inhalt einfügen
        if content:
            c.setFont("Helvetica", 9)
            # Text in Zeilen aufteilen
            lines = self.wrap_text(content, width - 0.5 * cm, c)

            for i, line in enumerate(lines):
                if i * line_spacing < height - 0.8 * cm:  # Prüfen ob Platz vorhanden
                    y_text = y_pos - 0.4 * cm - (i * line_spacing)
                    c.drawString(x_pos + 0.2 * cm, y_text, line)

    def wrap_text(self, text, width, canvas):
        """Teilt Text in Zeilen auf, die in die angegebene Breite passen"""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word
            if canvas.stringWidth(test_line, "Helvetica", 9) <= width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    def draw_checkbox(self, c, label, x_pos, y_pos, checked=False):
        """Zeichnet eine Checkbox mit Label"""
        # Checkbox
        c.setLineWidth(0.5)
        c.rect(x_pos, y_pos - 0.3 * cm, 0.4 * cm, 0.4 * cm, stroke=1, fill=0)

        # Häkchen wenn aktiviert
        if checked:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(x_pos + 0.05 * cm, y_pos - 0.25 * cm, "✓")

        # Label
        c.setFont("Helvetica", 10)
        c.drawString(x_pos + 0.6 * cm, y_pos - 0.1 * cm, label)

    def draw_personnel_table(self, c, y_pos, personnel_data):
        """Zeichnet eine Tabelle für Personal mit Daten"""
        # Tabellenkopf
        headers = ["Name", "Funktion"]
        col_widths = [4 * cm, 3 * cm]

        c.setFont("Helvetica-Bold", 10)
        x_start = self.margin

        # Header zeichnen
        for i, (header, width) in enumerate(zip(headers, col_widths)):
            x_pos = x_start + sum(col_widths[:i])
            c.drawString(x_pos + 0.1 * cm, y_pos, header)
            c.rect(x_pos, y_pos - 0.4 * cm, width, 0.6 * cm, stroke=1, fill=0)

        # Zeilen für Einträge mit Daten
        c.setFont("Helvetica", 9)
        for row in range(max(6, len(personnel_data))):  # Mindestens 6 Zeilen
            y_row = y_pos - 0.6 * cm - (row * 0.6 * cm)

            # Daten eintragen wenn vorhanden
            person_data = personnel_data[row] if row < len(personnel_data) else {}

            data_fields = ["name", "funktion", "ankunft", "ende", "unterschrift"]

            for i, (width, field) in enumerate(zip(col_widths, data_fields)):
                x_pos = x_start + sum(col_widths[:i])
                c.rect(x_pos, y_row - 0.4 * cm, width, 0.6 * cm, stroke=1, fill=0)

                # Wert eintragen
                value = person_data.get(field, "")
                if value:
                    c.drawString(x_pos + 0.1 * cm, y_row - 0.1 * cm, str(value))


def create_sample_data():
    """Erstellt Beispieldaten für das Protokoll"""
    return {
        # Seite 1 - Patient
        "name": "Mustermann",
        "vorname": "Max",
        "geburtsdatum": "15.03.2010",
        "klassenlehrer": "Frau Steffen",

        # Alarmierung
        "symptom": "Sturz vom Klettergerüst",
        "alarm_typ": "Unfall",
        "alarm_eingegangen": "14:23 Uhr",

        # Vitalzeichen
        "puls": "95 /min",
        "spo2": "98%",
        "blutdruck": "110/70 mmHg",
        "blutzucker": "95 mg/dl",
        "temperatur": "36.8°C",
        "schmerz": "4/10",

        # Maßnahmen
        "massnahme": "Erstversorgung",
        "abholmassnahme": "Rettungswagen",
        "eltern_zeit": "14:45 Uhr",
        "eltern_von": "Sekretariat",
        "krankenhaus": "Klinikum Lörach",

        # Seite 2 - Personal
        "personal": [
            {"name": "Anna Müller", "funktion": "Sani1",
             "unterschrift": ""},
            {"name": "Roman Kramer", "funktion": "Sani2"},
            {"name": "Andrea Trippe", "funktion": "Einsatztleitung"}
        ],}




def main():
    """Hauptfunktion zum Erstellen des Protokolls"""
    generator = EinsatzprotokollGenerator()

    # Beispieldaten laden
    data = create_sample_data()

    # Erstelle das Protokoll mit Daten
    output_file = "einsatzprotokoll_2_seiten.pdf"
    generator.create_protocol(data, output_file)

    print(f"\n✓ Einsatzprotokoll (2 Seiten) wurde erfolgreich erstellt: {output_file}")
    print("Das Protokoll enthält die übergebenen Daten auf 2 Seiten.")


if __name__ == "__main__":
    # Prüfe ob ReportLab installiert ist
    try:
        import reportlab

        print("ReportLab gefunden, erstelle ausgefülltes Einsatzprotokoll...")
        main()
    except ImportError:
        print("ReportLab ist nicht installiert.")
        print("Installieren Sie es mit: pip install reportlab")