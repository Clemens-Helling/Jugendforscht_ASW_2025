from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os


def generate_keypair(client_name="client"):
    """Generiert RSA-Schlüsselpaar für einen Client"""

    # RSA-Schlüsselpaar generieren
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    # Privaten Schlüssel speichern (nur für Client)
    private_key_path = f'{client_name}_private_key.pem'
    with open(private_key_path, 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Öffentlichen Schlüssel speichern (für Server)
    public_key_path = f'{client_name}_public_key.pem'
    with open(public_key_path, 'wb') as f:
        f.write(private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    print(f"✓ Schlüsselpaar für '{client_name}' erstellt:")
    print(f"  {private_key_path} -> Client (GEHEIM HALTEN!)")
    print(f"  {public_key_path}  -> Server")

    return private_key_path, public_key_path


if __name__ == '__main__':
    generate_keypair("client")