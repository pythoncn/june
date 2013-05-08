# coding: utf-8

from flask import Blueprint
from flask import render_template
from ..models import Node, Topic, fill_topics


bp = Blueprint('front', __name__)


@bp.route('/')
def home():
    topics = Topic.query.order_by(Topic.id.desc()).limit(16)
    topics = fill_topics(topics)

    nodes = Node.query.order_by(Node.id.desc()).limit(10)
    return render_template('index.html', topics=topics, nodes=nodes)
