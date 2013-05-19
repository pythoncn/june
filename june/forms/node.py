# coding: utf-8

from flask.ext.wtf import TextField, TextAreaField, SelectField
from flask.ext.wtf import DataRequired
from flask.ext.babel import lazy_gettext as _

from ._base import BaseForm
from ..models import Node


class NodeForm(BaseForm):
    title = TextField(
        _('Title'), validators=[DataRequired()],
        description=_('The screen title of the node')
    )
    urlname = TextField(
        _('URL'), validators=[DataRequired()],
        description=_('The url name of the node')
    )
    description = TextAreaField(_('Description'))
    role = SelectField(
        _('Role'),
        description=_('Required role'),
        choices=[
            ('user', _('User')),
            ('staff', _('Staff')),
            ('admin', _('Admin'))
        ],
        default='user',
    )

    def validate_urlname(self, field):
        if self._obj and self._obj.urlname == field.data:
            return
        if Node.query.filter_by(urlname=field.data).count():
            raise ValueError(_('The node exists'))

    def save(self):
        node = Node(**self.data)
        node.save()
        return node
