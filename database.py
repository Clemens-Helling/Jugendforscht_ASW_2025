import time

import mysql.connector
from mysql.connector import Error

db = mysql.connector.connect(
    host="localhost", user="Clemens", password="Clemens1712", database="notifyer"
)
cursor = db.cursor()


def insert_alarm(Symptom):
    try:
        cursor.execute(
            "INSERT INTO alamierungen (Symptome, Datum_Uhrzeit) VALUES (%s,%s);",
            (Symptom, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),
        )
        db.commit()
    except Error as e:
        print(e)
