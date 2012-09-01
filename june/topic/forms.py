from flask.ext.wtf import Form


class TopicForm(Form):
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

    def save(self, obj=None):
        if not obj:
            obj = Node()

        for name, data in self.data.iteritems():
            setattr(obj, name, data)

        db.session.add(obj)
        db.session.commit()
        return obj
