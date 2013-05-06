# coding: utf-8

from flask import Blueprint
from flask import render_template
from ..models import Node
from ..helpers import require_staff, require_user


__all__ = ['bp']

bp = Blueprint('node', __name__)


@bp.route('/create', methods=['GET', 'POST'])
@require_staff
def create():
    """
    Create a node by staff members.
    """
    pass


@bp.route('/<urlname>')
def urlname(urlname):
    """
    The view page of the Node.

    The node page should contain the information of the node, and topics
    in this node.

    :param urlname: the urlname of the Node model
    """

    node = Node.query.filter_by(urlname=urlname).first_or_404()
    # TODO
    return render_template('node/urlname.html', node=node)


@bp.route('/<urlname>/edit')
@require_staff
def edit(urlname):
    """
    Edit a node by staff members.

    :param urlname: the urlname of the Node model
    """
    pass


@bp.route('/<urlname>/newtopic')
@require_user
def newtopic(urlname):
    """
    Create a topic in the node by an activated user.

    :param urlname: the urlname of the Node model
    """
    pass
