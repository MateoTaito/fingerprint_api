from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Fingerprint(Base):
    __tablename__ = 'fingerprints'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    template_data = Column(String, nullable=False)
    
    # Relationship with user
    user = relationship("User", back_populates="fingerprints")
    
    def __init__(self, user_id, template_data):
        self.user_id = user_id
        self.template_data = template_data
    
    def __repr__(self):
        return f'<Fingerprint {self.id}>'