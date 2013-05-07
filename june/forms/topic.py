# coding: utf-8

from flask.ext.wtf import TextField, TextAreaField
from flask.ext.babel import lazy_gettext as _

from ._base import BaseForm, required
from ..models import Topic


class TopicForm(BaseForm):
    title = TextField(
        _('Title'), validators=[required],
        description=_('The title of the topic')
    )
    content = TextAreaField(_('Content'))

    def save(self, user):
        topic = Topic(**self.data)
        topic.account_id = user.id
        topic.save()
        return topic
