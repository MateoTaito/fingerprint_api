from models.user import User

class UserService:
    def __init__(self, db_service):
        self.db_service = db_service

    def register_user(self, username, password):
        if self.db_service.get_user_by_username(username):
            raise ValueError("Username already exists.")
        
        new_user = User(username=username, password=password)
        self.db_service.add_user(new_user)
        return new_user

    def get_user(self, username):
        user = self.db_service.get_user_by_username(username)
        if not user:
            raise ValueError("User not found.")
        return user

    def update_user(self, username, new_data):
        user = self.get_user(username)
        # Note: User model doesn't have an update method, you'll need to implement this
        for key, value in new_data.items():
            setattr(user, key, value)
        self.db_service.update_user(user)

    def delete_user(self, username):
        user = self.get_user(username)
        self.db_service.delete_user(user)

    def list_users(self):
        return self.db_service.get_all_users()