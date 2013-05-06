# coding: utf-8

from flask.ext.wtf import Form
from flask.ext.wtf import Required
from flask.ext.babel import lazy_gettext as _


# because we need lazy gettext
required = Required(message=_('This field is required.'))
# TODO: more validators


class BaseForm(Form):
    def __init__(self, *args, **kwargs):
        self._obj = kwargs.get('obj', None)
        super(BaseForm, self).__init__(*args, **kwargs)
