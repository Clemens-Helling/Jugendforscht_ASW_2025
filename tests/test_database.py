import datetime
from unittest import mock

import pytest

from Data.database import (add_alert, add_patient, generate_unique_pseudonym,
                           is_name_in_patient, is_uuid_in_patient)
from Data.models import (Alarmierung, Base, Material, Patient, Protokoll,
                         SaniProtokoll, Teacher, User)


@mock.patch("Data.database.session")
def test_add_alert(mock_session):
    mock_alert = mock.Mock(spec=Alarmierung)
    mock_alert.alert_id = 42
    mock_session.add.return_value = None
    mock_session.flush.return_value = None
    mock_session.commit.return_value = None

    with mock.patch("Data.database.Alarmierung", return_value=mock_alert):
        with mock.patch("Data.database.Protokoll") as mock_protokoll:
            mock_protokoll.return_value = mock.Mock()
            alert_id = add_alert("Bauchweh", "erkrankung")
            assert alert_id == 42
            assert mock_session.add.call_count == 2
            mock_session.commit.assert_called_once()


@mock.patch("Data.database.session")
@mock.patch("Data.database.encrypt", return_value="enc")
def test_is_name_in_patient(mock_encrypt, mock_session):
    mock_patient = mock.Mock(spec=Patient)
    mock_session.query.return_value.filter_by.return_value.first.return_value = (
        mock_patient
    )
    result = is_name_in_patient("Max", "Mustermann", datetime.datetime(2020, 1, 1))
    assert result == mock_patient

    mock_session.query.return_value.filter_by.return_value.first.return_value = None
    result = is_name_in_patient("Max", "Mustermann", datetime.datetime(2020, 1, 1))
    assert result is None


@mock.patch("Data.database.session")
def test_is_uuid_in_patient(mock_session):
    mock_session.query.return_value.filter_by.return_value.first.return_value = (
        mock.Mock()
    )
    assert is_uuid_in_patient("uuid") is True
    mock_session.query.return_value.filter_by.return_value.first.return_value = None
    assert is_uuid_in_patient("uuid") is None


@mock.patch("Data.database.is_uuid_in_patient", return_value=False)
def test_generate_unique_pseudonym(mock_is_uuid):
    uuid_val = generate_unique_pseudonym()
    assert isinstance(uuid_val, str)
    assert len(uuid_val) > 0


@mock.patch("Data.database.session")
@mock.patch("Data.database.is_name_in_patient")
@mock.patch("Data.database.encrypt", return_value="enc")
@mock.patch("Data.database.generate_unique_pseudonym", return_value="unique")
def test_add_patient_new(mock_gen, mock_encrypt, mock_is_name, mock_session):
    # Neuer Patient
    mock_is_name.return_value = None
    mock_protokoll = mock.Mock(spec=Protokoll)
    mock_session.query.return_value.filter_by.return_value.first.return_value = (
        mock_protokoll
    )
    mock_patient = mock.Mock(spec=Patient)
    with mock.patch("Data.database.Patient", return_value=mock_patient):
        add_patient("Max", "Mustermann", datetime.datetime(2020, 1, 1), 1)
        mock_session.add.assert_called_with(mock_patient)
        mock_protokoll.pseudonym = "unique"
        mock_session.commit.assert_called()


@mock.patch("Data.database.session")
@mock.patch("Data.database.is_name_in_patient")
def test_add_patient_exists(mock_is_name, mock_session):
    # Patient existiert schon
    mock_patient = mock.Mock(spec=Patient)
    mock_patient.pseudonym = "pseudonym"
    mock_is_name.return_value = mock_patient
    mock_protokoll = mock.Mock(spec=Protokoll)
    mock_session.query.return_value.filter_by.return_value.first.return_value = (
        mock_protokoll
    )
    add_patient("Max", "Mustermann", datetime.datetime(2020, 1, 1), 1)
    assert mock_protokoll.pseudonym == "pseudonym"
    mock_session.commit.assert_called()
