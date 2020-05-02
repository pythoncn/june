# coding: utf-8

from flask import Blueprint, g, request
from flask import render_template, abort
from ..helpers import force_int
from ..models import Notify
from ..models import fill_with_topics, fill_with_users
from ..utils.user import require_login


__all__ = ['bp']

bp = Blueprint('notify', __name__)


@bp.route('/')
@require_login
def notifies():
    """
    The topics list page.
    """
    page = force_int(request.args.get('page', 1), 0)
    if not page:
        return abort(404)
    paginator = Notify.query.filter_by(
        account_id=g.user.id, is_viewed=0).order_by(
        Notify.created.desc()).paginate(page)
    paginator.items = fill_with_users(paginator.items)
    paginator.items = fill_with_topics(paginator.items)
    return render_template('notify/notify.html', paginator=paginator)
