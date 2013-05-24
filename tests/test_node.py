# coding: utf-8

from .suite import BaseSuite
from june.models import Node


class TestNode(BaseSuite):
    def test_get(self):
        rv = self.client.get('/node/create')
        assert '/account/signin' in rv.location

    def test_create(self):
        self.prepare_login()
        rv = self.client.get('/node/create')
        assert '</form>' in rv.data

        rv = self.client.post('/node/create', data={
            'title': 'june',
            'urlname': 'june'
        })
        assert '/node/june' in rv.location

        # re create
        rv = self.client.post('/node/create', data={
            'title': 'june',
            'urlname': 'june'
        })
        assert 'node exists' in rv.data

    def test_edit(self):
        self.prepare_login()
        with self.app.test_request_context():
            node = Node(title='june', urlname='june')
            node.save()

        rv = self.client.get('/node/june/edit')
        assert '</form>' in rv.data

        # re edit
        rv = self.client.post('/node/june/edit', data={
            'title': 'june',
            'urlname': 'june'
        })
        assert '/node/june' in rv.location

        rv = self.client.post('/node/june/edit', data={
            'title': 'june',
            'urlname': 'foo'
        })
        assert '/node/foo' in rv.location

    def test_nodes(self):
        rv = self.client.get('/node/')
        assert '<title>Nodes' in rv.data

    def test_view(self):
        rv = self.client.get('/node/june')
        assert rv.status_code == 404

        with self.app.test_request_context():
            node = Node(title='june', urlname='june')
            node.save()
            assert repr(node) == '<Node: june>'

        rv = self.client.get('/node/june')
        assert rv.status_code == 200

        rv = self.client.get('/node/june?page=s')
        assert rv.status_code == 404

        self.prepare_login()
        with self.app.test_request_context():
            node.description = 'june'
            node.save()
        rv = self.client.get('/node/june')
        assert rv.status_code == 200
