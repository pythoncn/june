from july.web import JulyHandler
from .models import Member


class UserHandler(JulyHandler):
    def get_current_user(self):
        cookie = self.get_secure_cookie("user")
        if not cookie:
            return None
        try:
            id, token = cookie.split('/')
            id = int(id)
        except:
            self.clear_cookie("user")
            return None
        user = Member.query.filter_by(id=id).first()
        if not user:
            return None
        if token == user.token:
            return user
        self.clear_cookie("user")
        return None

    @property
    def next_url(self):
        next_url = self.get_argument("next", None)
        return next_url or '/'

    def check_permission_of(self, model):
        user = self.current_user
        if user.is_staff or model.user_id == user.id:
            return True
        self.flash_message(
            "You have no permission",
            "warn"
        )
        self.send_error(403)
        return False
