from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime
import datetime
Base = declarative_base()

class Alarmierungen(Base):
    __tablename__ = 'alamierungen'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    lastname = Column(String(50))
    teacher = Column(String(50))
    Alarm_recieved = Column(DateTime, default=datetime.datetime.now)
    alarm_type = Column(String(50))
    symptom = Column(String(50))
    operation_end = Column(DateTime)
    operationsmanager= Column(String(50))
    status = Column(String(50))
    pulse = Column(Integer)
    spo2 = Column(Integer)
    blood_pressure = Column(String(30))
    temperature = Column(Integer)
    blood_suger = Column(Integer)
    pain = Column(Integer)  
    measures = Column(String(50))


    def __repr__(self):
        return f"<Alarmierungen(name='{self.name}', description='{self.symptom}')>"
    
class Pseudonymization(Base):
    __tablename__ = 'pseudonymization'

    id = Column(Integer, primary_key=True)
    pseudonym = Column(String(50))
    real_name = Column(String(50))
    real_last_name = Column(String(50))
    created_at = Column(DateTime, default=datetime.datetime.now)
    def __repr__(self):
        return f"<Pseudonymization(real_name='{self.real_name}', real_last_name='{self.real_last_name}', pseudonym='{self.pseudonym}')>"

    def __str__(self):
        return f"Pseudonymization(real_name='{self.real_name}', real_last_name='{self.real_last_name}', pseudonym='{self.pseudonym}')"
    
class Medics(Base):
    __tablename__ = 'Sanitäter'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    lernbegleiter = Column(String(50))
    karten_nummer = Column(String(20))
    premission = Column(String(50))
    last_login = Column(DateTime)

    def __repr__(self):
        return f"<Schueler(id={self.id}, name={self.name}, last_name={self.last_name}, lernbegleiter={self.lernbegleiter}, karten_nummer={self.karten_nummer})>"