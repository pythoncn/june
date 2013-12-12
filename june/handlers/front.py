# coding: utf-8

import os
import time
import datetime
from flask import Blueprint, request, g, current_app
from flask import render_template, Response, jsonify
from ..filters import markdown
from ..utils.user import require_user
from ..models import Node, Topic, fill_topics, cache


bp = Blueprint('front', __name__)


@bp.route('/')
def home():
    """The homepage of the site."""
    nodes = Node.query.order_by(Node.id.desc()).all()

    home_nodes = filter(lambda o: o.on_home, nodes)
    home_node_ids = map(lambda o: o.id, home_nodes)
    topics = Topic.query.filter(
        Topic.node_id.in_(home_node_ids)
    ).order_by(Topic.id.desc()).limit(16)
    topics = fill_topics(topics)

    # blog is a special node, get the latest posts from blog
    blog = Node.query.filter_by(urlname='blog').first()
    if blog:
        blogs = Topic.query.filter_by(
            node_id=blog.id).order_by(Topic.id.desc()).limit(2)
    else:
        blogs = None

    return render_template(
        'index.html', topics=topics, nodes=nodes[:16],
        blog=blog, blogs=blogs
    )


@bp.route('/feed')
def feed():
    html = cache.get('sitefeed')
    if not html:
        topics = Topic.query.order_by(Topic.id.desc()).limit(16)
        topics = fill_topics(topics)
        now = datetime.datetime.now()
        html = render_template('feed.xml', topics=topics, now=now)
        cache.set('sitefeed', html, 1800)

    return Response(html, content_type='text/xml; charset=utf-8')


@bp.route('/markdown', methods=['POST'])
def preview():
    content = request.form.get('content', '')
    return markdown(content)


@bp.route('/upload', methods=['POST'])
@require_user
def upload():
    """Upload images handler."""
    image = request.files.get('image')
    _, ext = os.path.splitext(image.filename)
    filename = '%d-%d%s' % (g.user.id, int(time.time()), ext.lower())
    try:
        url = current_app.storage.save(image, filename)
        return jsonify(url=url)
    except:
        return jsonify(error='upload failed')
