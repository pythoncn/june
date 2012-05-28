#!/usr/bin/python

from july.util import parse_config_file
parse_config_file('tmp.config')

from july.database import db
from june.topic.models import Topic, Vote


#: topic changes


def pre_update_topic_table():
    db.session.execute('alter table topic add column up_count integer')
    db.session.execute('alter table topic add column down_count integer')
    db.session.commit()


def post_update_topic_table():
    db.session.execute('alter table topic delete column ups')
    db.session.execute('alter table topic delete column downs')
    db.session.commit()


def update_topic():
    for topic in Topic.query.all():
        print("update topic: %s" % topic.title)
        if topic.ups:
            user_ids = topic.ups.split(',')
            topic.up_count = len(user_ids)
            for id in user_ids:
                vote = Vote.query.get_first(user_id=id, topic_id=topic.id)
                if not vote:
                    vote = Vote(user_id=id, topic_id=topic.id)
                vote.type = 'up'
                db.session.add(vote)
        else:
            topic.up_count = 0

        if topic.downs:
            user_ids = topic.downs.split(',')
            topic.down_count = len(user_ids)
            for id in user_ids:
                vote = Vote.query.get_first(user_id=id, topic_id=topic.id)
                if not vote:
                    vote = Vote(user_id=id, topic_id=topic.id)
                vote.type = 'down'
                db.session.add(vote)
        else:
            topic.down_count = 0

    db.session.commit()


#update_topic()


#: member changes

def pre_update_member_table():
    db.session.execute('alter table member add column edit_username_count integer')
    db.session.execute('alter table member add column city varchar(200)')
    db.session.execute('alter table member add column description text')
    db.session.commit()


def post_update_member_table():
    db.session.execute('update member set edit_username_count = 2')
    db.session.commit()

post_update_member_table()
