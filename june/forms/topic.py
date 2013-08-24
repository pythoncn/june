# coding: utf-8

from wtforms import TextField, TextAreaField
from wtforms.validators import DataRequired
from flask.ext.babel import lazy_gettext as _

from ._base import BaseForm
from ..models import Topic, Reply


class TopicForm(BaseForm):
    title = TextField(
        _('Title'), validators=[DataRequired()],
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
    content = TextAreaField(_('Content'), validators=[DataRequired()])

    def save(self, user, topic):
        item = Reply(**self.data)
        return item.save(user=user, topic=topic)
