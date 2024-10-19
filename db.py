# Code is adapted and modified from the following source:
# https://canvas.umn.edu/courses/460699/pages/session-07-postgresql?module_item_id=13115326

from contextlib import contextmanager
from flask import current_app, g
import os
import datetime
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import RealDictCursor

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
        cursor = connection.cursor(cursor_factory=RealDictCursor)
        # cursor = connection.cursor()
        try:
            yield cursor
            if commit:
                connection.commit()
        finally:
            cursor.close()


def insert_user(user_data):
    query = "INSERT INTO users (user_sub, username, email,descript) VALUES (%s, %s, %s,%s)"
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (user_data['user_sub'], user_data['username'], user_data['email'],user_data['descript']))

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


def retrieve_user(user_sub):
    query = "SELECT * FROM users where user_sub = %s"
    with get_db_cursor() as cursor:
        cursor.execute(query, (user_sub,))
        return cursor.fetchone()

def retrieve_user_by_name(username):
    query = "SELECT * FROM users WHERE username = %s"
    with get_db_cursor() as cursor:
        cursor.execute(query, (username,))
        return cursor.fetchone()

def retrieve_user_id_by_sub(sub):
    query = "SELECT user_id FROM users WHERE user_sub = %s"
    with get_db_cursor() as cursor:
        cursor.execute(query, (sub,))
        return cursor.fetchone()

def retrieve_topics_by_game_id(game_id):
    query = "SELECT * FROM POSTS WHERE game_id = %s AND post = 'topic'"
    with get_db_cursor() as cursor:
        cursor.execute(query, (game_id,))
        return cursor.fetchall()


def retrieve_reviews_by_game_id(game_id):
    query = "SELECT *, username FROM POSTS JOIN USERS ON POSTS.user_id = USERS.user_id WHERE post = 'review' AND game_id = %s"
    with get_db_cursor() as cursor:
        cursor.execute(query, (game_id,))
        return cursor.fetchall()


def retrieve_review_by_post_id(post_id):
    query = "SELECT POSTS.*, username, user_sub FROM POSTS JOIN USERS ON POSTS.user_id = USERS.user_id WHERE post_id = %s"
    with get_db_cursor() as cursor:
        cursor.execute(query, (post_id,))
        return cursor.fetchone()


def retrieve_replies_by_post_id(review_id):
    query = """WITH RECURSIVE replies AS (
    SELECT post_id, parent_id, content, user_id
    FROM POSTS
    WHERE parent_id = %s
    UNION ALL
    SELECT p.post_id, p.parent_id, p.content, p.user_id
    FROM POSTS p
    JOIN replies r ON p.parent_id = r.post_id)
    SELECT replies.*, username, user_sub FROM replies INNER JOIN USERS ON replies.user_id = USERS.user_id ORDER BY post_id"""

    with get_db_cursor() as cursor:
        cursor.execute(query, (review_id,))
        return cursor.fetchall()



## This will delete the content of the post and all of its replies
def delete_content(post_id):
    query = """WITH RECURSIVE posts_to_delete AS (
    SELECT post_id
    FROM posts
    WHERE post_id = %s

    UNION ALL

    SELECT p.post_id
    FROM posts p
    INNER JOIN posts_to_delete pt ON p.parent_id = pt.post_id
    )
    DELETE FROM posts
    WHERE post_id IN (SELECT post_id FROM posts_to_delete);"""

    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (post_id,))


def update_reviews(review_data):
    query = "UPDATE POSTS SET title = %s, rating = %s, content = %s WHERE post_id = %s"
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (review_data['title'], review_data['rating'], review_data['content'], review_data['post_id']))


def update_reply_content(reply_data):
    query = "UPDATE POSTS SET content = %s WHERE post_id = %s"
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (reply_data['content'], reply_data['post_id']))


def insert_post(title, game_id, content, post_type, rating, user_id, parent_id):
    query = "INSERT INTO POSTS (game_id, title, rating, content, post, parent_id, user_id) VALUES (%s,%s,%s,%s,%s,%s,%s)"
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (game_id, title, rating, content, post_type, parent_id, user_id))


def get_user_most_recent_post(user_id):
    query = "SELECT post_id FROM POSTS WHERE user_id = %s ORDER BY created DESC;"
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (user_id,))
        return cursor.fetchone()


def get_post_by_id(id):
    query = "SELECT * FROM POSTS WHERE post_id = %s"

    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (id,))
        post = cursor.fetchone()

    return post

def update_post_db(title, content, rating, post_id):
    query = "UPDATE POSTS SET title = %s, content = %s, rating = %s WHERE post_id = %s"
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (title, content, rating, post_id))

def get_user_by_sub(sub):
    query = "SELECT * FROM Users where user_sub = (%s)"
    with get_db_cursor() as cursor:
        cursor.execute(query, (sub,))
        return cursor.fetchone()
        
def retrieve_all_post(type,search):
    fuzzy = f"%{search}%"
    query = "SELECT * FROM POSTS WHERE post = %s AND (title ILIKE %s OR content ILIKE %s)"
    # TODO: bug where some parent post/review do not have a template.
    with get_db_cursor() as cursor:
        cursor.execute(query, (type,fuzzy,fuzzy))
        data = cursor.fetchall()
        res = {}
        for d in data:
            parent = d["parent_id"]
            # checks for none i.e. parent post
            if parent == None:
                res[d["post_id"]] =d["title"]
        return res



def get_game_by_id_database(game_id):
    query = "SELECT * FROM Games where game_id = (%s)"
    with get_db_cursor() as cursor:
        cursor.execute(query, (game_id,))
        return cursor.fetchone()


def save_game_data(game_data):
    query = "INSERT INTO GAMES (game_id, image_url, summary, name) VALUES (%s, %s, %s, %s);"
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (game_data.get('id'), game_data.get('cover').get('url'), game_data.get('summary'), game_data.get('name')))

def retrieve_all_users():
    query = "SELECT * FROM Users"
    with get_db_cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()
    
    
def update_user_profile(user_sub, username, email, descript):
    query = """
        UPDATE users
        SET username = %s, email = %s, descript = %s
        WHERE user_sub = %s
    """
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (username, email, descript, user_sub))
