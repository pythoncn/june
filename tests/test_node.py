# coding: utf-8

from .suite import BaseSuite
from june.models import Node


class TestNode(BaseSuite):
    def test_get(self):
        rv = self.client.get(self.url_for('node.create'))
        assert self.url_for('account.signin') in rv.location

    def test_create(self):
        self.prepare_login()
        url = self.url_for('node.create')
        rv = self.client.get(url)
        assert '</form>' in rv.data

        rv = self.client.post(url, data={
            'title': 'june',
            'urlname': 'june'
        })
        assert self.url_for('node.view', urlname='june') in rv.location

        # re create
        rv = self.client.post(url, data={
            'title': 'june',
            'urlname': 'june'
        })
        assert 'node exists' in rv.data

    def test_edit(self):
        self.prepare_login()
        with self.app.test_request_context():
            node = Node(title='june', urlname='june')
            node.save()
        url = self.url_for('node.edit', urlname='june')

        rv = self.client.get(url)
        assert '</form>' in rv.data

        # re edit
        rv = self.client.post(url, data={
            'title': 'june',
            'urlname': 'june'
        })
        assert self.url_for('node.view', urlname='june') in rv.location

        rv = self.client.post(url, data={
            'title': 'june',
            'urlname': 'foo'
        })
        assert self.url_for('node.view', urlname='foo') in rv.location

    def test_nodes(self):
        rv = self.client.get(self.url_for('node.nodes'))
        assert '<title>Nodes' in rv.data

    def test_view(self):
        url = self.url_for('node.view', urlname='june')

        rv = self.client.get(url)
        assert rv.status_code == 404

        with self.app.test_request_context():
            node = Node(title='june', urlname='june')
            node.save()
            assert repr(node) == '<Node: june>'

        rv = self.client.get(url)
        assert rv.status_code == 200

        rv = self.client.get(url + '?page=s')
        assert rv.status_code == 404

        self.prepare_login()
        with self.app.test_request_context():
            node.description = 'june'
            node.save()
        rv = self.client.get(url)
        assert rv.status_code == 200
