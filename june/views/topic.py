# coding: utf-8

from flask import Blueprint, g, request, flash
from flask import render_template, redirect, url_for, abort
from ..helpers import require_user, force_int
from ..models import Node, Topic, fill_topics
from ..forms import TopicForm, ReplyForm


__all__ = ['bp']

bp = Blueprint('topic', __name__)


@bp.route('/')
def topics():
    """
    The topics list page.
    """
    page = force_int(request.args.get('page', 1), 0)
    if not page:
        return abort(404)
    paginator = Topic.query.order_by(Topic.id.desc()).paginate(page)
    paginator.items = fill_topics(paginator.items)
    return render_template('topic/topics.html', paginator=paginator)


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
        topic = form.save(g.user, node)
        return redirect(url_for('.view', uid=topic.id))
    return render_template('topic/create.html', node=node, form=form)


@bp.route('/<int:uid>', methods=['GET', 'POST'])
def view(uid):
    """
    View a topic with the given id.

    :param uid: the id of a topic.
    """
    topic = Topic.query.get_or_404(uid)

    form = None
    if g.user:
        form = ReplyForm()

    return render_template('topic/view.html', topic=topic, form=form)


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
    topic = Topic.query.get_or_404(uid)
    form = ReplyForm()
    if form.validate_on_submit():
        form.save(g.user, topic)
    else:
        flash(_('Missing content'), 'error')
    return redirect(url_for('.view', uid=uid))
