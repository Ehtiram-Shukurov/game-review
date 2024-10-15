CREATE TYPE post_type AS ENUM ('review', 'topic', 'reply');

CREATE TABLE Users (
    user_id PRIMARY SERIAL KEY,
    user_sub TEXT NOT NULL,
    username TEXT NOT NULL,
    email TEXT NOT NULL);


CREATE TABLE POSTS (
    post_id SERIAL PRIMARY KEY,
    game_id INT NULL references Games(game_id),
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
    7,
    '2');

INSERT INTO POSTS (
    game_id, content, post, parent_id, user_id) 
    VALUES (1, 
    'I disagree', 
    'reply', 
    12,
    '2');

CREATE TABLE GAMES (
    game_id INT PRIMARY KEY,
    image_url varchar(512),
    summary text,
    name varchar(256)
)



-- retrive replies tree recursively
WITH RECURSIVE replies AS (
    SELECT post_id, parent_id, content, user_id
    FROM POSTS
    WHERE parent_id = 7
    UNION ALL
    SELECT p.post_id, p.parent_id, p.content, p.user_id
    FROM POSTS p
    JOIN replies r ON p.parent_id = r.post_id)

    SELECT replies.*, username FROM replies INNER JOIN USERS ON replies.user_id = USERS.user_id ORDER BY post_id;


-- delete review and all replies
WITH RECURSIVE posts_to_delete AS (
    SELECT post_id
    FROM posts
    WHERE post_id = 10

    UNION ALL

    SELECT p.post_id
    FROM posts p
    INNER JOIN posts_to_delete pt ON p.parent_id = pt.post_id
)

DELETE FROM posts
WHERE post_id IN (SELECT post_id FROM posts_to_delete);