from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os

# Pfad zur Schlüsseldatei
key_file_path = "key.key"

# Funktion zum Laden des Schlüssels
def load_key():
    if os.path.exists(key_file_path):
        with open(key_file_path, "rb") as key_file:
            key = key_file.read()
        print("Schlüssel geladen.")
    else:
        key = os.urandom(16)  # 16 Bytes Schlüssel für AES-128
        with open(key_file_path, "wb") as key_file:
            key_file.write(key)
        print("Neuer Schlüssel generiert und gespeichert.")
    return key

# Schlüssel laden oder generieren
key = load_key()

# Fester IV für deterministische Verschlüsselung
iv = b'0123456789abcdef'  # 16 Bytes IV für AES

# Verschlüssele die gepolsterten Daten
def encrypt(data):
    if isinstance(data, str):
        data = data.encode()  # Konvertiere in Bytes, falls es sich um einen String handelt
    gepolsterte_daten = pad(data, AES.block_size)
    cipher_encrypt = AES.new(key, AES.MODE_CBC, iv)  # Verschlüsselungsobjekt hier erstellen
    return cipher_encrypt.encrypt(gepolsterte_daten)

# Entschlüssele die Daten
def decrypt(data):
    cipher_decrypt = AES.new(key, AES.MODE_CBC, iv)  # Entschlüsselungsobjekt hier erstellen
    entschluesselte_daten = cipher_decrypt.decrypt(data)
    return unpad(entschluesselte_daten, AES.block_size).decode()

# Beispiel für die Verwendung
if __name__ == "__main__":
    daten = "geheime_nachricht"  # Beispiel für Daten
    encrypted_data = encrypt(daten)
    print(f"Verschlüsselte Daten: {encrypted_data}")
    decrypted_data = decrypt(encrypted_data)
    print(f"Entschlüsselte Daten: {decrypted_data}")