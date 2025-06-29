from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class LeadBase(BaseModel):
    company_name: str
    contact_person: str
    email: EmailStr
    phone: str
    profession: str
    chatbot_topic: str
    data_source: str
    use_case: str
    additional_specs: Optional[str] = None

class LeadCreate(LeadBase):
    pass

class LeadResponse(LeadBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
   
    class Config:
        from_attributes = True