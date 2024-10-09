CREATE TYPE post_type AS ENUM ('review', 'topic', 'reply');

CREATE TABLE Users (
    user_id TEXT PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL);


CREATE TABLE POSTS (
    post_id SERIAL PRIMARY KEY,
    game_id INT NULL,
    title TEXT,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rating INT NULL,
    content TEXT,
    post post_type,
    parent_id INT NULL,
    user_id TEXT REFERENCES Users(user_id)
);




