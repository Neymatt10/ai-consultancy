from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database.connection import Base

class Lead(Base):
    __tablename__ = "leads"
   
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(255), nullable=False)
    contact_person = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=False)
    profession = Column(String(255), nullable=False)
    chatbot_topic = Column(String(255), nullable=False)
    data_source = Column(Text, nullable=False)
    use_case = Column(Text, nullable=False)
    additional_specs = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())