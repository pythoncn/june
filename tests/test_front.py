# coding: utf-8

from .suite import BaseSuite


class TestFront(BaseSuite):
    def test_get(self):
        rv = self.client.get(self.url_for('front.home'))
        assert rv.status_code == 200
