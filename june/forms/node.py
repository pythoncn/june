# coding: utf-8

from flask.ext.wtf import TextField, TextAreaField
from flask.ext.babel import lazy_gettext as _

from ._base import BaseForm, required


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
