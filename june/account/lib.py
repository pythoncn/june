from july.web import JulyHandler
from july.database import db
from july.cache import get_cache_list
from .models import Member, Notification, Social


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

    def create_notification(self, receiver, content, refer, **kwargs):
        if not self.current_user:
            return
        if not isinstance(receiver, (int, long)):
            # receiver is username
            receiver = Member.query.filter_by(username=receiver).value('id')

        if not receiver:
            self.flash_message('There is no such member', 'error')
            return
        if receiver == self.current_user.id:
            #: can't send notification to oneself
            return
        if 'exception' in kwargs and receiver == kwargs['exception']:
            return

        data = Notification(sender=self.current_user.id, receiver=receiver,
                            content=content, refer=refer)
        if 'type' in kwargs:
            data.type = kwargs['type']
        db.session.add(data)


def get_full_notifications(messages):
    users = get_cache_list(Member, (m.sender for m in messages), 'member:')
    for msg in messages:
        if msg.sender in users:
            msg.who = users[msg.sender]
            yield msg


def get_social_map(user_id):
    dct = {}
    for network in Social.query.filter_by(user_id=user_id):
        dct[network.service] = network

    return dct
