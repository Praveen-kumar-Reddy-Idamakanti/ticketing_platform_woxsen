from flask_login import UserMixin

class Register(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data.get("_id"))  # MongoDB uses `_id` by default
        self.username = user_data.get("username")
        self.email = user_data.get("email")

    def get_id(self):
        return self.email  # Use email as a unique identifier
