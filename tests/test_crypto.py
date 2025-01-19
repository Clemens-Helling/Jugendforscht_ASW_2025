from unittest import mock
from unittest.mock import mock_open
from Data.crypto import load_key, encrypt, decrypt # Importiere die Funktion aus dem Modul, das du testest

key_file_path = 'key.key'


# Funktion zum Testen
@mock.patch('Data.crypto.os.path.exists')  # Passe den Modulpfad an
@mock.patch('Data.crypto.open', new_callable=mock_open)  # Mock open
@mock.patch('Data.crypto.os.urandom')  # Mock os.urandom
def test_load_key(mock_urandom, mock_open, mock_exists):
    # Szenario 1: Schlüsseldatei existiert
    mock_exists.return_value = True
    mock_open.return_value.__enter__.return_value.read.return_value = b'existing_key'

    result = load_key()
    assert result == b'existing_key'
    mock_open.assert_called_with(key_file_path, "rb")
    print("Test: Schlüsseldatei existiert - bestanden.")

    # Szenario 2: Schlüsseldatei existiert nicht
    mock_exists.return_value = False
    mock_urandom.return_value = b'new_random_key'
    mock_open.return_value.__enter__.return_value.write = mock.MagicMock()

    result = load_key()
    assert result == b'new_random_key'
    mock_open.assert_called_with(key_file_path, "wb")
    mock_open.return_value.__enter__.return_value.write.assert_called_once_with(b'new_random_key')
    print("Test: Schlüsseldatei existiert nicht - bestanden.")

def test_encrypt_decrypt():
    data = "Hallo, Welt!"
    encrypted_data = encrypt(data)
    decrypted_data = decrypt(encrypted_data)
    assert decrypted_data == data

