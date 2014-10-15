# coding: utf-8

from .suite import BaseSuite


class TestSignup(BaseSuite):
    def test_get(self):
        rv = self.client.get(self.url_for('account.signup'))
        assert '</form>' in rv.data

    def test_required_fields(self):
        rv = self.client.post(self.url_for('account.signup'))
        assert 'This field is required' in rv.data

    def test_invalid_email(self):
        rv = self.client.post(self.url_for('account.signup'), data={
            'username': 'lepture',
            'email': 'lepture',
            'password': '1'
        })
        assert 'Invalid email address' in rv.data

    def test_reserved_username(self):
        rv = self.client.post(self.url_for('account.signup'), data={
            'username': 'root',
            'email': 'me@lepture.com',
            'password': '1'
        })
        assert 'reserved' in rv.data

    def test_success(self):
        rv = self.client.post(self.url_for('account.signup'), data={
            'username': 'lepture',
            'email': 'me@lepture.com',
            'password': '1'
        })
        assert rv.status_code == 302


class TestSignin(BaseSuite):
    def test_get(self):
        rv = self.client.get(self.url_for('account.signin'))
        assert '</form>' in rv.data

    def test_invalid_password(self):
        self.prepare_account()
        rv = self.client.post(self.url_for('account.signin'), data={
            'account': 'foo',
            'password': '2'
        })
        assert b'error' in rv.data

    def test_invalid_account(self):
        rv = self.client.post(self.url_for('account.signin'), data={
            'account': 'foo',
            'password': '1'
        })
        assert b'error' in rv.data

    def test_success(self):
        self.prepare_account()
        rv = self.client.post(self.url_for('account.signin'), data={
            'account': 'foo',
            'password': '1'
        })
        assert rv.status_code == 302


class TestFind(BaseSuite):
    def test_get(self):
        rv = self.client.get(self.url_for('account.find'))
        assert '</form>' in rv.data

    def test_post(self):
        self.prepare_account()
        rv = self.client.post(self.url_for('account.find'), data={
            'account': 'foo',
        })
        assert '</table>' in rv.data
