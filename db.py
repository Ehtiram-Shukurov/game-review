# Code is adapted and modified from the following source:
# https://canvas.umn.edu/courses/460699/pages/session-07-postgresql?module_item_id=13115326

from contextlib import contextmanager
from flask import current_app, g
import os
import datetime
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import DictCursor

pool = None


def setup():
    global pool
    DATABASE_URL = os.environ['DATABASE_URL']
    pool = ThreadedConnectionPool(1, 100, dsn=DATABASE_URL, sslmode='require')


@contextmanager
def get_db_connection():
    try:
        connection = pool.getconn()
        yield connection
    finally:
        pool.putconn(connection)


@contextmanager
def get_db_cursor(commit=False):
    with get_db_connection() as connection:
        cursor = connection.cursor(cursor_factory=DictCursor)
        # cursor = connection.cursor()
        try:
            yield cursor
            if commit:
                connection.commit()
        finally:
            current_app.logger.info(f"closing db cursor")
            cursor.close()


def insert_user(user_data):
    query = "INSERT INTO users (userid, username, email) VALUES (%s, %s)"
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (user_data['sub'], user_data['username'], user_data['email']))


def insert_review(review_data):
    game_id = review_data['game_id']
    query = "INSERT INTO POSTS (game_id, title, rating, content, post, user_id) VALUES (%s, %s, %s, %s, %s, %s)"
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (
        game_id, review_data['title'], review_data['rating'], review_data['content'], 'review', review_data['user_id']))


def insert_topic(topic_data):
    game_id = topic_data['game_id']
    query = "INSERT INTO POSTS (game_id, title, rating, content, post, user_id) VALUES (%s, %s, %s, %s, %s, %s)"
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (
        game_id, topic_data['title'], topic_data['rating'], topic_data['content'], 'topic', topic_data['user_id']))


def insert_reply(reply_data):
    query = "INSERT INTO POSTS (title, rating, content, post, parent_id, user_id) VALUES (%s, %s, %s, %s, %s, %s)"
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (
        reply_data['title'], reply_data['rating'], reply_data['content'], 'topic', reply_data['parent_id'],
        reply_data['user_id']))


def retrieve_user(user_id):
    query = "SELECT * FROM users where user_id = %s"
    with get_db_cursor() as cursor:
        cursor.execute(query, (user_id,))
        return cursor.fetchone()


def retrieve_user_by_name(username):
    query = "SELECT * FROM users WHERE username = %s"
    with get_db_cursor() as cursor:
        cursor.execute(query, (username,))
        return cursor.fetchone()


def retrieve_topics_by_game_id(game_id):
    query = "SELECT * FROM POSTS WHERE game_id = %s AND post = 'topic'"
    with get_db_cursor() as cursor:
        cursor.execute(query, (game_id,))
        return cursor.fetchall()


def retrieve_reviews_by_game_id(game_id):
    query = "SELECT * FROM POSTS WHERE game_id = %s AND post = 'review'"
    with get_db_cursor() as cursor:
        cursor.execute(query, (game_id,))
        return cursor.fetchall()
    
def retrieve_review_by_post_id(post_id):
    query = "SELECT *, username FROM POSTS JOIN USERS ON POSTS.user_id = USERS.user_id WHERE post_id = %s"
    with get_db_cursor() as cursor:
        cursor.execute(query, (post_id,))
        return cursor.fetchone()

def retrive_replies_by_post_id(review_id):
    query = """WITH RECURSIVE replies AS (
    SELECT post_id, parent_id, content, user_id
    FROM POSTS
    WHERE parent_id = %s
    UNION ALL
    SELECT p.post_id, p.parent_id, p.content, p.user_id
    FROM POSTS p
    JOIN replies r ON p.parent_id = r.post_id)

    SELECT replies.*, username FROM replies INNER JOIN USERS ON replies.user_id = USERS.user_id ORDER BY post_id"""

    with get_db_cursor() as cursor:
        cursor.execute(query, (review_id,))
        return cursor.fetchall()


def retrieve_replies_by_post_id(post_id):
    query = "SELECT * FROM POSTS WHERE parent_id = %s"
    with get_db_cursor() as cursor:
        cursor.execute(query, (post_id,))
        return cursor.fetchall()

#TODO: get all subreplies
