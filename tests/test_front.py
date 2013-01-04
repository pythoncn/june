from june.app import create_app


class TestHomePage(object):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_get(self):
        rv = self.client.get('/')
        assert rv.status_code == 200
