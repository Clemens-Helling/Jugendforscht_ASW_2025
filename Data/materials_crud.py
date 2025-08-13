from setup_database import session
from models import Material, ProtokollMaterials, Protokoll
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


def update_material_quantity(material_id, quantity):
    """Aktualisiert die Menge eines Materials."""
    material = session.query(Material).filter_by(material_id=material_id).first()
    if material:
        material.quantity = quantity
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


def add_material_to_protokoll(protokoll_id, material_id, quantity):
    """Fügt ein Material zu einem Protokoll hinzu."""

    protokoll_material = ProtokollMaterials(
        protokoll_id=protokoll_id, material_id=material_id, quantity=quantity
    )
    session.add(protokoll_material)
    session.commit()

    print(f"Material ID {material_id} zu Protokoll ID {protokoll_id} hinzugefügt.")

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

print(get_materials_by_protokoll(protokoll_id=23))