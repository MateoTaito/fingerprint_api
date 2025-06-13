from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(120), nullable=False)
    
    # Relationship with fingerprints
    fingerprints = relationship("Fingerprint", back_populates="user")
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    def __repr__(self):
        return f'<User {self.username}>'