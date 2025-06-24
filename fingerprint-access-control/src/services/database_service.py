from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
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
            # Refresh to get the ID and detach from session
            session.refresh(user)
            session.expunge(user)
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
            user = session.query(User).options(joinedload(User.fingerprints)).filter(User.username == username).first()
            if user:
                session.expunge(user)  # Detach from session
            return user
        except SQLAlchemyError as e:
            print(f"Error retrieving user: {e}")
            return None
        finally:
            session.close()

    def get_user(self, user_id):
        session = self.Session()
        try:
            user = session.query(User).options(joinedload(User.fingerprints)).filter(User.id == user_id).first()
            if user:
                session.expunge(user)  # Detach from session
            return user
        except SQLAlchemyError as e:
            print(f"Error retrieving user: {e}")
            return None
        finally:
            session.close()

    def get_all_users(self):
        session = self.Session()
        try:
            # Use joinedload to eagerly load fingerprints relationship
            users = session.query(User).options(joinedload(User.fingerprints)).all()
            # Detach from session to avoid lazy loading issues
            for user in users:
                session.expunge(user)
            return users
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
            fingerprints = session.query(Fingerprint).filter(Fingerprint.user_id == user_id).all()
            # Detach from session
            for fp in fingerprints:
                session.expunge(fp)
            return fingerprints
        except SQLAlchemyError as e:
            print(f"Error retrieving fingerprints: {e}")
            return []
        finally:
            session.close()

    def delete_fingerprint(self, fingerprint):
        """Delete a specific fingerprint record from the database"""
        session = self.Session()
        try:
            # Get the fingerprint from this session
            fingerprint_in_session = session.merge(fingerprint)
            session.delete(fingerprint_in_session)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error deleting fingerprint: {e}")
            raise
        finally:
            session.close()

    def close(self):
        if hasattr(self, 'engine'):
            self.engine.dispose()