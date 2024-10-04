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
    current_app.logger.info(f"creating db connection pool")
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

def insert_user(userdata):
    query = "INSERT INTO users (username, email) VALUES (%s, %s)"
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (userdata['username'], userdata['email']))

def insert_reviews(reviewdata):
    game_id = reviewdata['game_id']
    query = "UPDATE page SET reviews = ARRAY_APPEND(reviews, %s) WHERE game_id = (%s)"
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (reviewdata, game_id))
    
def insert_topic(topicdata):
    game_id = topicdata['game_id']
    query = "UPDATE page SET topics = ARRAY_APPEND(topics, %s) WHERE game_id = (%s)"
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (topicdata, game_id))

def retrieve_user(reversed=False):
    query = "SELECT * FROM users"
    with get_db_cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()

def retrieve_user_byname(username):
    query = "SELECT * FROM users WHERE username = %s"
    with get_db_cursor() as cursor:
        cursor.execute(query, (username,))
        return cursor.fetchone()

def retrive_page():
    query = "SELECT * FROM page"
    with get_db_cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()
    
def retrive_topics_bygameid(game_id):
    query = "SELECT topics FROM page WHERE game_id = %s"
    with get_db_cursor() as cursor:
        cursor.execute(query, (game_id,))
        return cursor.fetchone()
    
def retrive_review_bygameid(game_id):
    query = "SELECT reviews FROM page WHERE game_id = %s"
    with get_db_cursor() as cursor:
        cursor.execute(query, (game_id,))
        return cursor.fetchone()