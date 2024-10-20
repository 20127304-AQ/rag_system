import uuid
from tornado.web import RequestHandler
from utils import generate_jwt

# Handling authentication
class AuthHandler(RequestHandler):
    def post(self):
        user_id = str(uuid.uuid4())  # Generate a unique user ID
        token = generate_jwt(user_id)
        self.write({"token": token, "user_id": user_id})