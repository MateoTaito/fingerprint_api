from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Fingerprint(Base):
    __tablename__ = 'fingerprints'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    finger = Column(String(50), nullable=False)  # e.g., "right-index-finger"
    label = Column(String(100), nullable=True)   # Optional label
    template_data = Column(String, nullable=True)  # Could be empty for fprintd-managed prints
    
    # Relationship with user
    user = relationship("User", back_populates="fingerprints")
    
    def __init__(self, user_id, finger, label=None, template_data=None):
        self.user_id = user_id
        self.finger = finger
        self.label = label
        self.template_data = template_data or f"fprintd://{finger}"
    
    def __repr__(self):
        return f'<Fingerprint {self.id}: {self.finger}>'