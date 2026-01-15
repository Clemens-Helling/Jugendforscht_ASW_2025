import json
import time
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from typing import Dict, Any
import os

class SecureLogClient:
    def __init__(self, server_url: str, private_key_path: str):
        self.server_url = server_url
        self.sequence = 0

        # Privaten Schlüssel laden
        with open(private_key_path, 'rb') as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(),
                password=None
            )

        # Client-ID aus Public Key ableiten
        public_key = self.private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        import hashlib
        self.client_id = hashlib.sha256(public_pem).hexdigest()[:16]

    def _create_signature(self, data: str) -> str:
        """Erstellt RSA-Signatur mit privatem Schlüssel"""
        signature = self.private_key.sign(
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature.hex()

    def send_log(self, level: str, message: str, metadata: Dict[str, Any] = None):
        """Sendet einen signierten Log-Eintrag"""
        self.sequence += 1

        log_entry = {
            'client_id': self.client_id,
            'timestamp': time.time(),
            'sequence': self.sequence,
            'level': level,
            'message': message,
            'metadata': metadata or {}
        }

        # Daten serialisieren für Signatur
        data_to_sign = json.dumps(log_entry, sort_keys=True)
        signature = self._create_signature(data_to_sign)

        payload = {
            'log': log_entry,
            'signature': signature
        }

        try:
            response = requests.post(
                f'{self.server_url}/log',
                json=payload,
                timeout=5,
                verify=True  # Verifiziert Server-Zertifikat
            )
            response.raise_for_status()
            print(f"✓ Log gesendet: [{level}] {message}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"✗ Fehler beim Senden: {e}")
            return False
# example_usage.py - Beispiel-Nutzung
if __name__ == '__main__':
    import sys

    # Schlüssel generieren falls nicht vorhanden
    if not os.path.exists('client_private_key.pem'):
        print("Generiere Schlüsselpaar...")
        from generate_keys import generate_keypair

        generate_keypair("client")
        print("\n⚠️  Kopiere 'client_public_key.pem' in das Server 'keys/' Verzeichnis!\n")

    # Client initialisieren
    client = SecureLogClient(
        server_url='http://192.168.178.112:5000',  # In Produktion: https://
        private_key_path='client_private_key.pem'
    )

    print(f"\n📤 Sende Test-Logs als Client {client.client_id}...\n")

    # Logs senden
    client.send_log('INFO', 'Anwendung gestartet')
    client.send_log('WARNING', 'Hohe CPU-Last', {'cpu': 95, 'cores': 8})
    client.send_log('ERROR', 'Datenbankverbindung fehlgeschlagen', {
        'db': 'postgres',
        'host': 'db.example.com',
        'retry_count': 3
    })
    client.send_log('INFO', 'Anwendung beendet')