# coding: utf-8

from flask import Blueprint, request
from flask import render_template, redirect, url_for, abort
from ..models import Node, Topic
from ..forms import NodeForm
from ..helpers import require_staff, force_int


__all__ = ['bp']

bp = Blueprint('node', __name__)


@bp.route('/')
def nodes():
    nodes = Node.query.all()
    return render_template('node/nodes.html', nodes=nodes)


@bp.route('/create', methods=['GET', 'POST'])
@require_staff
def create():
    """
    Create a node by staff members.
    """
    form = NodeForm()
    if form.validate_on_submit():
        node = form.save()
        return redirect(url_for('.view', urlname=node.urlname))
    return render_template('node/create.html', form=form)


@bp.route('/<urlname>')
def view(urlname):
    """
    The view page of the Node.

    The node page should contain the information of the node, and topics
    in this node.

    :param urlname: the urlname of the Node model
    """

    node = Node.query.filter_by(urlname=urlname).first_or_404()
    page = force_int(request.args.get('page', 1), 0)
    if not page:
        return abort(404)
    paginator = Topic.query.filter_by(node_id=node.id).paginate(page)
    return render_template(
        'node/view.html', node=node, paginator=paginator
    )


@bp.route('/<urlname>/edit', methods=['GET', 'POST'])
@require_staff
def edit(urlname):
    """
    Edit a node by staff members.

    :param urlname: the urlname of the Node model
    """
    node = Node.query.filter_by(urlname=urlname).first_or_404()
    form = NodeForm(obj=node)
    if form.validate_on_submit():
        form.populate_obj(node)
        node.save()
        return redirect(url_for('.view', urlname=node.urlname))
    return render_template('node/edit.html', form=form, node=node)
