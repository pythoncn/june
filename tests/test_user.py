# coding: utf-8

from .suite import BaseSuite


class TestUser(BaseSuite):
    def test_users(self):
        rv = self.client.get('/user/')
        assert '<title>Users' in rv.data

        rv = self.client.get('/user/?page=s')
        assert rv.status_code == 404

    def test_city(self):
        rv = self.client.get('/user/in/hangzhou')
        assert '<title>hangzhou' in rv.data

        rv = self.client.get('/user/in/hangzhou?page=s')
        assert rv.status_code == 404

    def test_view(self):
        self.prepare_account()
        rv = self.client.get('/user/foo')
        assert '<title>foo' in rv.data

        rv = self.client.get('/user/foo/topics')
        assert rv.status_code == 200
        rv = self.client.get('/user/foo/topics?page=s')
        assert rv.status_code == 404
