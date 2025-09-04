from Data.setup_database import session
from Data.models import Material, ProtokollMaterials, Protokoll
import datetime


def add_material(material_name, quantity, expires_at):
    """Fügt ein Material hinzu."""
    material = Material(
        material_name=material_name, quantity=quantity, expires_at=expires_at
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
        material.quantity = material.quantity - quantity
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
        protokoll_id=protokoll.protokoll_id, material_id= material.material_id, quantity=quantity
    )
    session.add(protokoll_material)
    session.commit()

    print(f"Material ID {material.material_id} zu Protokoll ID {protokoll.protokoll_id} hinzugefügt.")

def get_materials_by_protokoll(protokoll_id):
    """Gibt alle Materialien eines Protokolls zurück."""
    materials = (
        session.query(ProtokollMaterials)
        .filter_by(protokoll_id=protokoll_id)
        .all()
    )
    result = []
    for material in materials:
        mat = session.query(Material).filter_by(material_id=material.material_id).first()
        if mat:
            result.append({'name': mat.material_name, 'quantity': material.quantity})
    return result
def get_all_material_names():
    """Gibt alle Materialien zurück."""
    materials = session.query(Material).all()
    return [f"{m.material_name}" for m in materials]
print(get_materials_by_protokoll(protokoll_id=23))

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
            }
        )
    return result

def get_material_id_by_name(material_name):
    """Gibt die ID eines Materials anhand seines Namens zurück."""
    material = session.query(Material).filter_by(material_name=material_name).first()
    if material:
        return material.material_id
    else:
        print(f"Material {material_name} nicht gefunden.")
        return None