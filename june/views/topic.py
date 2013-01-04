# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import render_template
from june.node.models import Node


app = Blueprint('topic', __name__, template_folder='templates')


@app.route('/-create/<slug>')
def create(slug):
    node = Node.query.filter_by(slug=slug).first_or_404()
    return render_template("create_topic.html", node=node)


@app.route('/<int:id>/-edit', methods=['GET', 'POST'])
def edit(id):
    pass
