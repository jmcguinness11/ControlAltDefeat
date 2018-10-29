DROP TABLE Events;
DROP TABLE Plays;
DROP TABLE Players;

CREATE TABLE Players(
	name CHAR(50),
	position CHAR(5),
	playerTag CHAR(10) PRIMARY KEY,
	height INT DEFAULT NULL,
	weight INT DEFAULT NULL,
	active INT DEFAULT 1
);

CREATE TABLE Events(
	id INT PRIMARY KEY,
	game CHAR(100),
	playNum INT,
	quarter INT,
	series INT,
	seriesSeq INT,
	seriesEnd CHAR(20),
	active INT DEFAULT 1
);

CREATE TABLE Plays(
	id INT PRIMARY KEY AUTO_INCREMENT,
	event_id INT REFERENCES Events(id),
	pff_QB CHAR(10),
	pff_BALLCARRIER CHAR(10),
	pff_PASSRECTARGET CHAR(10),
	genFormation CHAR(20),
	genPlay CHAR(20),
	down INT,
	dist INT,
	rp CHAR(1),
	fieldPos INT,
	gain INT,
	explosive CHAR(1),
	result CHAR(20),
	winP CHAR(1),
	pff_YARDSAFTERCONTACT INT,
	pff_YARDSAFTERCATCH INT,
	pff_PASSRESULT CHAR(20),
	pff_PASSDEPTH INT,
	passingMap CHAR(1),
	protection CHAR(20),
	backfield CHAR(5),
	motion_shift CHAR(20),
	active INT DEFAULT 1,
	FOREIGN KEY (pff_QB) REFERENCES Players(playerTag), 
	FOREIGN KEY (pff_BALLCARRIER) REFERENCES Players(playerTag), 
	FOREIGN KEY (pff_PASSRECTARGET) REFERENCES Players(playerTag)
);
