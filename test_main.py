import unittest
from unittest.mock import MagicMock
from Data.database import search_alerts
from main import AlarmApp

class TestAlarmApp(unittest.TestCase):
    def setUp(self):
        self.app = TestAlarmApp()
        self.app.entry = MagicMock()
        self.app.entry1 = MagicMock()

    def test_load_data(self):
        # Set up the entry values
        self.app.entry.get.return_value = "test_entry"
        self.app.entry1.get.return_value = "test_entry1"

        # Call the load_data method
        self.app.load_data()

        # Check if the data was loaded correctly
        # This part depends on how you handle the loaded data in your application
        # For example, if you store the data in a variable, you can check it like this:
        # self.assertIsNotNone(self.app.loaded_data)
        # self.assertGreater(len(self.app.loaded_data), 0)

if __name__ == '__main__':
    unittest.main()