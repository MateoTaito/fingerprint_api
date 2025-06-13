from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from database import Base
from models.user import User
from models.fingerprint import Fingerprint

class DatabaseService:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def add_user(self, user):
        session = self.Session()
        try:
            session.add(user)
            session.commit()
            return user
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error adding user: {e}")
            raise
        finally:
            session.close()

    def get_user_by_username(self, username):
        session = self.Session()
        try:
            return session.query(User).filter(User.username == username).first()
        except SQLAlchemyError as e:
            print(f"Error retrieving user: {e}")
            return None
        finally:
            session.close()

    def get_user(self, user_id):
        session = self.Session()
        try:
            return session.query(User).filter(User.id == user_id).first()
        except SQLAlchemyError as e:
            print(f"Error retrieving user: {e}")
            return None
        finally:
            session.close()

    def get_all_users(self):
        session = self.Session()
        try:
            return session.query(User).all()
        except SQLAlchemyError as e:
            print(f"Error retrieving users: {e}")
            return []
        finally:
            session.close()

    def update_user(self, user):
        session = self.Session()
        try:
            session.merge(user)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error updating user: {e}")
            raise
        finally:
            session.close()

    def delete_user(self, user):
        session = self.Session()
        try:
            session.delete(user)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error deleting user: {e}")
            raise
        finally:
            session.close()

    def add_fingerprint(self, fingerprint):
        session = self.Session()
        try:
            session.add(fingerprint)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error adding fingerprint: {e}")
            raise
        finally:
            session.close()

    def get_fingerprints_by_user(self, user_id):
        session = self.Session()
        try:
            return session.query(Fingerprint).filter(Fingerprint.user_id == user_id).all()
        except SQLAlchemyError as e:
            print(f"Error retrieving fingerprints: {e}")
            return []
        finally:
            session.close()

    def close(self):
        if hasattr(self, 'engine'):
            self.engine.dispose()