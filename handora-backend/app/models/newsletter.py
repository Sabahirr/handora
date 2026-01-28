from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class Newsletter(Base):
    __tablename__ = "newsletter"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    subscribed_at = Column(DateTime, default=datetime.utcnow)