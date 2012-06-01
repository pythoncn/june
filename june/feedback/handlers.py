# -*- coding: utf-8 -*-

import hashlib

from tornado.escape import utf8

from july.app import JulyApp
from july.cache import cache
from july.database import db

from june.account.lib import UserHandler
from june.account.decorators import require_user

from .models import Feedback

class CreateFeedbackHandler(UserHandler):
    @require_user
    def get(self):
        self.render("create_feedback.html")

    @require_user
    def post(self):
        title = self.get_argument('title', None)
        content = self.get_argument('content', None)
        if not (title and content):
            self.flash_message('Please fill in required fields', 'error')
            self.render("create_feedback.html")
            return

        key = hashlib.md5(utf8(content)).hexdigest()
        url = cache.get(key)
        if url:
            self.redirect(url)
            return

        feedback = Feedback(title=title, content=content)
        feedback.sender = self.current_user.id

        db.session.add(feedback)
        db.session.commit()

        self.flash_message('Thank you for your feedback', 'info')
        self.redirect('/')

handlers = [
    ('/create', CreateFeedbackHandler),
]

app = JulyApp('feedback', __name__, handlers=handlers)
