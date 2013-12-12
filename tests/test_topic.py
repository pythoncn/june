# coding: utf-8

from .suite import BaseSuite
from june.models import Node, Topic, db


class TestTopic(BaseSuite):
    def prepare_topic(self):
        node = Node(title='june', urlname='june')
        db.session.add(node)
        topic = Topic(title='june', content='june',
                      account_id=1, node_id=1)
        db.session.add(topic)
        db.session.commit()
        return topic

    def test_create_and_view(self):
        rv = self.client.get('/topic/1')
        assert rv.status_code == 404

        with self.app.test_request_context():
            node = Node(title='june', urlname='june')
            node.save()

        rv = self.client.get('/topic/create/june')
        assert '/account/signin' in rv.location
        self.prepare_login()
        rv = self.client.get('/topic/create/june')
        assert '</form>' in rv.data

        rv = self.client.post('/topic/create/june', data={
            'title': 'june',
            'content': 'june'
        })
        assert '/topic/1' in rv.location

        rv = self.client.get('/topic/1')
        assert b'june</h1>' in rv.data

        rv = self.client.get('/topic/1?page=s')
        assert rv.status_code == 404

        rv = self.client.post('/topic/1')
        assert b'hits' in rv.data

    def test_fail_create_and_edit(self):
        with self.app.test_request_context():
            topic = self.prepare_topic()
            self.prepare_login('bar')
            rv = self.client.get('/topic/%d/edit' % topic.id)
            assert rv.status_code == 403

            rv = self.client.get('/topic/create/june', follow_redirects=True)
            assert b'New users' in rv.data

    def test_edit_topic(self):
        with self.app.test_request_context():
            topic = self.prepare_topic()
            rv = self.client.get('/topic/%d/edit' % topic.id)
            assert '/account/signin' in rv.location

            self.prepare_login()
            rv = self.client.get('/topic/%d/edit' % topic.id)
            assert '</form>' in rv.data

            rv = self.client.post('/topic/%d/edit' % topic.id, data={
                'title': 'flask',
                'content': 'june'
            }, follow_redirects=True)
            assert b'flask</h1>' in rv.data

    def test_reply(self):
        with self.app.test_request_context():
            topic = self.prepare_topic()
            self.prepare_login()
            rv = self.client.post('/topic/%d/reply' % topic.id, data={
            }, follow_redirects=True)
            assert 'Missing content' in rv.data

            rv = self.client.post('/topic/%d/reply' % topic.id, data={
                'content': 'foobar'
            }, follow_redirects=True)
            assert 'foobar' in rv.data
            rv = self.client.delete('/topic/%d/reply?reply=1' % topic.id)
            assert 'success' in rv.data

    def test_topics(self):
        rv = self.client.get('/topic/')
        assert '<title>Topics' in rv.data

        rv = self.client.get('/topic/?page=s')
        assert rv.status_code == 404

    def test_latest(self):
        rv = self.client.get('/topic/latest')
        assert '<title>Topics' in rv.data

        rv = self.client.get('/topic/latest?page=s')
        assert rv.status_code == 404

    def test_desert(self):
        rv = self.client.get('/topic/desert')
        assert '<title>Topics' in rv.data

        rv = self.client.get('/topic/desert?page=s')
        assert rv.status_code == 404
