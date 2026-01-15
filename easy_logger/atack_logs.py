# attack_simulation.py - Verschiedene Angriffe simulieren
import json
import time
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

SERVER_URL = 'http://localhost:5000'

# Lade private und public keys für Tests
with open('client_private_key.pem', 'rb') as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

with open('./keys/client_public_key.pem', 'rb') as f:
    public_key = serialization.load_pem_public_key(f.read())

# Client-ID berechnen
import hashlib

public_pem = public_key.public_bytes(#

    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
CLIENT_ID = hashlib.sha256(public_pem).hexdigest()[:16]


def create_valid_log(sequence, level, message):
    """Erstellt einen gültigen, signierten Log"""
    log_entry = {
        'client_id': CLIENT_ID,
        'timestamp': time.time(),
        'sequence': sequence,
        'level': level,
        'message': message,
        'metadata': {}
    }

    data_to_sign = json.dumps(log_entry, sort_keys=True)
    signature = private_key.sign(
        data_to_sign.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    return {
        'log': log_entry,
        'signature': signature.hex()
    }


def send_request(payload, description):
    """Sendet Request und zeigt Ergebnis"""
    print(f"\n{'=' * 70}")
    print(f"🎯 ANGRIFF: {description}")
    print(f"{'=' * 70}")

    try:
        response = requests.post(f'{SERVER_URL}/log', json=payload, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Antwort: {response.json()}")

        if response.status_code == 200:
            print("❌ ANGRIFF ERFOLGREICH - System ist verwundbar!")
        else:
            print("✅ ANGRIFF ABGEWEHRT - System ist sicher!")

    except Exception as e:
        print(f"Fehler: {e}")


# ============================================================================
# ANGRIFF 1: Message Manipulation
# ============================================================================
def attack_1_message_manipulation():
    """Versuche die Nachricht zu ändern ohne neue Signatur"""
    print("\n" + "=" * 70)
    print("ANGRIFF 1: Message Manipulation")
    print("=" * 70)

    # Erstelle gültigen Log
    payload = create_valid_log(1, 'INFO', 'Originale Nachricht')

    # Manipuliere die Nachricht NACH dem Signieren
    payload['log']['message'] = 'MANIPULIERTE NACHRICHT - GEHACKT!'
    payload['log']['level'] = 'CRITICAL'

    send_request(payload, "Nachricht nach Signierung geändert")


# ============================================================================
# ANGRIFF 2: Replay Attack
# ============================================================================
def attack_2_replay_attack():
    """Sende denselben Log mehrfach (Replay)"""
    print("\n" + "=" * 70)
    print("ANGRIFF 2: Replay Attack")
    print("=" * 70)

    # Erstelle gültigen Log
    payload = create_valid_log(2, 'INFO', 'Legitimer Log-Eintrag')

    # Sende einmal (sollte funktionieren)
    print("\n1. Versuch (legitim):")
    send_request(payload.copy(), "Erster Versuch - legitim")

    time.sleep(1)

    # Sende nochmal denselben Log (sollte blockiert werden)
    print("\n2. Versuch (Replay-Angriff):")
    send_request(payload.copy(), "Wiederholung desselben Logs")


# ============================================================================
# ANGRIFF 3: Sequence Manipulation
# ============================================================================
def attack_3_sequence_manipulation():
    """Versuche Sequenznummer zu manipulieren"""
    print("\n" + "=" * 70)
    print("ANGRIFF 3: Sequence Number Manipulation")
    print("=" * 70)

    # Sende Log mit Sequenz 10
    payload1 = create_valid_log(10, 'INFO', 'Log mit Sequenz 10')
    send_request(payload1, "Log mit Sequenz 10")

    time.sleep(1)

    # Versuche alte Sequenz 5 zu senden (sollte blockiert werden)
    payload2 = create_valid_log(5, 'INFO', 'Log mit alter Sequenz 5')
    send_request(payload2, "Versuch mit alter Sequenz 5")


# ============================================================================
# ANGRIFF 4: Signature Manipulation
# ============================================================================
def attack_4_signature_manipulation():
    """Versuche die Signatur zu ändern"""
    print("\n" + "=" * 70)
    print("ANGRIFF 4: Signature Manipulation")
    print("=" * 70)

    payload = create_valid_log(20, 'INFO', 'Test Message')

    # Ändere ein Byte in der Signatur
    sig_bytes = bytes.fromhex(payload['signature'])
    manipulated_sig = bytearray(sig_bytes)
    manipulated_sig[0] ^= 0xFF  # Flippe erstes Byte
    payload['signature'] = manipulated_sig.hex()

    send_request(payload, "Signatur manipuliert")


# ============================================================================
# ANGRIFF 5: Metadata Injection
# ============================================================================
def attack_5_metadata_injection():
    """Versuche Metadata zu ändern ohne neue Signatur"""
    print("\n" + "=" * 70)
    print("ANGRIFF 5: Metadata Injection")
    print("=" * 70)

    payload = create_valid_log(30, 'INFO', 'Normaler Log')

    # Füge böswillige Metadata hinzu
    payload['log']['metadata'] = {
        'injected': 'malicious_data',
        'admin': True,
        'sql_injection': "'; DROP TABLE logs; --"
    }

    send_request(payload, "Metadata nach Signierung hinzugefügt")


# ============================================================================
# ANGRIFF 6: Timestamp Manipulation
# ============================================================================
def attack_6_timestamp_manipulation():
    """Versuche Zeitstempel zu ändern"""
    print("\n" + "=" * 70)
    print("ANGRIFF 6: Timestamp Manipulation")
    print("=" * 70)

    payload = create_valid_log(40, 'INFO', 'Test Log')

    # Ändere Timestamp auf Zukunft
    payload['log']['timestamp'] = time.time() + 86400  # +1 Tag

    send_request(payload, "Timestamp in die Zukunft geändert")


# ============================================================================
# ANGRIFF 7: Client-ID Spoofing
# ============================================================================
def attack_7_client_id_spoofing():
    """Versuche sich als anderer Client auszugeben"""
    print("\n" + "=" * 70)
    print("ANGRIFF 7: Client-ID Spoofing")
    print("=" * 70)

    payload = create_valid_log(50, 'INFO', 'Legitimate message')

    # Ändere Client-ID zu falschem Wert
    payload['log']['client_id'] = 'fake_client_12345678'

    send_request(payload, "Client-ID gefälscht")


# ============================================================================
# ANGRIFF 8: Ohne Signatur
# ============================================================================
def attack_8_no_signature():
    """Sende Log ohne Signatur"""
    print("\n" + "=" * 70)
    print("ANGRIFF 8: No Signature")
    print("=" * 70)

    log_entry = {
        'client_id': CLIENT_ID,
        'timestamp': time.time(),
        'sequence': 60,
        'level': 'CRITICAL',
        'message': 'HACKER MESSAGE - NO SIGNATURE',
        'metadata': {}
    }

    payload = {
        'log': log_entry,
        'signature': ''  # Leere Signatur
    }

    send_request(payload, "Kein Signatur-Feld")


# ============================================================================
# ANGRIFF 9: Man-in-the-Middle (ohne TLS)
# ============================================================================
def attack_9_mitm_simulation():
    """Simuliert Abfangen und Ändern während Übertragung"""
    print("\n" + "=" * 70)
    print("ANGRIFF 9: Man-in-the-Middle Simulation")
    print("=" * 70)
    print("⚠️  Hinweis: Ohne TLS könnte ein Angreifer:")
    print("   - Logs mitlesen (Klartext)")
    print("   - Verbindung unterbrechen")
    print("   - Logs verzögern oder blockieren")
    print("   ✅ ABER: Signatur verhindert Manipulation!")
    print("\nDieser Angriff ist nur mit TLS vollständig abwehrbar.")


# ============================================================================
# MAIN
# ============================================================================
def main():
    print("\n" + "🔴" * 35)
    print("SICHERHEITS-TEST: Manipulations-Angriffe")
    print("🔴" * 35)
    print("\nDieser Test simuliert verschiedene Angriffe auf das Log-System.")
    print("Alle Angriffe sollten vom Server ABGEWEHRT werden.\n")

    input("Drücke ENTER um zu starten...")

    # Führe alle Angriffe durch
    attack_1_message_manipulation()
    time.sleep(1)

    attack_2_replay_attack()
    time.sleep(1)

    attack_3_sequence_manipulation()
    time.sleep(1)

    attack_4_signature_manipulation()
    time.sleep(1)

    attack_5_metadata_injection()
    time.sleep(1)

    attack_6_timestamp_manipulation()
    time.sleep(1)

    attack_7_client_id_spoofing()
    time.sleep(1)

    attack_8_no_signature()
    time.sleep(1)

    attack_9_mitm_simulation()

    print("\n" + "=" * 70)
    print("✅ TEST ABGESCHLOSSEN")
    print("=" * 70)
    print("\nWenn alle Angriffe abgewehrt wurden, ist das System sicher!")
    print("Für vollständigen Schutz fehlt noch: TLS-Verschlüsselung\n")


if __name__ == '__main__':
    main()