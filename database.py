import mysql.connector
from mysql.connector import Error

db = mysql.connector.connect(
    host="localhost",
    user="Clemens",
    password="Clemens1712",
    database="notifyer"
)
cursor = db.cursor()

print(cursor.execute("SELECT * FROM alamierungen"))
results = cursor.fetchall()

for row in results:
    print(row)