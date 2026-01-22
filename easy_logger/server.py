from flask import Flask, request, jsonify
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import json
import os
import datetime
from pathlib import Path

app = Flask(__name__)

# Log-Datei Konfiguration
LOG_FILE = 'server_logs.jsonl'

# Public Keys der Clients laden
client_public_keys = {}


def load_client_keys(keys_directory='../keys'):
    """Lädt alle öffentlichen Schlüssel aus dem Verzeichnis"""
    keys_path = Path(keys_directory)
    if not keys_path.exists():
        keys_path.mkdir(parents=True)
        print(f"⚠️  Verzeichnis {keys_directory} erstellt. Kopiere Client Public Keys hierhin.")
        return

    for key_file in keys_path.glob('*_public_key.pem'):
        with open(key_file, 'rb') as f:
            public_key = serialization.load_pem_public_key(f.read())

            # Client-ID aus Public Key ableiten
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            import hashlib
            client_id = hashlib.sha256(public_pem).hexdigest()[:16]

            client_public_keys[client_id] = public_key
            print(f"✓ Public Key geladen: {key_file.name} -> Client-ID: {client_id}")


# Speichert letzte Sequenznummer pro Client
client_sequences = {}


def verify_signature(log_data: dict, signature_hex: str, client_id: str) -> bool:
    """Verifiziert RSA-Signatur mit öffentlichem Schlüssel"""
    if client_id not in client_public_keys:
        print(f"✗ Unbekannte Client-ID: {client_id}")
        return False

    try:
        signature = bytes.fromhex(signature_hex)
        data = json.dumps(log_data, sort_keys=True).encode()

        public_key = client_public_keys[client_id]
        public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception as e:
        print(f"✗ Signatur-Verifikation fehlgeschlagen: {e}")
        return False


def verify_sequence(client_id: str, sequence: int) -> bool:
    """Prüft Sequenznummer gegen Replay-Angriffe"""
    last_seq = client_sequences.get(client_id, 0)

    if sequence <= last_seq:
        print(f"✗ Ungültige Sequenz: {sequence} (erwartet > {last_seq})")
        return False

    client_sequences[client_id] = sequence
    return True


def write_log_to_file(log_entry: dict):
    """Schreibt Log-Eintrag in Datei"""
    try:
        # Zeitstempel für Empfang hinzufügen
        log_entry['received_at'] = datetime.datetime.now().isoformat()

        # In JSONL-Format schreiben (eine JSON-Zeile pro Log)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

        print(f"✓ Log in Datei geschrieben: {LOG_FILE}")
        return True
    except Exception as e:
        print(f"✗ Fehler beim Schreiben in Datei: {e}")
        return False


@app.route('/log', methods=['POST'])
def receive_log():
    data = request.get_json()

    if not data or 'log' not in data or 'signature' not in data:
        return jsonify({'error': 'Invalid request'}), 400

    log_entry = data['log']
    signature = data['signature']
    client_id = log_entry.get('client_id')

    if not client_id:
        return jsonify({'error': 'Missing client_id'}), 400

    # Signatur verifizieren
    if not verify_signature(log_entry, signature, client_id):
        return jsonify({'error': 'Invalid signature'}), 401

    # Sequenznummer prüfen
    if not verify_sequence(client_id, log_entry['sequence']):
        return jsonify({'error': 'Invalid sequence'}), 401

    # Log in Datei schreiben
    if not write_log_to_file(log_entry):
        return jsonify({'error': 'Failed to write log'}), 500

    # Log auch auf Konsole ausgeben
    print(f"\n{'=' * 60}")
    print(f"Client: {client_id}")
    print(f"[{log_entry['level']}] {log_entry['message']}")
    if log_entry['metadata']:
        print(f"Metadata: {log_entry['metadata']}")
    print(f"{'=' * 60}")

    return jsonify({'status': 'success'}), 200


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'registered_clients': len(client_public_keys)
    })


if __name__ == '__main__':
    print("\n🔐 Sicherer Log-Server startet...")
    print(f"📝 Logs werden gespeichert in: {LOG_FILE}")
    load_client_keys('../keys')

    # In Produktion mit echtem TLS-Zertifikat:
    # app.run(ssl_context=('cert.pem', 'key.pem'), host='0.0.0.0', port=443)
    app.run(host='0.0.0.0', port=5000, debug=True)

# example_usage.py - Beispiel-Nutzung
if __name__ == '__main__':
    import sys

    # Schlüssel generieren falls nicht vorhanden
    private_key_path = '../keys/client_private_key.pem'
    if not os.path.exists(private_key_path):
        print("Generiere Schlüsselpaar...")
        from generate_keys import generate_keypair

        generate_keypair("client", keys_dir="../keys")
        print("\n⚠️  Alle Schlüssel wurden im 'keys/' Verzeichnis erstellt!\n")

    # Client initialisieren
    client = SecureLogClient(
        server_url='http://localhost:5000',  # In Produktion: https://
        private_key_path=private_key_path
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