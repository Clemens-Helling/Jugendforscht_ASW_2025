import os
from Data.models import UserSettings
from Data.alerts_crud import session_scope
from easy_logger.easy_logger import EasyLogger
from easy_logger.secure_log_client import SecureLogClient
from easy_logger.error_codes import ErrorCodes

logger = EasyLogger(
    name="UsersCRUD",
    level="INFO",
    log_to_file=True,
    log_dir="logs",
    log_file="database.log"
)

# Initialize secure log client
secure_logger = None
if os.path.exists('/home/clemens/dev/Jugendforscht_ASW_2025/keys/client_private_key.pem'):
    try:
        secure_logger = SecureLogClient(
            server_url='http://192.168.178.112:5000',
            private_key_path='/home/clemens/dev/Jugendforscht_ASW_2025/keys/client_private_key.pem'
        )
    except Exception as e:
        print(f"Failed to initialize secure logger: {e}")
def get_user_settings(setting_id):
    with session_scope() as session:
        settings = (
            session.query(UserSettings)
            .filter(UserSettings.setting_id == setting_id)
            .first()
        )
        if settings:
            # Attribute vor dem Schließen der Session laden
            return {
                "setting_id": settings.setting_id,
                "method": settings.notification_method,
                "ntfy_url": settings.ntfy_url,
                "divera_key": settings.divera_key,
                "divera_ric": settings.divera_ric,
            }
        return None

def add_divera_settings(divera_key, divera_ric):
    with session_scope() as session:
        result = session.query(UserSettings).filter(UserSettings.setting_id == 1).first()
        result.divera_key = divera_key
        result.divera_ric = divera_ric
        session.commit()
        if secure_logger:
            secure_logger.send_log('INFO', 'Divera settings updated', {'setting_id': 1})

def add_ntfy_settings(ntfy_url):
    with session_scope() as session:
        result = session.query(UserSettings).filter(UserSettings.setting_id == 1).first()
        result.ntfy_url = ntfy_url
        session.commit()
        if secure_logger:
            secure_logger.send_log('INFO', 'Ntfy settings updated', {'setting_id': 1, 'ntfy_url': ntfy_url})

def add_notification_method(method):
    with session_scope() as session:
        result = session.query(UserSettings).filter(UserSettings.setting_id == 1).first()
        result.notification_method = method
        session.commit()



if __name__ == "__main__":
    add_notification_method("ntfy")

