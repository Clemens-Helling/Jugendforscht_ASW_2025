"""
EasyLogger - Eine einfache und flexible Logging-Bibliothek

Verwendung:
    from easy_logger import EasyLogger

    logger = EasyLogger("MeineApp")
    logger.info("Das ist eine Info")
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class EasyLogger:
    """Eine benutzerfreundliche Logging-Klasse mit sinnvollen Defaults."""

    def __init__(
            self,
            name: str = "app",
            level: str = "INFO",
            log_to_file: bool = True,
            log_to_console: bool = True,
            log_dir: str = "logs",
            log_file: Optional[str] = None,
            format_string: Optional[str] = None
    ):
        """
        Initialisiert den Logger.

        Args:
            name: Name des Loggers
            level: Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: Ob in Datei geloggt werden soll
            log_to_console: Ob in Konsole geloggt werden soll
            log_dir: Verzeichnis für Log-Dateien
            log_file: Name der Log-Datei (default: {name}_{datum}.log)
            format_string: Custom Format-String
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        self.logger.handlers.clear()

        # Standard-Format
        if format_string is None:
            format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

        formatter = logging.Formatter(format_string, datefmt='%Y-%m-%d %H:%M:%S')

        # Console Handler
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # File Handler
        if log_to_file:
            log_path = Path(log_dir)
            log_path.mkdir(exist_ok=True)

            if log_file is None:
                log_file = f"{name}_{datetime.now().strftime('%Y%m%d')}.log"

            file_handler = logging.FileHandler(log_path / log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def debug(self, message: str, **kwargs):
        """Debug-Level Log"""
        self.logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs):
        """Info-Level Log"""
        self.logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Warning-Level Log"""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs):
        """Error-Level Log"""
        self.logger.error(message, exc_info=exc_info, **kwargs)

    def critical(self, message: str, exc_info: bool = False, **kwargs):
        """Critical-Level Log"""
        self.logger.critical(message, exc_info=exc_info, **kwargs)

    def exception(self, message: str, **kwargs):
        """Loggt eine Exception mit Traceback"""
        self.logger.exception(message, **kwargs)

    def set_level(self, level: str):
        """Ändert das Log-Level zur Laufzeit"""
        self.logger.setLevel(getattr(logging, level.upper()))


# Convenience-Funktion für schnelles Setup
def get_logger(
        name: str = "app",
        level: str = "INFO",
        **kwargs
) -> EasyLogger:
    """
    Erstellt schnell einen konfigurierten Logger.

    Beispiel:
        logger = get_logger("MeineApp", level="DEBUG")
        logger.info("Hallo Welt!")
    """
    return EasyLogger(name=name, level=level, **kwargs)


# Beispielverwendung
if __name__ == "__main__":
    # Beispiel 1: Einfacher Logger
    logger = get_logger("TestApp")
    logger.info("Programm gestartet")
    logger.warning("Das ist eine Warnung")
    logger.error("Das ist ein Fehler")

    # Beispiel 2: Logger mit Custom-Konfiguration
    custom_logger = EasyLogger(
        name="CustomApp",
        level="DEBUG",
        log_to_file=True,
        log_to_console=True,
        log_dir="logs",
        log_file="meine_app.log"
    )

    custom_logger.debug("Debug-Information")
    custom_logger.info("Info-Nachricht")

    # Beispiel 3: Exception-Logging
    try:
        result = 10 / 0
    except Exception:
        custom_logger.exception("Ein Fehler ist aufgetreten")

    print("\n✅ Logs wurden erstellt! Schau in den 'logs' Ordner.")