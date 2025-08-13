from setup_database import session
from models import User, SaniProtokoll, Protokoll, Teacher
import datetime


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
    print(f"Benutzer {name} {last_name} hinzugefügt.")


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
