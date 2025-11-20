import datetime

from sqlalchemy import (BLOB, Column, DateTime, Float, ForeignKey, Integer,
                        String, Text, create_engine)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Patient(Base):
    __tablename__ = "patient"
    id = Column(Integer, primary_key=True, autoincrement=True)
    pseudonym = Column(String(255), unique=True, nullable=False)
    real_name = Column(BLOB)
    real_last_name = Column(BLOB)
    birth_day = Column(DateTime)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    protokolle = relationship("Protokoll", back_populates="patient")


class Alarmierung(Base):
    __tablename__ = "alarmierungen"
    alert_id = Column(Integer, primary_key=True, autoincrement=True)
    alert_received = Column(DateTime)
    alert_type = Column(String(255))
    symptom = Column(String(255))

    protokoll = relationship("Protokoll", back_populates="alarmierung", uselist=False)


class Teacher(Base):
    __tablename__ = "teachers"
    teacher_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    house = Column(String(255))

    protokolle = relationship("Protokoll", back_populates="teacher")


class User(Base):
    __tablename__ = "users"
    User_ID = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    last_name = Column(String(255))
    lernbegleiter = Column(String(255))
    karten_nummer = Column(String(255), unique=True)
    permission = Column(String(255))


class Material(Base):
    __tablename__ = "materials"
    material_id = Column(Integer, primary_key=True, autoincrement=True)
    material_name = Column(String(255), unique=True)
    quantity = Column(Integer)
    expires_at = Column(DateTime)  # In MySQL vorhanden
    minimum_stock = Column(Integer)

    protokoll_materials = relationship("ProtokollMaterials", back_populates="material")


class ProtokollMaterials(Base):
    __tablename__ = "protokoll_materials"
    material_protokoll_id = Column(Integer, primary_key=True, autoincrement=True)
    protokoll_id = Column(Integer, ForeignKey("protokolle.protokoll_id"))
    material_id = Column(Integer, ForeignKey("materials.material_id"))
    quantity = Column(Integer)

    protokoll = relationship("Protokoll", back_populates="protokoll_materials")
    material = relationship("Material", back_populates="protokoll_materials")


class SaniProtokoll(Base):
    __tablename__ = "sani_protokoll"
    sani_protokoll_id = Column(Integer, primary_key=True, autoincrement=True)
    sani1 = Column(Integer, ForeignKey("users.User_ID"))
    sani2 = Column(Integer, ForeignKey("users.User_ID"))
    operationsmanager = Column(Integer, ForeignKey("users.User_ID"))
    protokoll_id = Column(
        Integer, ForeignKey("protokolle.protokoll_id"), unique=True
    )  # <-- Hinzugefügt

    sani1_fk = relationship("User", foreign_keys=[sani1])
    sani2_fk = relationship("User", foreign_keys=[sani2])
    operationsmanager_fk = relationship("User", foreign_keys=[operationsmanager])
    protokoll = relationship("Protokoll", back_populates="sani_protokoll")


class Protokoll(Base):
    __tablename__ = "protokolle"
    protokoll_id = Column(Integer, primary_key=True, autoincrement=True)
    alert_id = Column(Integer, ForeignKey("alarmierungen.alert_id"))
    pseudonym = Column(String(255), ForeignKey("patient.pseudonym"))
    teacher_id = Column(Integer, ForeignKey("teachers.teacher_id"))
    medic_id = Column(Integer, ForeignKey("users.User_ID"))

    operation_end = Column(DateTime)
    status = Column(String(255))
    pulse = Column(Integer)
    spo2 = Column(Integer)
    blood_pressure = Column(String(255))
    temperature = Column(Float)
    blood_sugar = Column(Float)
    pain = Column(String(255))
    measures = Column(Text)
    abhol_massnahme = Column(String(255))
    parents_notified_by = Column(String(255))
    parents_notified_at = Column(DateTime)
    hospital = Column(String(255))

    alarmierung = relationship("Alarmierung", back_populates="protokoll")
    patient = relationship("Patient", back_populates="protokolle")
    teacher = relationship("Teacher", back_populates="protokolle")
    medic = relationship("User", foreign_keys=[medic_id])
    protokoll_materials = relationship("ProtokollMaterials", back_populates="protokoll")
    sani_protokoll = relationship(
        "SaniProtokoll", back_populates="protokoll", uselist=False
    )

class UserSettings(Base):
    __tablename__ = "user_settings"
    setting_id = Column(Integer, primary_key=True, autoincrement=True)
    notification_method = Column(String(100))
    ntfy_url = Column(String(150))
    divera_key = Column(String(250))
    divera_ric = Column(String(150))

    def __repr__(self):
        return f"<UserSettings(setting_id={self.setting_id}, name={self.name}, value={self.value})>"

if __name__ == "__main__":
    engine = create_engine(
        "mysql+mysqlconnector://user:password@localhost/deine_datenbank", echo=True
    )
    Base.metadata.create_all(engine)
