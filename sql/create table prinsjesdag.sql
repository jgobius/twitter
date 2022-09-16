CREATE TABLE tweets (
	id BIGINT,
	created_at DATETIME,
	possibly_sensitive BIT,
	text VARCHAR(280),
	hashtags VARCHAR(280),
	user_id BIGINT,
	user_name VARCHAR(256),
	screen_name VARCHAR(256),
	verified BIT)

CREATE TABLE logs (
	id INT,
	log_type VARCHAR(20),
	log_message VARCHAR(MAX),
	created_at DATETIME,
	PRIMARY KEY (id),
)

CREATE TABLE sentiment(
	id INT,
    sentiment VARCHAR(256),
    positive FLOAT,
    neutral FLOAT,
    negative FLOAT,
    tweet_id BIGINT,
    PRIMARY KEY (id),
    FOREIGN KEY (tweet_id) REFERENCES tweets(id)
)