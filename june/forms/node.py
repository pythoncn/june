# coding: utf-8

from flask.ext.wtf import TextField, TextAreaField, IntegerField
from flask.ext.babel import lazy_gettext as _

from ._base import BaseForm, required
from ..models import Node


class NodeForm(BaseForm):
    title = TextField(
        _('Title'), validators=[required],
        description=_('The screen title of the node')
    )
    urlname = TextField(
        _('URL'), validators=[required],
        description=_('The url name of the node')
    )
    description = TextAreaField(_('Description'))
    role = IntegerField(description=_('Required role'), default=1)

    def save(self):
        node = Node(**self.data)
        node.save()
        return node
