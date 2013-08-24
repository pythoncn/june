# coding: utf-8

import os
import tempfile
from june.app import create_app
from june.models import db, Account


class BaseSuite(object):
    def setUp(self):
        config = {'TESTING': True, 'WTF_CSRF_ENABLED': False}
        config['SECRET_KEY'] = 'secret-key-for-test'

        self.db_fd, self.db_file = tempfile.mkstemp()
        config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % self.db_file

        app = create_app(config)
        self.app = app

        self.client = app.test_client()

        db.create_all()

        if hasattr(self, 'prehook'):
            self.prehook()

    def prepare_account(self):
        with self.app.test_request_context():
            foo = Account(username='foo', email='foo@email.com', password='1')
            foo.role = 'staff'

            bar = Account(username='bar', email='bar@email.com', password='1')
            bar.role = 'user'

            baz = Account(username='baz', email='baz@email.com', password='1')
            db.session.add(foo)
            db.session.add(bar)
            db.session.add(baz)
            db.session.commit()

    def prepare_login(self, username='foo'):
        self.prepare_account()
        self.client.post('/account/signin', data={
            'account': username,
            'password': '1'
        }, follow_redirects=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

        os.close(self.db_fd)
        os.unlink(self.db_file)

        if hasattr(self, 'posthook'):
            self.posthook()
