# coding: utf-8

from flask import Blueprint
from flask import render_template
from ..models import Topic, fill_topics


bp = Blueprint('front', __name__)


@bp.route('/')
def home():
    topics = Topic.query.order_by(Topic.id.desc()).limit(16)
    topics = fill_topics(topics)
    return render_template('index.html', topics=topics)
