# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import render_template
from flask import request
from flask import g
from june.node.models import Node
from .models import Topic

app = Blueprint('topic', __name__, template_folder='templates')


@app.route('/-create/<slug>')
def create(slug):
    node = Node.query.filter_by(slug=slug).first_or_404()
    return render_template("create_topic.html")


@app.route('/<int:id>/-edit', methods=['GET', 'POST'])
def edit(id):
    pass
