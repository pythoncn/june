# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import render_template
from flask import request, redirect, url_for
from flask import flash
from flask import g
from .models import Topic, Reply, Vote, TopicLog

app = Blueprint('topic', __name__, template_folder='templates')


@app.route('/-create', methods=['GET'])
def create():
    nodes = Node.query.all()
    return render_template("create_topic.html", nodes=nodes)


@app.route('/<int:id>/-edit', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'POST':
        topic = Topic.query.get_or_404(id)

    if request.method == 'GET':
        pass
