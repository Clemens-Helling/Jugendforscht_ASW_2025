import pytest
from unittest import mock
from Alert.alarm import alarm

def test_alarm():
    with mock.patch("Alert.alarm.database") as mock_database:
        alarm("symtom", "name", "last_name")
        assert mock_database.add_alarm.call_count == 1
        mock_database.add_alarm.assert_called_with("name", "last_name", "symtom")
