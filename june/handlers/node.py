# coding: utf-8

from flask import Blueprint, request, g
from flask import render_template, redirect, url_for, abort
from ..models import Node, NodeStatus, Topic, fill_topics
from ..forms import NodeForm
from ..helpers import force_int
from ..utils.user import require_staff


__all__ = ['bp']

bp = Blueprint('node', __name__)


@bp.route('/')
def nodes():
    """Nodes pages."""
    nodes = Node.query.order_by(Node.updated.desc()).all()
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
    paginator = Topic.query.filter_by(
        node_id=node.id).order_by(Topic.id.desc()).paginate(page)
    paginator.items = fill_topics(paginator.items)

    status = None
    if g.user:
        status = NodeStatus.query.filter_by(
            account_id=g.user.id, node_id=node.id
        ).first()
    return render_template(
        'node/view.html', node=node, paginator=paginator, status=status
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
