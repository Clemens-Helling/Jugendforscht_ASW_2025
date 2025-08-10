import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    Float,
    Text,
    BLOB,
    ForeignKey,
    Table
)
from sqlalchemy.orm import relationship, declarative_base

# Deklarative Basisklasse erstellen
Base = declarative_base()

# Assoziationstabelle für die Viele-zu-Viele-Beziehung zwischen Protokoll und Material
protokoll_materials_association = Table('protokoll_materials', Base.metadata,
                                        Column('material_protokoll_id', Integer, primary_key=True),
                                        Column('protokoll_id', Integer, ForeignKey('protokolle.protokoll_id')),
                                        Column('material_id', Integer, ForeignKey('materials.material_id')),
                                        Column('quantity', Integer)
                                        )


class Patient(Base):
    __tablename__ = 'patient'
    id = Column(Integer, primary_key=True, autoincrement=True)
    pseudonym = Column(String(255), unique=True, nullable=False)
    real_name = Column(BLOB)
    real_last_name = Column(BLOB)
    birth_day = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.UTC))
    # Beziehung zu Protokolle
    protokolle = relationship("Protokoll", back_populates="patient")


class Alarmierung(Base):
    __tablename__ = 'alarmierungen'
    alert_id = Column(Integer, primary_key=True,  autoincrement=True)
    alert_received = Column(DateTime)
    alert_type = Column(String)
    symptom = Column(String)

    # Beziehung zu Protokolle
    protokoll = relationship("Protokoll", back_populates="alarmierung", uselist=False)


class Teacher(Base):
    __tablename__ = 'teachers'
    teacher_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    house = Column(String)

    # Beziehung zu Protokolle
    protokolle = relationship("Protokoll", back_populates="teacher")


class User(Base):
    __tablename__ = 'users'
    User_ID = Column(Integer, primary_key=True)
    name = Column(String)
    last_name = Column(String)
    lernbegleiter = Column(String)
    kartennummer = Column(String, unique=True)
    permission = Column(String)


class Material(Base):
    __tablename__ = 'materials'
    material_id = Column(Integer, primary_key=True)
    material_name = Column(String, unique=True)
    quantity = Column(Integer)

    # Beziehung über die Assoziationstabelle
    protokolle = relationship(
        "Protokoll",
        secondary=protokoll_materials_association,
        back_populates="materials"
    )


class SaniProtokoll(Base):
    __tablename__ = 'sani_protokoll'
    sani_protokoll_id = Column(Integer, primary_key=True)

    # Fremdschlüssel zu User-Tabelle
    sani1_id = Column(Integer, ForeignKey('users.User_ID'))
    sani2_id = Column(Integer, ForeignKey('users.User_ID'))
    operationsmanager_id = Column(Integer, ForeignKey('users.User_ID'))

    # Fremdschlüssel zu Protokoll (für Eins-zu-Eins-Beziehung)
    protokoll_id = Column(Integer, ForeignKey('protokolle.protokoll_id'))

    # Beziehungen zu User
    sani1 = relationship("User", foreign_keys=[sani1_id])
    sani2 = relationship("User", foreign_keys=[sani2_id])
    operationsmanager = relationship("User", foreign_keys=[operationsmanager_id])


class Protokoll(Base):
    __tablename__ = 'protokolle'
    protokoll_id = Column(Integer, primary_key=True)

    # Fremdschlüssel
    alert_id = Column(Integer, ForeignKey('alarmierungen.alert_id'))
    pseudonym = Column(String, ForeignKey('patient.pseudonym'))  # Im Diagramm als 'pseudonym' bezeichnet
    teacher_id = Column(Integer, ForeignKey('teachers.teacher_id'))  # Im Diagramm als 'teacher' bezeichnet
    medic_id = Column(Integer, ForeignKey('users.User_ID'))

    # Spalten
    operation_end = Column(DateTime)
    status = Column(String)
    pulse = Column(Integer)
    spo2 = Column(Integer)
    blood_pressure = Column(String)
    temperature = Column(Float)
    blood_sugar = Column(Float)
    pain = Column(String)
    measures = Column(Text)
    abhol_massnahme = Column(String)
    parents_notified_by = Column(String)
    parents_notified_at = Column(DateTime)
    hospital = Column(String)

    # Beziehungen
    alarmierung = relationship("Alarmierung", back_populates="protokoll")
    patient = relationship("Patient", back_populates="protokolle")
    teacher = relationship("Teacher", back_populates="protokolle")
    medic = relationship("User", foreign_keys=[medic_id])

    # Eins-zu-Eins-Beziehung zu SaniProtokoll
    sani_protokoll = relationship("SaniProtokoll", uselist=False, backref="protokoll")

    # Viele-zu-Viele-Beziehung zu Material
    materials = relationship(
        "Material",
        secondary=protokoll_materials_association,
        back_populates="protokolle",
        # Ermöglicht den Zugriff auf die Spalten der Assoziationstabelle
        viewonly=True
    )


# Beispiel für die Erstellung der Engine und der Tabellen (optional)
if __name__ == '__main__':
    # Ersetze 'sqlite:///your_database.db' mit deiner Datenbank-Verbindungs-URL
    engine = create_engine('sqlite:///your_database.db')
    Base.metadata.create_all(engine)
    print("Datenbanktabellen wurden erstellt.")