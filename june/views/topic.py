# coding: utf-8

from flask import Blueprint
from flask import render_template
from ..helpers import require_staff, require_user


__all__ = ['bp']

bp = Blueprint('topic', __name__)


@bp.route('/create/<urlname>', methods=['GET', 'POST'])
@require_user
def create(urlname):
    """
    Create a topic in the node by an activated user.

    :param urlname: the urlname of the Node model
    """
    pass


@bp.route('/<int:uid>')
def view(uid):
    """
    View a topic with the given id.

    :param uid: the id of a topic.
    """
    pass


@bp.route('/<int:uid>/edit', methods=['GET', 'POST', 'DELETE'])
@require_user
def edit(uid):
    """
    Edit a topic by the topic author.

    :param uid: the id of the topic
    """
    pass


@bp.route('/<int:uid>/reply', methods=['POST', 'DELETE'])
@require_user
def reply(uid):
    """
    Reply of the given topic.

    * POST: it will create a reply
    * DELETE: it will delete a reply

    Delete should pass an arg of the reply id, and it can be only deleted
    by the reply author or the staff members.

    :param uid: the id of the topic
    """
    pass
