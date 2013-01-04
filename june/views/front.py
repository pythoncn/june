# coding: utf-8

from flask import Blueprint


bp = Blueprint('front', __name__)


@bp.route('/')
def home():
    return 'hello'
