CREATE TYPE ReviewType AS (replyid INT, authorid INT, content TEXT, created TIMESTAMP, rating INT);
CREATE TYPE TopicType AS (topicid INT, authorid INT, title TEXT, content TEXT, created TIMESTAMP, rating INT);

CREATE TABLE Users (
    userid SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT NOT NULL);

CREATE TABLE Page (
    pageid SERIAL PRIMARY KEY,
    gameid INT NOT NULL,
    reviews ReviewType[],
    topics TopicType[]
);
