# coding: utf-8

from .suite import BaseSuite


class TestUser(BaseSuite):
    def test_users(self):
        url = self.url_for('user.users')

        rv = self.client.get(url)
        assert '<title>Users' in rv.data

        rv = self.client.get(url + '?page=s')
        assert rv.status_code == 404

    def test_city(self):
        url = self.url_for('user.city', city='hangzhou')

        rv = self.client.get(url)
        assert '<title>hangzhou' in rv.data

        rv = self.client.get(url + '?page=s')
        assert rv.status_code == 404

    def test_view(self):
        self.prepare_account()

        rv = self.client.get(self.url_for('user.view', username='foo'))
        assert '<title>foo' in rv.data

        rv = self.client.get(self.url_for('user.topics', username='foo'))
        assert rv.status_code == 200
        rv = self.client.get(self.url_for('user.topics', username='foo'
                                          ) + '?page=s')
        assert rv.status_code == 404
