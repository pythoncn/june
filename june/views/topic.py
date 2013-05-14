# coding: utf-8

from flask import Blueprint, g, request, flash
from flask import render_template, redirect, abort, jsonify
from flask import url_for
from flask.ext.babel import gettext as _
from ..helpers import require_user, force_int, limit_request
from ..models import Node, Topic, Reply, Account
from ..models import fill_topics, fill_with_users
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
    paginator = Topic.query.order_by(Topic.updated.desc()).paginate(page)
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

    if node.role == 'staff' and not g.user.is_staff:
        flash(_('You have no permission in this node.'), 'warn')
        return redirect(url_for('node.view', urlname=urlname))

    if node.role == 'admin' and not g.user.is_admin:
        flash(_('You have no permission in this node.'), 'warn')
        return redirect(url_for('node.view', urlname=urlname))

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
    page = force_int(request.args.get('page', 1), 0)
    if not page:
        return abort(404)

    topic = Topic.query.get_or_404(uid)
    node = Node.query.get_or_404(topic.node_id)
    author = Account.query.get_or_404(topic.account_id)

    paginator = Reply.query.filter_by(topic_id=uid).paginate(page)
    paginator.items = fill_with_users(paginator.items)

    form = None
    if g.user:
        form = ReplyForm()

    return render_template(
        'topic/view.html', topic=topic, node=node, author=author,
        form=form, paginator=paginator
    )


@bp.route('/<int:uid>/edit', methods=['GET', 'POST'])
@require_user
def edit(uid):
    """
    Edit a topic by the topic author.

    :param uid: the id of the topic
    """
    topic = Topic.query.get_or_404(uid)
    form = TopicForm(obj=topic)
    if form.validate_on_submit():
        form.populate_obj(topic)
        topic.save()
        return redirect(url_for('.view', uid=uid))
    return render_template('topic/edit.html', topic=topic, form=form)


@bp.route('/<int:uid>/move', methods=['GET', 'POST'])
@require_user
def move(uid):
    """
    Move a topic to another node.

    :param uid: the id of the topic
    """
    topic = Topic.query.get_or_404(uid)
    if g.user.id != topic.account_id and not g.user.is_staff:
        return abort(403)

    if request.method == 'GET':
        return render_template('topic/move.html', topic=topic)

    urlname = request.form.get('node', None)
    if not urlname:
        return redirect(url_for('.view', uid=uid))
    node = Node.query.filter_by(urlname=urlname).first()
    if node:
        topic.move(node)
        flash(_('Move topic success.'), 'success')
    else:
        flash(_('Node not found.'), 'error')
    return redirect(url_for('.view', uid=uid))


@bp.route('/<int:uid>/reply', methods=['POST', 'DELETE'])
@limit_request(5, redirect_url=lambda uid: url_for('.view', uid=uid))
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
    if request.method == 'DELETE':
        reply_id = force_int(request.args.get('reply', 0), 0)
        if not reply_id:
            return abort(404)
        reply = Reply.query.get_or_404(reply_id)
        if not reply:
            return abort(404)
        if reply.topic_id != uid:
            return abort(404)
        if g.user.is_staff or g.user.id == reply.account_id:
            reply.delete()
            return jsonify(status='success')
        return abort(403)

    topic = Topic.query.get_or_404(uid)
    form = ReplyForm()
    if form.validate_on_submit():
        form.save(g.user, topic)
    else:
        flash(_('Missing content'), 'error')
    return redirect(url_for('.view', uid=uid))
