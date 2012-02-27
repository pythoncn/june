from june.lib.handler import BaseHandler


class HomeHandler(BaseHandler):
    def get(self):
        self.write(self.user_agent)
        if self.current_user:
            self.write(self.current_user.username)


handlers = [
    ('/', HomeHandler),
]
