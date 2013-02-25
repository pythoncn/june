# coding: utf-8

from flask.ext.wtf import TextField, TextAreaField
from flask.ext.babel import lazy_gettext as _

from ._base import BaseForm


class NodeForm(Form):
    title = TextField(
        _('Title'), validators=[Required()],
        description=_('The screen title of the node')
    )
    slug = TextField(
        _('URL'), validators=[Required()],
        description=_('The url name of the node')
    )
    description = TextAreaField(_('Description'))
