from mfrc522 import SimpleMFRC522

import RPi.GPIO as GPIO

class RFIDReader:
    def __init__(self):
        self.reader = SimpleMFRC522()

    def read_data(self):
        try:
            print("Place your RFID card near the reader...")
            id, text = self.reader.read()
            print(f"ID: {id}")
            print(f"Text: {text}")
            return id
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            GPIO.cleanup()

    def write_data(self, text):
        try:
            print("Place your RFID card near the reader...")
            self.reader.write(text)
            print(f"Data written successfully: {text}")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            GPIO.cleanup()
            

if __name__ == "__main__":
    rfid_reader = RFIDReader()
    rfid_reader.read_data()