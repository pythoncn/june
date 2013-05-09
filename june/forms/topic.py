# coding: utf-8

from flask.ext.wtf import TextField, TextAreaField
from flask.ext.babel import lazy_gettext as _

from ._base import BaseForm, required
from ..models import Topic, Reply


class TopicForm(BaseForm):
    title = TextField(
        _('Title'), validators=[required],
        description=_('Title of the topic')
    )
    content = TextAreaField(
        _('Content'),
        description=_('Content of the topic')
    )

    def save(self, user, node):
        topic = Topic(**self.data)
        return topic.save(user=user, node=node)


class ReplyForm(BaseForm):
    content = TextAreaField(_('Content'), validators=[required])

    def save(self, user, topic):
        item = Reply(**self.data)
        return item.save(user=user, topic=topic)
