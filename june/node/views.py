from flask import Blueprint
from flask import render_template, redirect, url_for
from .forms import NodeForm
from .models import Node
from june.account.decorators import require_admin


app = Blueprint('node', __name__, template_folder='templates')


@app.route('/')
def index():
    nodes = Node.query.all()
    return render_template('node/index.html', nodes=nodes)


@app.route('/<slug>')
def topics(slug):
    node = Node.query.filter_by(slug=slug).first_or_404()
    return render_template('node/topics.html', node=node)


@app.route('/-create', methods=['GET', 'POST'])
@require_admin
def create():
    form = NodeForm()
    if form.validate_on_submit():
        node = form.save()
        return redirect(url_for('.topics', slug=node.slug))
    return render_template('node/create.html', form=form)


@app.route('/<slug>/-edit', methods=['GET', 'POST'])
@require_admin
def edit(slug):
    node = Node.query.filter_by(slug=slug).first_or_404()
    form = NodeForm(obj=node)
    if form.validate_on_submit():
        node = form.save(node)
        return redirect(url_for('.topics', slug=node.slug))
    return render_template('node/create.html', form=form)
