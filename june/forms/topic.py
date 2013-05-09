# coding: utf-8

from flask.ext.wtf import TextField, TextAreaField
from flask.ext.babel import lazy_gettext as _

from ._base import BaseForm, required
from ..models import Topic, Reply


class TopicForm(BaseForm):
    title = TextField(
        _('Title'), validators=[required],
        description=_('The title of the topic')
    )
    content = TextAreaField(_('Content'))

    def save(self, user, node):
        topic = Topic(**self.data)
        topic.account_id = user.id
        topic.node_id = node.id
        topic.save()
        return topic


class ReplyForm(BaseForm):
    content = TextAreaField(_('Content'), validators=[required])

    def save(self, user, topic):
        item = Reply(**self.data)
        item.account_id = user.id
        item.topic_id = topic.id
        item.save()
        return item
