import pytest
from unittest import mock
from Data.database import add_alarm, is_name_in_pseudonymization, is_uuid_in_pseudonymization, find_real_name, find_real_lastname, get_all_active_alerts, add_health_data, add_alert_data, add_accsess_key, delete_accsess_key, check_accsess_premission, search_alerts
from Data.crypto import encrypt


def test_find_real_name():
    encrypted_name = encrypt("clemens")

    with mock.patch("Data.database.session") as mock_session:
        mock_query = mock.Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock.Mock(real_name=encrypted_name)

        assert find_real_name("clemens") == "clemens"



def test_add_alarm():
    with mock.patch("Data.database.session") as mock_session:
        with mock.patch("Data.database.crypto") as mock_crypto:
            mock_crypto.encrypt.return_value = "encrypted_name"
            mock_query = mock.Mock()
            mock_session.query.return_value = mock_query
            mock_query.filter_by.return_value = mock_query
            mock_query.first.return_value = None

            add_alarm("name", "lastname", "symptom")

            assert mock_session.add.call_count == 2
            assert mock_session.commit.call_count == 1

            mock_query.first.return_value = mock.Mock(pseudonym="unique_id")
            add_alarm("name", "lastname", "symptom")
            assert mock_session.add.call_count == 3
            assert mock_session.commit.call_count == 2#

def test_is_name_in_pseudonymization():
    with mock.patch("Data.database.session") as mock_session:
        with mock.patch("Data.database.crypto") as mock_crypto:
            mock_crypto.encrypt.return_value = "encrypted_name"
            mock_query = mock.Mock()
            mock_session.query.return_value = mock_query
            mock_query.filter_by.return_value = mock_query
            mock_query.first.return_value = mock.Mock(real_name="encrypted_name")

            assert is_name_in_pseudonymization("name") == True
            mock_query.first.return_value = None
            assert is_name_in_pseudonymization("not_in_db") == False

def test_is_uuid_in_pseudonymization():
    with mock.patch("Data.database.session") as mock_session:
        mock_query = mock.Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock.Mock(pseudonym="unique_id")

        assert is_uuid_in_pseudonymization("unique_id") == True
        mock_query.first.return_value = None
        assert is_uuid_in_pseudonymization("not_in_db") == False

def test_find_real_lastname():
    encrypted_lastname = encrypt(" helling")

    with mock.patch("Data.database.session") as mock_session:
        mock_query = mock.Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock.Mock(real_last_name=encrypted_lastname)
        assert find_real_lastname(" helling") == " helling"
        mock_query.first.return_value = None
        assert find_real_lastname("not_in_db") == None

class MockAlert:
    def __init__(self, id, name, lastname, symptom, Alarm_recieved):
        self.id = id
        self.name = name
        self.lastname = lastname
        self.symptom = symptom
        self.Alarm_recieved = Alarm_recieved

# Funktion zum Testen
@mock.patch('Data.database.session.query')  # Mock die Datenbankabfrage
@mock.patch('Data.database.find_real_name')  # Mock die Hilfsfunktion find_real_name
@mock.patch('Data.database.find_real_lastname')  # Mock die Hilfsfunktion find_real_lastname
def test_get_all_active_alerts(mock_find_lastname, mock_find_name, mock_query):
    # Beispiel-Daten, die zurückgegeben werden sollen
    mock_alerts = [
        MockAlert(1, "JohnDoe", "Smith", "Headache", "2025-01-19 12:00:00"),
        MockAlert(2, "JaneDoe", "Doe", "Fever", "2025-01-19 13:00:00")
    ]

    # Mock die Rückgabe von session.query().filter_by().all()
    mock_query.return_value.filter_by.return_value.all.return_value = mock_alerts

    # Mock die Rückgabe der Hilfsfunktionen
    mock_find_name.side_effect = lambda x: "John" if x == "JohnDoe" else "Jane"
    mock_find_lastname.side_effect = lambda x: "Smith" if x == "Smith" else "Doe"

    # Erwartete Ergebnisse
    expected_result = [
        {"id": 1, "name": "John", "lastname": "Smith", "symptom": "Headache", "timestamp": "2025-01-19 12:00:00"},
        {"id": 2, "name": "Jane", "lastname": "Doe", "symptom": "Fever", "timestamp": "2025-01-19 13:00:00"}
    ]

    # Führe die zu testende Funktion aus
    result = get_all_active_alerts()

    # Überprüfe das Ergebnis
    assert result == expected_result

def test_add_health_data():
    with mock.patch("Data.database.session") as mock_session:
        add_health_data("unique_id", "pulse", "spo2", "blood_pressure", "temperature", "blood_suger", "pain")
        assert mock_session.commit.call_count == 1

def test_add_alert_data():
    with mock.patch("Data.database.session") as mock_session:
        add_alert_data("unique_id", "teacher", "measures")
        assert mock_session.commit.call_count == 1

def test_add_accsess_key():
    with mock.patch("Data.database.session") as mock_session:
        add_accsess_key("firstname", "lastname", "key")
        assert mock_session.commit.call_count == 1

def test_delete_accsess_key():
    with mock.patch("Data.database.session") as mock_session:
        delete_accsess_key("firstname", "lastname")
        assert mock_session.commit.call_count == 1

def test_check_accsess_premission():
    with mock.patch("Data.database.session") as mock_session:
        mock_query = mock.Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.first.return_value = mock.Mock(premission="admin")

        assert check_accsess_premission("key") == True
        mock_query.first.return_value = None
        assert check_accsess_premission("not_in_db") == False


class MockPseudonymization:
    def __init__(self, real_name, real_last_name, pseudonym):
        self.real_name = real_name
        self.real_last_name = real_last_name
        self.pseudonym = pseudonym


class MockAlert1:
    def __init__(self, symptom, Alarm_recieved):
        self.symptom = symptom
        self.Alarm_recieved = Alarm_recieved


# Funktion zum Testen
@mock.patch('Data.database.session.query')  # Mock die Datenbankabfrage
@mock.patch('Data.crypto.encrypt')  # Mock die Verschlüsselungsfunktion
@mock.patch('Data.crypto.decrypt')  # Mock die Entschlüsselungsfunktion
def test_search_alerts(mock_decrypt, mock_encrypt, mock_query):
    # Beispiel-Daten für Pseudonymization
    mock_pseudonymization = MockPseudonymization("encryptedJohn", "encryptedDoe", "pseudonym123")

    # Beispiel-Daten für Alarmierungen
    mock_alerts = [
        MockAlert1("Headache", "2025-01-19 12:00:00"),
        MockAlert1("Fever", "2025-01-19 13:00:00")
    ]

    # Mock die Verschlüsselungsfunktion
    mock_encrypt.side_effect = lambda x: f"encrypted{x}"

    # Mock die Entschlüsselungsfunktion
    mock_decrypt.side_effect = lambda x: x.replace("encrypted", "")

    # Mock die Rückgabe von session.query().filter_by().first() und .all()
    mock_query.return_value.filter_by.return_value.first.return_value = mock_pseudonymization
    mock_query.return_value.filter_by.return_value.all.return_value = mock_alerts

    # Erwartete Ergebnisse
    expected_result = [
        {"name": "John", "lastname": "Doe", "symptom": "Headache", "timestamp": "2025-01-19 12:00:00"},
        {"name": "John", "lastname": "Doe", "symptom": "Fever", "timestamp": "2025-01-19 13:00:00"}
    ]

    # Führe die zu testende Funktion aus
    result = search_alerts("John", "Doe")

    # Überprüfe das Ergebnis
    assert result == expected_result