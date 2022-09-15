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