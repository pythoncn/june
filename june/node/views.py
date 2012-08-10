from flask import Blueprint
from flask import render_template, redirect, url_for
from .forms import CreateNodeForm
from june.account.decorators import require_admin


app = Blueprint('node', __name__, template_folder='templates')


@app.route('/<slug>', methods=['GET'])
def view(slug):
    return slug


@app.route('/-create', methods=['GET', 'POST'])
@require_admin
def create():
    form = CreateNodeForm()
    if form.validate_on_submit():
        node = form.save()
        return redirect(url_for('.view', slug=node.slug))
    return render_template('node/create.html', form=form)
