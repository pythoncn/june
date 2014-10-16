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
        url_view = self.url_for('topic.view', uid=1)
        rv = self.client.get(url_view)
        assert rv.status_code == 404

        with self.app.test_request_context():
            node = Node(title='june', urlname='june')
            node.save()
        url_create = self.url_for('topic.create', urlname='june')

        rv = self.client.get(url_create)
        assert self.url_for('account.signin') in rv.location
        self.prepare_login()
        rv = self.client.get(url_create)
        assert '</form>' in rv.data

        rv = self.client.post(url_create, data={
            'title': 'june',
            'content': 'june'
        })
        assert url_view in rv.location

        rv = self.client.get(url_view)
        assert b'june</h1>' in rv.data

        rv = self.client.get(url_view + '?page=s')
        assert rv.status_code == 404

        rv = self.client.post(url_view)
        assert b'hits' in rv.data

    def test_fail_create_and_edit(self):
        with self.app.test_request_context():
            topic = self.prepare_topic()
            self.prepare_login('bar')

            rv = self.client.get(self.url_for('topic.edit', uid=topic.id))
            assert rv.status_code == 403

            rv = self.client.get(self.url_for('topic.create', urlname='june'),
                                 follow_redirects=True)
            assert b'New users' in rv.data

    def test_edit_topic(self):
        with self.app.test_request_context():
            topic = self.prepare_topic()
            url = self.url_for('topic.edit', uid=topic.id)

            rv = self.client.get(url)
            assert self.url_for('account.signin') in rv.location

            self.prepare_login()
            rv = self.client.get(url)
            assert '</form>' in rv.data

            rv = self.client.post(url, data={
                'title': 'flask',
                'content': 'june'
            }, follow_redirects=True)
            assert b'flask</h1>' in rv.data

    def test_reply(self):
        with self.app.test_request_context():
            topic = self.prepare_topic()
            self.prepare_login()
            url = self.url_for('topic.reply', uid=topic.id)

            rv = self.client.post(url, data={}, follow_redirects=True)
            assert 'Missing content' in rv.data

            rv = self.client.post(url, data={'content': 'foobar'},
                                  follow_redirects=True)
            assert 'foobar' in rv.data
            rv = self.client.delete(url + '?reply=1')
            assert 'success' in rv.data

    def test_topics(self):
        url = self.url_for('topic.topics')

        rv = self.client.get(url)
        assert '<title>Topics' in rv.data

        rv = self.client.get(url + '?page=s')
        assert rv.status_code == 404

    def test_latest(self):
        url = self.url_for('topic.latest')

        rv = self.client.get(url)
        assert '<title>Topics' in rv.data

        rv = self.client.get(url + '?page=s')
        assert rv.status_code == 404

    def test_desert(self):
        url = self.url_for('topic.desert')

        rv = self.client.get(url)
        assert '<title>Topics' in rv.data

        rv = self.client.get(url + '?page=s')
        assert rv.status_code == 404
