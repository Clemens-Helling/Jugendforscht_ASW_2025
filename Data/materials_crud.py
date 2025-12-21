import datetime

from Data.models import Material, Protokoll, ProtokollMaterials
from Data.setup_database import session
from contextlib import contextmanager

@contextmanager
def session_scope():
    """Bietet einen Transaktions-Umfang für die Datenbank-Session."""
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def add_material(material_name, quantity, min_qunataty, expires_at, reuseable=False):
    """Fügt ein Material hinzu."""
    material = Material(
        material_name=material_name, quantity=quantity, expires_at=expires_at, minimum_stock=min_qunataty, reuseable=reuseable
    )
    session.add(material)
    session.commit()
    print(f"Material {material_name} hinzugefügt.")


def get_material(material_name):
    """Gibt ein Material zurück."""
    material = session.query(Material).filter_by(material_name=material_name).first()
    if material:
        return {
            "material_id": material.material_id,
            "material_name": material.material_name,
            "quantity": material.quantity,
            "expires_at": material.expires_at,
            "is_reuseable": material.reuseable,
        }
    else:
        print(f"Material {material_name} nicht gefunden.")
        return None


def add_material_quantity(material_id, quantity):
    """Aktualisiert die Menge eines Materials."""
    material = session.query(Material).filter_by(material_id=material_id).first()
    if material:
        material.quantity = material.quantity + quantity
        session.commit()
        print(f"Material {material.material_name} aktualisiert.")
    else:
        print(f"Material mit ID {material_id} nicht gefunden.")


def subtract_material_quantity(material_id, quantity):
    """Aktualisiert die Menge eines Materials."""
    material = session.query(Material).filter_by(material_id=material_id).first()
    if material:
        newQuantity = material.quantity - quantity
        material.quantity = newQuantity
        print(f"Neuer Bestand von {material.material_name}: {newQuantity}")
        session.commit()
        print(f"Material {material.material_name} aktualisiert.")
    else:
        print(f"Material mit ID {material_id} nicht gefunden.")


def update_material_expiration(material_id, expires_at):
    """Aktualisiert das Ablaufdatum eines Materials."""
    material = session.query(Material).filter_by(material_id=material_id).first()
    if material:
        material.expires_at = expires_at
        session.commit()
        print(f"Ablaufdatum von Material {material.material_name} aktualisiert.")
    else:
        print(f"Material mit ID {material_id} nicht gefunden.")


def delete_material(material_id):
    """Löscht ein Material."""
    material = session.query(Material).filter_by(material_id=material_id).first()
    if material:
        session.delete(material)
        session.commit()
        print(f"Material {material.material_name} gelöscht.")
    else:
        print(f"Material mit ID {material_id} nicht gefunden.")


def add_material_to_protokoll(alert_id, material_name, quantity):
    """Fügt ein Material zu einem Protokoll hinzu."""
    protokoll = session.query(Protokoll).filter_by(alert_id=alert_id).first()
    material = session.query(Material).filter_by(material_name=material_name).first()
    if not protokoll:
        print(f"Kein Protokoll mit alert_id {alert_id} gefunden.")
        return
    protokoll_material = ProtokollMaterials(
        protokoll_id=protokoll.protokoll_id,
        material_id=material.material_id,
        quantity=quantity,
    )
    session.add(protokoll_material)
    session.commit()

    print(
        f"Material ID {material.material_id} zu Protokoll ID {protokoll.protokoll_id} hinzugefügt."
    )


def get_materials_by_protokoll(protokoll_id):
    """Gibt alle Materialien eines Protokolls zurück."""

    materials = (
        session.query(ProtokollMaterials).filter_by(protokoll_id=protokoll_id).all()
    )
    result = []
    for material in materials:
        mat = (
            session.query(Material).filter_by(material_id=material.material_id).first()
        )
        if mat:
            result.append({"name": mat.material_name, "quantity": material.quantity})
    return result


def get_all_material_names():
    """Gibt alle Materialien zurück."""
    materials = session.query(Material).all()
    return [f"{m.material_name}" for m in materials]


print(get_materials_by_protokoll(protokoll_id=23))


def set_minimum_stock(material_id, minimum_stock):
    """Setzt den Mindestbestand eines Materials."""
    material = session.query(Material).filter_by(material_id=material_id).first()
    if material:
        material.minimum_stock = minimum_stock
        session.commit()
        print(
            f"Mindestbestand von Material {material.material_name} auf {minimum_stock} gesetzt."
        )
    else:
        print(f"Material mit ID {material_id} nicht gefunden.")


def check_low_stock():
    """Überprüft alle Materialien auf Mindestbestand und gibt eine Liste der Materialien zurück, die unter dem Mindestbestand liegen."""
    low_stock_materials = (
        session.query(Material)
        .filter(Material.quantity <= Material.minimum_stock)
        .all()
    )
    result = []
    for material in low_stock_materials:
        result.append(
            {
                "material_name": material.material_name,
                "quantity": material.quantity,
                "minimum_stock": material.minimum_stock,
            }
        )
    return result


def get_all_materials():
    """Gibt alle Materialien zurück."""
    materials = session.query(Material).all()
    result = []
    for material in materials:
        result.append(
            {
                "material_id": material.material_id,
                "material_name": material.material_name,
                "quantity": material.quantity,
                "expires_at": material.expires_at,
                "minimum_stock": material.minimum_stock,
            }
        )
    return result

def update_material(material_id, material_name=None, quantity=None, expires_at=None, minimum_stock=None):
    """Aktualisiert die Daten eines Materials."""
    material = session.query(Material).filter_by(material_id=material_id).first()
    if not material:
        print(f"Kein Material mit ID {material_id} gefunden.")
        return

    if material_name is not None:
        material.material_name = material_name
    if quantity is not None:
        material.quantity = quantity
    if expires_at is not None:
        material.expires_at = expires_at
    if minimum_stock is not None:
        material.minimum_stock = minimum_stock

    session.commit()
    print(f"Material mit ID {material_id} aktualisiert.")

def get_material_id_by_name(material_name):
    """Gibt die Material-ID anhand des Materialnamens zurück."""
    material = session.query(Material).filter_by(material_name=material_name).first()
    if material:
        return material.material_id
    else:
        print(f"Material {material_name} nicht gefunden.")
        return None

def get_material_name_by_id(material_id):
    """Gibt den Materialnamen anhand der Material-ID zurück."""
    material = session.query(Material).filter_by(material_id=material_id).first()
    if material:
        return material.material_name
    else:
        print(f"Material mit ID {material_id} nicht gefunden.")
        return None

def get_materials_by_protokoll_id(protokoll_id):
    """Gibt alle Materialien eines Protokolls anhand der Protokoll-ID zurück."""
    materials = (
        session.query(ProtokollMaterials).filter_by(protokoll_id=protokoll_id).all()
    )
    result = []
    for material in materials:
        mat = (
            session.query(Material).filter_by(material_id=material.material_id).first()
        )
        if mat:
            result.append({"name": mat.material_name, "quantity": material.quantity})
    return result


