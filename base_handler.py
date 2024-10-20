import tornado.web
from utils import decode_jwt

# Handler for get user task
class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        token = self.request.headers.get("Authorization")
        if not token:
            return None
        try:
            payload = decode_jwt(token.split(" ")[1])
            return payload["user_id"]
        except Exception:
            return None

    def prepare(self):
        if self.request.method != "OPTIONS" and not self.current_user:
            raise tornado.web.HTTPError(401, "Authentication required")