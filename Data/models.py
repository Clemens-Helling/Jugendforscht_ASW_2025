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
    measures = Column(String(200))
    operation_end = Column(DateTime)
    operationsmanager= Column(String(50))
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