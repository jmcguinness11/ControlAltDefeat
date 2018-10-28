
DROP TABLE Players;
DROP TABLE Events;
DROP TABLE Plays;

CREATE TABLE Players(
	number INT PRIMARY KEY,
	name CHAR(50),
	position CHAR(50)
);

CREATE TABLE Events(
	id INT PRIMARY KEY,
	date DATE,
	opponent CHAR(50),
	isPractice BOOLEAN
);

CREATE TABLE Plays(
	id INT PRIMARY KEY,
	event_id INT REFERENCES Events(id),
	player1_number INT,
	player2_number INT,
	name CHAR(50),
	type CHAR(50),
	quarter INT,
	down INT,
	distance INT,
	isWin BOOLEAN,
	yards_after_contact INT,
	yards_after_catch INT,
	pass_result INT,
	pass_depth INT,
	protection INT, 
	passing_map INT,
	backfield INT
);
