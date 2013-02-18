# coding: utf-8

from .suite import BaseSuite


class TestFront(BaseSuite):
    def test_get(self):
        rv = self.client.get('/')
        assert rv.status_code == 200
