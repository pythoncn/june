# coding: utf-8

import os
import tempfile
from june.app import create_app
from june.models import db


class BaseSuite(object):
    def setUp(self):
        config = {'TESTING': True, 'CSRF_ENABLED': False}
        config['SECRET_KEY'] = 'secret-key-for-test'

        self.db_fd, self.db_file = tempfile.mkstemp()
        config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///%s' % self.db_file

        app = create_app(config)
        self.app = app

        self.client = app.test_client()

        db.create_all()

        if hasattr(self, 'prehook'):
            self.prehook()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_file)

        if hasattr(self, 'posthook'):
            self.posthook()
