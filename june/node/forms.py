from flask.ext.wtf import Form
from flask.ext.wtf import TextField, TextAreaField, IntegerField
from flask.ext.wtf import Required, Regexp
from flask.ext.babel import lazy_gettext as _
from .models import db, Node


messages = [
    _('Only lower English characters are allowed'),
]


class CreateNodeForm(Form):
    title = TextField(
        _('Title'), validators=[Required()]
    )
    slug = TextField(
        _('Slug'),
        validators=[Required(), Regexp(r'[a-z]+', message=messages[0])],
        description=messages[0]
    )
    fgcolor = TextField(_('Front Color'))
    bgcolor = TextField(_('Background Color'))
    description = TextAreaField(
        _('Description')
    )
    header = TextAreaField(
        _('Header')
    )
    sidebar = TextAreaField(
        _('Sidebar')
    )
    footer = TextAreaField(
        _('Footer')
    )
    limit_role = IntegerField(_('Role Limitation'), default=0)

    def save(self):
        node = Node(
            title=self.title.data,
            slug=self.slug.data,
            fgcolor=self.fgcolor.data,
            bgcolor=self.bgcolor.data,
            description=self.description.data,
            header=self.header.data,
            sidebar=self.sidebar.data,
            footer=self.footer.data,
            limit_role=self.limit_role.data,
        )
        db.session.add(node)
        db.session.commit()
        return node
