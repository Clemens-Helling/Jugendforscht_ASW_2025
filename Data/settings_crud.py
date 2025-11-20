from Data.models import UserSettings
from Data.alerts_crud import session_scope


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

def add_ntfy_settings(ntfy_url):
    with session_scope() as session:
        result = session.query(UserSettings).filter(UserSettings.setting_id == 1).first()
        result.ntfy_url = ntfy_url
        session.commit()

def add_notification_method(method):
    with session_scope() as session:
        result = session.query(UserSettings).filter(UserSettings.setting_id == 1).first()
        result.notification_method = method
        session.commit()



if __name__ == "__main__":
    add_notification_method("ntfy")

