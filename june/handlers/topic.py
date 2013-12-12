# coding: utf-8

import datetime
from flask import Blueprint, g, request, flash, current_app
from flask import render_template, redirect, abort, jsonify
from flask import url_for
from flask.ext.babel import gettext as _
from ..helpers import force_int, limit_request
from ..models import db, Node, Account
from ..models import Topic, Reply, LikeTopic
from ..models import fill_topics, fill_with_users
from ..forms import TopicForm, ReplyForm
from ..utils.user import require_user


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
    return render_template('topic/topics.html', paginator=paginator,
                           endpoint='topic.topics')


@bp.route('/latest')
def latest():
    """
    Topics ordered by created time.
    """
    page = force_int(request.args.get('page', 1), 0)
    if not page:
        return abort(404)
    paginator = Topic.query.order_by(Topic.id.desc()).paginate(page)
    paginator.items = fill_topics(paginator.items)
    return render_template('topic/topics.html', paginator=paginator,
                           endpoint='topic.latest')


@bp.route('/desert')
def desert():
    """
    Topics without any replies.
    """
    page = force_int(request.args.get('page', 1), 0)
    if not page:
        return abort(404)
    paginator = Topic.query.filter_by(
        reply_count=0).order_by(Topic.id.desc()).paginate(page)
    paginator.items = fill_topics(paginator.items)
    return render_template('topic/topics.html', paginator=paginator,
                           endpoint='topic.desert')


@bp.route('/create/<urlname>', methods=['GET', 'POST'])
@require_user
def create(urlname):
    """
    Create a topic in the node by an activated user.

    :param urlname: the urlname of the Node model
    """

    now = datetime.datetime.utcnow()
    delta = now - g.user.created
    verify = current_app.config.get('VERIFY_USER')
    if verify and not delta.days and not g.user.is_admin:
        # only allow user who has been registered after a day
        flash(_('New users can not create a topic'), 'warn')
        return redirect(url_for('.topics'))

    if g.user.active:
        # if user has no active information
        d = now - g.user.active
        delta = d.days * 86400 + d.seconds
    else:
        delta = 1000
    if delta < 300 and not g.user.is_staff:
        # you cannot create a topic
        left = int(300 - delta)
        flash(_("Don't be a spammer, take a rest for %(time)i seconds.",
                time=left), 'warn')
        return redirect(url_for('.topics'))

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
    if request.method == 'POST':
        # record hits
        topic = Topic.query.get_or_404(uid)
        topic.hits += 1
        topic.save()
        return jsonify(hits=topic.hits)

    page = force_int(request.args.get('page', 1), 0)
    if not page:
        return abort(404)

    topic = Topic.query.get_or_404(uid)
    node = Node.query.get_or_404(topic.node_id)
    author = Account.query.get_or_404(topic.account_id)
    topic.author = author
    topic.node = node

    if g.user:
        topic.like = LikeTopic.query.filter_by(
            account_id=g.user.id, topic_id=uid
        ).first()

    paginator = Reply.query.filter_by(topic_id=uid).paginate(page)
    paginator.items = fill_with_users(paginator.items)

    form = None
    if g.user:
        form = ReplyForm()

    return render_template(
        'topic/view.html', topic=topic,
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
    if g.user.id != topic.account_id and not g.user.is_staff:
        return abort(403)
    form = TopicForm(obj=topic)
    if form.validate_on_submit():
        form.populate_obj(topic)
        topic.save()
        return redirect(url_for('.view', uid=uid))
    return render_template('topic/edit.html', topic=topic, form=form)


@bp.route('/<int:uid>/delete', methods=['POST'])
@require_user
def delete(uid):
    """
    Delete a topic by the topic author.
    """
    #TODO: should we delete the replies of the topic?
    password = request.form.get('password')
    if not password:
        flash(_('Password is required to delete a topic'), 'info')
        return redirect(url_for('.view', uid=uid))
    if not g.user.check_password(password):
        flash(_('Password is wrong'), 'error')
        return redirect(url_for('.view', uid=uid))
    topic = Topic.query.get_or_404(uid)
    topic.delete()
    return redirect(url_for('.topics'))


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


@bp.route('/<int:uid>/like', methods=('POST',))
@require_user
def like(uid):
    """Like a topic."""
    like = LikeTopic.query.filter_by(
        account_id=g.user.id, topic_id=uid
    ).first()
    if like:
        db.session.delete(like)
        db.session.commit()
        return jsonify(status='ok', action='cancel')
    like = LikeTopic(account_id=g.user.id, topic_id=uid)
    db.session.add(like)
    db.session.commit()
    return jsonify(status='ok', action='like')
