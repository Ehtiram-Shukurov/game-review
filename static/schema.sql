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

-- Data 
INSERT INTO Users (user_id, username, email) 
    VALUES ('1', 'user1', 'test@email.com');

INSERT INTO Users (user_id, username, email) 
    VALUES ('2', 'user2', 'test2@gmail.com');

INSERT INTO POSTS (
    game_id, title, rating, content, post, user_id) 
    VALUES (1, 
    'Review of game', 
    5, 
    'This game is great', 
    'review', 
    '1');

INSERT INTO POSTS (
    game_id, content, post, parent_id, user_id) 
    VALUES (1, 
    'Yes', 
    'reply', 
    1,
    '2');

INSERT INTO POSTS (
    game_id, content, post, parent_id, user_id)
    VALUES (1, 'I agree', 'reply', 3, '1');

INSERT INTO POSTS (
    game_id, content, post, parent_id, user_id) 
    VALUES (1, 
    'NO', 
    'reply', 
    1,
    '2');

INSERT INTO POSTS (
    game_id, content, post, parent_id, user_id) 
    VALUES (1, 
    'I disagree', 
    'reply', 
    5,
    '2');



-- retrive replies tree recursively
WITH RECURSIVE replies AS (
    SELECT post_id, parent_id, content, user_id
    FROM POSTS
    WHERE parent_id = 2
    UNION ALL
    SELECT p.post_id, p.parent_id, p.content, p.user_id
    FROM POSTS p
    JOIN replies r ON p.parent_id = r.post_id)

    SELECT replies.*, username FROM replies INNER JOIN USERS ON replies.user_id = USERS.user_id ORDER BY post_id;