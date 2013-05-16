# coding: utf-8

from flask import Blueprint
from flask import render_template
from ..helpers import require_user
from ..models import Node, Topic, fill_topics


bp = Blueprint('front', __name__)


@bp.route('/')
def home():
    """The homepage of the site."""
    topics = Topic.query.order_by(Topic.id.desc()).limit(16)
    topics = fill_topics(topics)
    nodes = Node.query.order_by(Node.id.desc()).limit(10)
    return render_template('index.html', topics=topics, nodes=nodes)


@bp.route('/upload', methods=['POST'])
@require_user
def upload():
    """Upload images handler."""
    #TODO
    return ''
