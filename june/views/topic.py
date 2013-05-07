# coding: utf-8

from flask import Blueprint, g
from flask import render_template, redirect, url_for
from ..helpers import require_user
from ..models import Node, Topic
from ..forms import TopicForm


__all__ = ['bp']

bp = Blueprint('topic', __name__)


@bp.route('/create/<urlname>', methods=['GET', 'POST'])
@require_user
def create(urlname):
    """
    Create a topic in the node by an activated user.

    :param urlname: the urlname of the Node model
    """
    node = Node.query.filter_by(urlname=urlname).first_or_404()
    form = TopicForm()
    if form.validate_on_submit():
        topic = form.save(g.user)
        return redirect(url_for('.view', uid=topic.id))
    return render_template('topic/create.html', node=node, form=form)


@bp.route('/<int:uid>')
def view(uid):
    """
    View a topic with the given id.

    :param uid: the id of a topic.
    """
    topic = Topic.query.get_or_404(uid)
    return render_template('topic/view.html', topic=topic)


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
