import datetime
import json

from Data.models import Protokoll, SaniProtokoll, Teacher, User
from Data.setup_database import session
from easy_logger.easy_logger import EasyLogger

logger = EasyLogger(
    name="UsersCRUD",
    level="INFO",
    log_to_file=True,
    log_dir="logs",
    log_file="database.log"
)

def add_user(name, last_name, lernbegleiter, kartennummer, permission):
    """Fügt einen Benutzer hinzu."""
    user = User(
        name=name,
        last_name=last_name,
        lernbegleiter=lernbegleiter,
        karten_nummer=kartennummer,
        permission=permission,
    )


    session.add(user)
    session.commit()
    logger.info(f"User {name} {last_name} added with card {kartennummer}.")


def add_sani1(card_number, alert_id):
    sani = session.query(User).filter_by(karten_nummer=card_number).first()

    if not sani:
        print(f"Kein Benutzer mit Karten­nummer {card_number} gefunden.")
        return

    protokoll = session.query(Protokoll).filter_by(alert_id=alert_id).first()
    if not protokoll:
        print(f"Kein Protokoll mit alert_id {alert_id} gefunden.")
        return

    sani_protokoll = SaniProtokoll(
        sani1=sani.User_ID, protokoll_id=protokoll.protokoll_id
    )

    session.add(sani_protokoll)
    session.flush()
    protokoll.medic_id = sani_protokoll.sani_protokoll_id
    session.commit()
    print(
        f"Sani 1 ({sani.name} {sani.last_name}) zum Protokoll {protokoll.protokoll_id} hinzugefügt."
    )


def add_sani2(card_number, alert_id):
    sani = session.query(User).filter_by(karten_nummer=card_number).first()

    if not sani:
        print(f"Kein Benutzer mit Karten­nummer {card_number} gefunden.")
        return

    protokoll = session.query(Protokoll).filter_by(alert_id=alert_id).first()
    if not protokoll:
        print(f"Kein Protokoll mit alert_id {alert_id} gefunden.")
        return

    sani_protokoll = (
        session.query(SaniProtokoll)
        .filter_by(protokoll_id=protokoll.protokoll_id)
        .first()
    )
    if not sani_protokoll:
        print(f"Kein SaniProtokoll für Protokoll {protokoll.protokoll_id} gefunden.")
        return
    sani_protokoll.sani2 = sani.User_ID
    session.commit()

    print(
        f"Sani 2 ({sani.name} {sani.last_name}) zum Protokoll {protokoll.protokoll_id} hinzugefügt."
    )


def add_teacher(first_name, last_name, house):
    """Fügt einen Lehrer hinzu."""
    teacher = Teacher(first_name=first_name, last_name=last_name, house=house)
    session.add(teacher)
    session.commit()
    print(f"Lehrer {first_name} {last_name} hinzugefügt.")


def get_all_teachers():
    """Gibt alle Lehrer zurück."""
    teachers = session.query(Teacher).all()
    return [f"{l.first_name} {l.last_name}" for l in teachers]


def get_teacher_by_name(first_name, last_name):
    """Gibt einen Lehrer anhand seines Namens zurück."""
    teacher = (
        session.query(Teacher)
        .filter_by(first_name=first_name, last_name=last_name)
        .first()
    )
    if teacher:
        return {
            "teacher_id": teacher.teacher_id,
            "first_name": teacher.first_name,
            "last_name": teacher.last_name,
            "house": teacher.house,
        }
    else:
        print(f"Kein Lehrer mit dem Namen {first_name} {last_name} gefunden.")
        return None


def get_teacher_name_by_id(teacher_id):
    """Gibt den Namen eines Lehrers anhand seiner ID zurück."""
    teacher = session.query(Teacher).filter_by(teacher_id=teacher_id).first()
    if teacher:
        return f"{teacher.first_name} {teacher.last_name}"
    else:
        print(f"Kein Lehrer mit der ID {teacher_id} gefunden.")
        return None


def transform_personal(mapping):
    role_map = {
        "sani1": ("Sani1", True),
        "sani2": ("Sani2", False),
        "operationsmanager": ("Einsatztleitung", False),
        # weitere Keys hier hinzufügen wenn nötig
    }

    result = []
    for key, name in mapping.items():
        name_clean = name.strip()
        funktion, needs_signature = role_map.get(key, (key, False))
        entry = {"name": name_clean, "funktion": funktion}

        result.append(entry)

    return result


