#script to load in data

import MySQLdb

#mysql connection
db = MySQLdb.connect(host="localhost", user="kkraus1", passwd="goirish1", db="kkraus1")
cur = db.cursor()

#open csv files (put them in home directory or one before ControlAltDefeat
playsfile = open("../playsEdit.csv", "r")
playersfile = open("../players.csv", "r")
eventsfile = open("../eventsEdit.csv", "r")

#get list of lists for data in each file
plays = [play.split(',') for play in playsfile.readlines()]
players = [player.split(',') for player in playersfile.readlines()]
events = [event.split(',') for event in eventsfile.readlines()]

#get rid of empty columns and replace with NULL
for i in range(0, len(plays)): 
	for j in range(0, len(plays[i])):
		if plays[i][j] == '':
			plays[i][j] = 'NULL'
for i in range(0, len(players)): 
	for j in range(0, len(players[i])):
		if players[i][j] == '':
			players[i][j] = 'NULL'
for i in range(0, len(events)): 
	for j in range(0, len(events[i])):
		if events[i][j] == '':
			events[i][j] = 'NULL'

#get rid of column headers
plays.pop(0)
players.pop(0)
events.pop(0)

#construct and execute insert statements
playerInsert = "INSERT INTO Players (name, position, playerTag) VALUES (\'"
for p in players:
	command = playerInsert + p[0] + "\', \'" + p[1] + "\', \'" + p[2] + "\')"
	cur.execute(command)
	row = cur.fetchall()
	if row != ():
		print row

eventsInsert = "INSERT INTO Events (id, game, playNum, quarter, series, seriesSeq, seriesEnd) VALUES ("
for e in events:
	seriesEnd = e[6] 
	if seriesEnd != 'NULL':
		seriesEnd = "\'" + seriesEnd + "\'"
	command = eventsInsert + e[0] + ", \'" + e[1] + "\', " + e[2] + ", " + e[3] + ", " + e[4] + ", " + e[5] + ", " + seriesEnd + ")"
	cur.execute(command)
	row = cur.fetchall()
	if row != ():
		print row

playsInsert = "INSERT INTO Plays (event_id, pff_QB, pff_BALLCARRIER, pff_PASSRECTARGET, genFormation, genPlay, down, dist, rp, fieldPos, gain, explosive, result, winP, pff_YARDSAFTERCONTACT, pff_YARDSAFTERCATCH, pff_PASSRESULT, pff_PASSDEPTH, passingMap, protection, backfield, motion_shift) VALUES ("
for i in range(0, len(plays)):
	#handle strings by adding quotes for insertion
	for a in [1, 2, 3, 4, 5, 8, 11, 12, 13, 16, 18, 19, 20, 21]:
		if plays[i][a] != 'NULL':
			plays[i][a] = "\'" + plays[i][a] + "\'"

	command = playsInsert + plays[i][0]
	for j in range(1, len(plays[i])-1):
		command = command + ", " + plays[i][j]
	command = command + ")"
	
	cur.execute(command)
	row = cur.fetchall()
	if row != ():
		print row

#close files and db connection
playsfile.close()
playersfile.close()
eventsfile.close()
db.commit()
db.close()