def get_medic_names_by_alert_id(alert_id):
    """Gibt die Namen der Sanis und des Operationsmanagers anhand der Alert-ID zurück."""
    protokoll = session.query(Protokoll).filter_by(alert_id=alert_id).first()
    if not protokoll:
        print(f"Kein Protokoll mit alert_id {alert_id} gefunden.")
        return None

    sani_protokoll = (
        session.query(SaniProtokoll)
        .filter_by(protokoll_id=protokoll.protokoll_id)
        .first()
    )
    if not sani_protokoll:
        print(f"Kein SaniProtokoll für Protokoll {protokoll.protokoll_id} gefunden.")
        return None

    sani1 = session.query(User).filter_by(User_ID=sani_protokoll.sani1).first()
    sani2 = session.query(User).filter_by(User_ID=sani_protokoll.sani2).first()
    operationsmanager = (
        session.query(User).filter_by(User_ID=sani_protokoll.operationsmanager).first()
    )

    inputData = {
        "sani1": f"{sani1.name} {sani1.last_name}" if sani1 else None,
        "sani2": f"{sani2.name} {sani2.last_name}" if sani2 else None,
        "operationsmanager": (
            f"{operationsmanager.name} {operationsmanager.last_name}"
            if operationsmanager
            else None
        ),
    }
    personal_list = transform_personal(inputData)


def get_sani_protokoll_id_by_alert_id(alert_id):
    """Gibt die SaniProtokoll_ID anhand der Alert-ID zurück."""
    protokoll = session.query(Protokoll).filter_by(alert_id=alert_id).first()
    if not protokoll:
        print(f"Kein Protokoll mit alert_id {alert_id} gefunden.")
        return None

    sani_protokoll = (
        session.query(SaniProtokoll)
        .filter_by(protokoll_id=protokoll.protokoll_id)
        .first()
    )
    if not sani_protokoll:
        print(f"Kein SaniProtokoll für Protokoll {protokoll.protokoll_id} gefunden.")
        return None

    return sani_protokoll.sani_protokoll_id


def get_user_by_card_number(card_number):
    """Gibt einen Benutzer anhand seiner Karten­nummer zurück."""
    user = session.query(User).filter(
        User.karten_nummer == card_number, User.permission != "deactivated"
    ).first()
    if user:
        return {
            "User_ID": user.User_ID,
            "name": user.name,
            "last_name": user.last_name,
            "lernbegleiter": user.lernbegleiter,
            "karten_nummer": user.karten_nummer,
            "permission": user.permission,
        }
    else:
        logger.warning(f"Karte {card_number} nicht gefunden.")
        print(f"Kein Benutzer mit Karten­nummer {card_number} gefunden.")
        return None


# Python
def get_all_active_users():
    """Gibt alle Benutzer als Liste von Dicts zurück."""
    users = session.query(User).filter(User.permission != "deactivated").all()
    personal_list = []
    for user in users:
        personal_list.append(
            {
                "User_ID": user.User_ID,
                "name": user.name,
                "last_name": user.last_name,
                "lernbegleiter": user.lernbegleiter,
                "karten_nummer": user.karten_nummer,
                "permission": user.permission,
            }
        )
    return personal_list


def update_user(
    user_id,
    name=None,
    last_name=None,
    lernbegleiter=None,
    kartennummer=None,
    permission=None,
):
    """Aktualisiert die Daten eines Benutzers."""
    user = session.query(User).filter_by(User_ID=user_id).first()
    if not user:
        print(f"Kein Benutzer mit ID {user_id} gefunden.")
        return

    if name is not None:
        user.name = name
    if last_name is not None:
        user.last_name = last_name
    if lernbegleiter is not None:
        user.lernbegleiter = lernbegleiter
    if kartennummer is not None:
        user.karten_nummer = kartennummer
    if permission is not None:
        user.permission = permission

    session.commit()
    logger.info(f"User {user.name} updated.")
    print(f"Benutzer mit ID {user_id} aktualisiert.")


def delete_user(user_id):
    """Löscht einen Benutzer."""
    user = session.query(User).filter_by(User_ID=user_id).first()
    if not user:
        print(f"Kein Benutzer mit ID {user_id} gefunden.")
        return
    user.permission = "deactivated"
    session.commit()
    logger.info(f"User {user.name} deleted.")


def check_user_permisson(card_number, required_permission):
    """Überprüft, ob ein Benutzer die erforderliche Berechtigung hat."""
    user = session.query(User).filter(
        User.karten_nummer == card_number, User.permission != "deactivated").first()
    if not user:
        print(f"Kein Benutzer mit Karten­nummer {card_number} gefunden.")
        logger.info(f"Faild login attempt with card number {card_number} for permission {required_permission}")
        return False

    if user.permission == required_permission or user.permission == "admin":
        return True
    else:
        logger.info(f"Faild login from {user.name} {user.last_name} for permission {required_permission}")
        return False


if __name__ == "__main__":
   logger.info("Users CRUD Modul ausgeführt.")
   print(get_user_by_card_number("7C42D67A"))
