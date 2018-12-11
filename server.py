from flask import *
import sys
import json
import MySQLdb
import atexit
import itertools
import collections
import csv

from queries import *

#global variables for column names
PLAYER_COLS = ['name', 'position', 'playerTag', 'height', 'weight', 'active']
PLAYERS_GET_QUERY = "SELECT * FROM Players WHERE active=1;"
DRIVE_COLS = ['Down', 'Dist', 'Run/Pass', 'FieldPos', 'Gain', 'Result', 'Explosive']
EVENTS_COLS = ['id', 'game']
SERIES_COLS = ['series']

#register exit function
def exitFunc(db):
    db.commit()
    db.close()


#set up mysql connection
db = MySQLdb.connect(host="localhost", user="kkraus1", passwd="goirish1", db="kkraus1")
cur = db.cursor()

#function for returning query as dictionary
def queryFormatted(colNames, query):
    cur.execute(query)
    result = cur.fetchall()
    res_list = []
    for row in result:
        row_dict = {}
        for k, col in enumerate(row):
	    if col:
                col = str(col)
                row_dict[colNames[k]] = col.decode('ascii', 'ignore').encode('ascii')
        res_list.append(row_dict)
    return res_list

# function to create inventory for each down and distance, by just changing conditionals in query
def inventories(regex):
	FIRST_QUERY = DOWNS_QUERY.format(regex)
	firstResp = queryFormatted(['List', 'Count', 'Percent'], FIRST_QUERY)
		
	TOTALS_Q = TOTALS_QUERY.format(regex)
	tResp = queryFormatted(['t'], TOTALS_Q) 
	total = tResp[0]['t']
	
	names = [] # list of all formations
	for formation in firstResp: 
		name = formation['List']
		names.append(name)

	# loop through names and get run and pass tables for each formation in 1st down
	data = {}
	RUNS = {}
	PASSES = {}
	for name in names: 
	# format with play name, r/p, down and distance
		nameNew = "\'" + name + "\'"
		runs = GEN_FORMATION.format(nameNew, '\'r\'', regex)
		passes = GEN_FORMATION.format(nameNew, '\'p\'', regex)
			
		run_q = queryFormatted(['List', 'Count', 'Num'], runs)
		pass_q = queryFormatted(['List', 'Count', 'Num'], passes)

		RUNS[name] = run_q
		PASSES[name] = pass_q

		data[name] = [{'List': 'Run', 'Count': '', 'Num': ''}] + run_q + [{'List': 'Pass', 'Count': '', 'Num': ''}] + pass_q

	return [firstResp, RUNS, PASSES, total]

def totalRPNDownload(INPUT):
    for item in INPUT:
        for dictionary in item:
            if dictionary['RP'] == 'R':
                if 'PlayCount' in dictionary:
                    runCount = dictionary['PlayCount']
                    runPercent = dictionary['PlayPercent']
                    totalPlays = dictionary['PlayTotal']
                if 'WinCount' in dictionary:
		    runWin = dictionary['WinCount']
		    runWinPercent = dictionary['WinPercent']
            elif dictionary['RP'] == 'P':
	        if 'PlayCount' in dictionary:
		    passCount = dictionary['PlayCount']
		    passPercent = dictionary['PlayPercent']
                    totalPlays = dictionary['PlayTotal']
                if 'WinCount' in dictionary:
		    passWin = dictionary['WinCount']
		    passWinPercent = dictionary['WinPercent']
            elif dictionary['RP'] == 'N':
		nCount = dictionary['PlayCount']
		nPercent = dictionary['PlayPercent']

    runString = runCount+' of '+totalPlays
    runWinString = runWin+' of '+runCount
    passString = passCount+' of '+totalPlays
    passWinString = passWin+' of '+passCount
    nString = nCount+' of'+totalPlays
    data = [[' ', 'R/P', 'Count', 'Percent', 'W/L', 'Percent'], ['1', 'R', runString, runPercent, runWinString, runWinPercent], ['2', 'P', passString, passPercent, passWinString, passWinPercent], ['3', 'N', nString, nPercent, ' ', ' ']]
    with open('TotalRPNdl.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)
    csvfile.close() 

def sitRPNDownload(INPUT):
    runCount = '0'
    runPercent = '0'
    passCount = '0'
    passPercent = '0'
    runWin = '0'
    passWin = '0'
    runWinPercent = '0'
    passWinPercent = '0'
    for item in INPUT:
	for dictionary in item:
	    if dictionary['RP'] == 'R':
		if 'PlayCount' in dictionary:
		    runCount = dictionary['PlayCount']
		    runPercent = dictionary['PlayPercent']
		    totalPlays = dictionary['PlayTotal']
		if 'WinCount' in dictionary:
		    runWin = dictionary['WinCount']
		    runWinPercent = dictionary['WinPercent']
	    elif dictionary['RP'] == 'P':
		if 'PlayCount' in dictionary:
		    passCount = dictionary['PlayCount']
		    passPercent = dictionary['PlayPercent']
		    totalPlays = dictionary['PlayTotal']
		if 'WinCount' in dictionary:
		    passWin = dictionary['WinCount']
		    passWinPercent = dictionary['WinPercent']
    runString = runCount+' of '+totalPlays
    runWinString = runWin+' of '+runCount
    passString = passCount+' of '+totalPlays
    passWinString = passWin+' of '+passCount
    returnedList = [[' ', 'Count', 'Percent', 'W/L', 'Percent'], ['R', runString, runPercent, runWinString, runWinPercent], ['P', passString, passPercent, passWinString, passWinPercent]]
    return returnedList

def motionsDownload(INPUT):
    bigList = []
    for item in INPUT:
	motion = item[0]
	count = 0
	for thing in item[1]:
	    if count == 0:
		totalPlays = thing['TOTAL']
		runPlays = thing['RUN']
		passPlays = thing['PASS']
		count += 1
	    else:
		runPercent = thing['RUN']
		passPercent = thing['PASS']
	count = 0
	resultingList = [[motion,' ',' ',' ',' ',' '],[' ','RUN',' ','PASS',' ','TOTAL'],[' ',runPlays,' ',passPlays,' ',totalPlays],[' ',runPercent,' 'passPercent,' ',' '],[' ',' ',' ',' ',' ',' ']]
	bigList += resultingList   
    with open('motions_dl.csv','w') as csvfile:
	writer = csv.writer(csvfile)
	writer.writerows(bigList)
    csvfile.close()


def backfieldDownload(INPUT):
    bigList = []
    for item in INPUT:
        backfield = item[0]
        count = 0
        for thing in item[1]:
	    if count == 0:
		totalPlays = thing['TOTAL']
		runPlays = thing['RUN']
		passPlays = thing['PASS']
		count += 1
	    else:
		runPercent = thing['RUN']
		passPercent = thing['PASS']
	count = 0
	resultingList = [[backfield,' ',' ',' ',' ',' '],[' ','RUN',' ','PASS',' ','TOTAL'],[' ',runPlays,' ',passPlays,' ',totalPlays],[' ',runPercent,' ',passPercent,' ',' '],[' ',' ',' ',' ',' ',' ']]
	bigList += resultingList
    with open('backfield_dl.csv','w') as csvfile:
	writer = csv.writer(csvfile)
	writer.writerows(bigList)
    csvfile.close()

def inventoryDownload(INPUT):
    GENFORMS = INPUT[0]
    RUNS = INPUT[1]
    PASSES = INPUT[2]
    TOTAL = INPUT[3]
    bigList = []
    extraList = []
    tempList = []
    count = 1
    for item in GENFORMS:
	genform = item['List']
	genformCount = item['Count']
	genformPercent = item['Percent']
	genformString = genformCount+' of '+TOTAL
	extraList = RUNS.get(genform)
	resultingList = [[count, genform,' ',' ',genformString,genformPercent]]
	count += 1
	bigList += resultingList
	totalPlays = 0
	newInt = 0
	for thing in extraList:
	    newInt = int(thing['Count'])
	    totalPlays += newInt
	stringTotalPlays = str(totalPlays)
	tempString = stringTotalPlays+' of '+genformCount
	genformCountInt = int(genformCount)
	tempList = [[' ',' ','R',' ',tempString,totalPlays/genformCountInt]]
	bigList += tempList
	newCount = 1
	for dictionary in extraList:
	    genplay = dictionary['List']
	    genplayCount = dictionary['Count']
	    genplayTotal = dictionary['Num']
	    genplayString = genplayCount+' of '+stringTotalPlays
	    tempList = [[' ',' ',newCount,genplay,genplayString,' ']]
	    bigList += tempList
	    newCount += 1
	extraList = PASSES.get(genform)
	totalPlays = 0
	for thing1 in extraList:
	    newInt = int(thing1['Count'])
	    totalPlays += newInt
	stringTotalPlays = str(totalPlays)
	tempString = stringTotalPlays+' of '+genformCount
	tempList = [[' ',' ','P',' ',tempString, totalPlays/genformCountInt]]
	bigList += tempList
	newCount = 1
	for dictionary1 in extraList:
	    genplay = dictionary1['List']
	    genplayCount = dictionary['Count']
	    genplayTotal = dictionary['Num']
	    genplayString = genplayCount+' of '+stringTotalPlays
	    tempList = [[' ',' ',newCount,genplay,genplayString,' ']]
	    bigList += tempList
	    newCount += 1
    return bigList


app = Flask(__name__)

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/home")
def home():
    return render_template('index.html')

@app.route("/drives", methods=['GET', 'POST'])
def drives():
    # Search query
    if request.method == "GET": # load queries
        eventquery = '''SELECT id, game FROM Events'''
        allGames = queryFormatted(EVENTS_COLS, eventquery)
        gameList = []
        for a in allGames:
            if a['game'] not in gameList:
                gameList.append(a['game'])
        return render_template('drives.html', result=gameList, content_type='application/json')

    form = request.form.get("form_type")
    if request.method == "POST":
        if form == 'GENERATE_DRIVES':
            select = request.form.get("selectGame")
            seriesQuery = "SELECT DISTINCT series from Events where game=\'" + str(select) + "\' ORDER BY series ASC"
            totalSeriesNums = queryFormatted(SERIES_COLS, seriesQuery)

	    seriesResults = []
            for t in totalSeriesNums:
                if 'series' not in t.keys():
                    continue
                playquery = "SELECT down, dist, rp, fieldPos, gain, result FROM Plays, Events WHERE Plays.event_id = Events.id and Events.game=\'" + str(select) + "\' and Events.series=" + t['series']
                re = queryFormatted(DRIVE_COLS, playquery)
		for r in re:
		    r['Series'] = t['series']
                seriesResults.append(re)
            return render_template('drives.html', data=seriesResults, content_type='application/json')


############################################################
@app.route("/reports", methods=['POST', 'GET'])
def reports():

    if request.method == "GET": # load queries
        return render_template('reports.html', result=[], content_type='application/json')

    # get dropdown option
    form = request.form.get("form_type")
    download = request.form.get("download")

    if request.method == "POST":
        if form == 'GENERATE_REPORT':
            select = request.form.get("selectReport")

            # run query based on dropdown value

            if select == "totalRPN": # totalRPN

                totalsResp = queryFormatted(RP_TOTALS_COLS, ALL_TOTALS_QUERY)
                winsResp = queryFormatted(RP_WINS_COLS, WINS_QUERY)

                COLS = RP_TOTALS_COLS + RP_WINS_COLS
                zipdata = zip(totalsResp, winsResp)
		print(zipdata)		
		if download == "DOWNLOAD":
			totalRPNDownload(zipdata)

                return render_template('reports.html', data=zipdata, cols=COLS, content_type='application/json')


            elif select == 'sitRP': 

		# first down
                first_totals_resp = queryFormatted(RP_TOTALS_COLS, TOTALS_QUERY_DOWNS.format("and Plays.down = 1") )
                first_wins_resp = queryFormatted(RP_WINS_COLS, WINS_QUERY_DOWNS.format("and Plays.down = 1") )

		# second and short 1-3
                second_short_totalsResp = queryFormatted(RP_TOTALS_COLS, TOTALS_QUERY_DOWNS.format("and Plays.down = 2 and Plays.dist >= 1 and Plays.dist <= 3"))
                second_short_winsResp = queryFormatted(RP_WINS_COLS, WINS_QUERY_DOWNS.format("and Plays.down = 2 and Plays.dist >= 1 and Plays.dist <= 3"))

		# second and 4-6
                second_mid_totalsResp = queryFormatted(RP_TOTALS_COLS, TOTALS_QUERY_DOWNS.format("and Plays.down = 2 and Plays.dist >= 4 and Plays.dist <= 6"))
                second_mid_winsResp = queryFormatted(RP_WINS_COLS, WINS_QUERY_DOWNS.format("and Plays.down = 2 and Plays.dist >= 4 and Plays.dist <= 6"))

		# second and 7-10
                second_long_totalsResp = queryFormatted(RP_TOTALS_COLS, TOTALS_QUERY_DOWNS.format("and Plays.down = 2 and Plays.dist >= 7 and Plays.dist <= 10"))
                second_long_winsResp = queryFormatted(RP_WINS_COLS, WINS_QUERY_DOWNS.format("and Plays.down = 2 and Plays.dist >= 7 and Plays.dist <= 10"))

		# second and 11+
                second_11_totalsResp = queryFormatted(RP_TOTALS_COLS, TOTALS_QUERY_DOWNS.format("and Plays.down = 2 and Plays.dist >= 11"))
                second_11_winsResp = queryFormatted(RP_WINS_COLS, WINS_QUERY_DOWNS.format("and Plays.down = 2 and Plays.dist >= 11"))

		#  third and short 1-2
                third_short_totalsResp = queryFormatted(RP_TOTALS_COLS, TOTALS_QUERY_DOWNS.format("and Plays.down = 3 and Plays.dist >= 1 and Plays.dist <= 2"))
                third_short_winsResp = queryFormatted(RP_WINS_COLS, WINS_QUERY_DOWNS.format("and Plays.down = 3 and Plays.dist >= 1 and Plays.dist <= 2"))

		# third and 3
                third_3_totalsResp = queryFormatted(RP_TOTALS_COLS, TOTALS_QUERY_DOWNS.format("and Plays.down = 3 and Plays.dist = 3"))
                third_3_winsResp = queryFormatted(RP_WINS_COLS, WINS_QUERY_DOWNS.format("and Plays.down = 3 and Plays.dist = 3"))

		# third and 4-6
                third_mid_totalsResp = queryFormatted(RP_TOTALS_COLS, TOTALS_QUERY_DOWNS.format("and Plays.down = 3 and Plays.dist >= 4 and Plays.dist <= 6"))
                third_mid_winsResp = queryFormatted(RP_WINS_COLS, WINS_QUERY_DOWNS.format("and Plays.down = 3 and Plays.dist >= 4 and Plays.dist <= 6"))

		# third and 7-10
                third_long_totalsResp = queryFormatted(RP_TOTALS_COLS, TOTALS_QUERY_DOWNS.format("and Plays.down = 3 and Plays.dist >= 7 and Plays.dist <=10"))
                third_long_winsResp = queryFormatted(RP_WINS_COLS, WINS_QUERY_DOWNS.format("and Plays.down = 3 and Plays.dist >= 7 and Plays.dist <=10"))

		# third and 11+
                third_11_totalsResp = queryFormatted(RP_TOTALS_COLS, TOTALS_QUERY_DOWNS.format("and Plays.down = 3 and Plays.dist >= 11"))
                third_11_winsResp = queryFormatted(RP_WINS_COLS, WINS_QUERY_DOWNS.format("and Plays.down = 3 and Plays.dist >= 11"))

		# fourth and short 1-3
                fourth_short_totalsResp = queryFormatted(RP_TOTALS_COLS, TOTALS_QUERY_DOWNS.format("and Plays.down = 4 and Plays.dist >= 1 and Plays.dist <= 3"))
                fourth_short_winsResp = queryFormatted(RP_WINS_COLS, WINS_QUERY_DOWNS.format("and Plays.down = 4 and Plays.dist >= 1 and Plays.dist <= 3"))

		# fourth and 4-6
                fourth_mid_totalsResp = queryFormatted(RP_TOTALS_COLS, TOTALS_QUERY_DOWNS.format("and Plays.down = 4 and Plays.dist >= 4 and Plays.dist <= 6"))
                fourth_mid_winsResp = queryFormatted(RP_WINS_COLS, WINS_QUERY_DOWNS.format("and Plays.down = 4 and Plays.dist >= 4 and Plays.dist <= 6"))

		# fourth and 7-10
                fourth_long_totalsResp = queryFormatted(RP_TOTALS_COLS, TOTALS_QUERY_DOWNS.format("and Plays.down = 4 and Plays.dist >= 7 and Plays.dist <= 10"))
                fourth_long_winsResp = queryFormatted(RP_WINS_COLS, WINS_QUERY_DOWNS.format("and Plays.down = 4 and Plays.dist >= 7 and Plays.dist <= 10"))

		# fourth and 11+
                fourth_11_totalsResp = queryFormatted(RP_TOTALS_COLS, TOTALS_QUERY_DOWNS.format("and Plays.down = 4 and Plays.dist >= 11"))
                fourth_11_winsResp = queryFormatted(RP_WINS_COLS, WINS_QUERY_DOWNS.format("and Plays.down = 4 and Plays.dist >= 11"))

		# first down
                fifth_totals_resp = queryFormatted(RP_TOTALS_COLS, TOTALS_QUERY_DOWNS.format("and Plays.down = 5") )
                fifth_wins_resp = queryFormatted(RP_WINS_COLS,WINS_QUERY_DOWNS.format("and Plays.down = 5") )

		# high red
		hred_tot_resp = queryFormatted(RP_TOTALS_COLS, TOTALS_QUERY_DOWNS.format("and fieldPos <= 30 and fieldPos >= 21"))
		hred_wins_resp = queryFormatted(RP_WINS_COLS, WINS_QUERY_DOWNS.format("and fieldPos <= 30 and fieldPos >= 21"))

		# red
		red_tot_resp = queryFormatted(RP_TOTALS_COLS, TOTALS_QUERY_DOWNS.format("and fieldPos <= 20 and fieldPos >= 11"))
		red_wins_resp = queryFormatted(RP_WINS_COLS, WINS_QUERY_DOWNS.format("and fieldPos <= 20 and fieldPos >= 11"))

		# red
		white_tot_resp = queryFormatted(RP_TOTALS_COLS, TOTALS_QUERY_DOWNS.format("and fieldPos <= 10 and fieldPos >= 6"))
		white_wins_resp = queryFormatted(RP_WINS_COLS, WINS_QUERY_DOWNS.format("and fieldPos <= 10 and fieldPos >= 6"))

		# blue
		blue_tot_resp = queryFormatted(RP_TOTALS_COLS, TOTALS_QUERY_DOWNS.format("and fieldPos <= 10 and fieldPos >= 6"))
		blue_wins_resp = queryFormatted(RP_WINS_COLS, WINS_QUERY_DOWNS.format("and fieldPos <= 10 and fieldPos >= 6"))

		# black
		black_tot_resp = queryFormatted(RP_TOTALS_COLS, TOTALS_QUERY_DOWNS.format("and fieldPos >= -10 and fieldPos <= -1"))
		black_wins_resp = queryFormatted(RP_WINS_COLS, WINS_QUERY_DOWNS.format("and fieldPos >= -10 and fieldPos <= -1"))

        	# zip data
        	first_zip = zip(first_totals_resp, first_wins_resp)
        	firstList = sitRPNDownload(first_zip)
		second_short_zip = zip(second_short_totalsResp, second_short_winsResp)
		second_short = sitRPNDownload(second_short_zip)
        	second_mid_zip = zip(second_mid_totalsResp, second_mid_winsResp)
        	second_mid = sitRPNDownload(second_mid_zip)
		second_long_zip = zip(second_long_totalsResp, second_long_winsResp)
        	second_long = sitRPNDownload(second_long_zip)
		second_11_zip = zip(second_11_totalsResp, second_11_winsResp)
		second_11 = sitRPNDownload(second_11_zip)
		third_short_zip = zip(third_short_totalsResp, third_short_winsResp)
		third_short = sitRPNDownload(third_short_zip)
		third_3_zip = zip(third_3_totalsResp, third_3_winsResp)
		third_3 = sitRPNDownload(third_3_zip)
		third_mid_zip = zip(third_mid_totalsResp, third_mid_winsResp)
		third_mid = sitRPNDownload(third_mid_zip)
		third_long_zip = zip(third_long_totalsResp, third_long_winsResp)
		third_long = sitRPNDownload(third_long_zip)
		third_11_zip = zip(third_11_totalsResp, third_11_winsResp)
        	third_11 = sitRPNDownload(third_11_zip)
		fourth_short_zip = zip(fourth_short_totalsResp, fourth_short_winsResp)
        	fourth_short = sitRPNDownload(fourth_short_zip)
		fourth_mid_zip = zip(fourth_mid_totalsResp, fourth_mid_winsResp)
        	fourth_mid = sitRPNDownload(fourth_mid_zip)
		fourth_long_zip = zip(fourth_long_totalsResp, fourth_long_winsResp)
        	fourth_long = sitRPNDownload(fourth_long_zip)
		fourth_11_zip = zip(fourth_11_totalsResp, fourth_11_winsResp)
        	fourth_11 = sitRPNDownload(fourth_11_zip)
		fifth_zip = zip(fifth_totals_resp, fifth_wins_resp)
		fifthList = sitRPNDownload(fifth_zip)
		hred_zip = zip(hred_tot_resp, hred_wins_resp)
		hredList = sitRPNDownload(hred_zip)
		red_zip = zip(red_tot_resp, red_wins_resp)
		redList = sitRPNDownload(red_zip)
		white_zip = zip(white_tot_resp, white_wins_resp)
		whiteList = sitRPNDownload(white_zip)
		black_zip = zip(black_tot_resp, black_wins_resp)
		blackList = sitRPNDownload(black_zip)
		blue_zip = zip(blue_tot_resp, blue_wins_resp)
		blueList = sitRPNDownload(blue_zip)

		bigList = firstList + second_short + second_mid + second_long + second_11 + third_short + third_3 + third_mid + third_long + third_11 + fourth_short + fourth_mid + fourth_long + fourth_11 + fifthList + hredList + redList + whiteList + blackList + blueList

		# initialize dictionary to pass to html
		d = collections.OrderedDict()
		d["1st Down"] = first_zip
		d["2nd and Short (1-3)"] = second_short_zip
		
		d["2nd and Mid (4-6)"] = second_mid_zip
		d["2nd and Long (7-10)"] = second_long_zip
		d["2nd and 11+"] = second_11_zip
		d["3rd and Short (1-3)"] = third_short_zip
		d["3rd and 3"] = third_3_zip
		d["3rd and Mid (4-6)"] = third_mid_zip
		d["3rd and Long (7-10)"] = third_long_zip
		d["3rd and 11+"] = third_11_zip
		d["4th and Short (1-3)"] = fourth_short_zip
		d["4th and Mid (4-6)"] = fourth_mid_zip
		d["4th and Long (7-10)"] = fourth_long_zip
		d["4th and 11+"] = fourth_11_zip
		d["5th"] = fifth_zip
		d["6. High Red"] = hred_zip 
		d["7. Red"] = red_zip 
		d["8. White"] = white_zip 
		d["9. Blue"] = blue_zip 
		d["10. Black"] = black_zip 

            	COLS = RP_TOTALS_COLS + RP_WINS_COLS

		if download == "DOWNLOAD":
			with open('sitRPNdl.csv', 'w') as csvfile:
			    writer = csv.writer(csvfile)
			    writer.writerows(bigList)
			csvfile.close()		
		return render_template('sitRP.html', data=d, cols=COLS, content_type='application/json')


	    elif select == 'backfields':
		backResp = queryFormatted(ALL_BACKFIELD_COLS, ALL_BACKFIELD_QUERY)

		b = []
		queries = []
		d = {}

		for i in backResp:
			name = i['Backfield']
			newName = "\'" + name + "\'"
			b.append(name)
			query = BACKFIELD_QUERY.format(newName)
			resp = queryFormatted(BACKFIELD_TABLE_COLS, query)
			d[name] = resp
			queries.append(resp)
		data = zip(b, queries)
		return render_template('motions.html', d=d, m=b, data=data, cols=MOTION_TABLE_COLS, content_type='application/json')


            elif select == 'motions':
                motionResp = queryFormatted(ALL_MOTION_COLS, ALL_MOTIONS_QUERY)
                m = []
                queries = []
		d = {}

                for i in motionResp:    # create list of all motion names
                    name = i['Motion']
                    newName = "\'" + name + "\'"
                    m.append(name)
                    query = MOTION_QUERY.format(newName) # run query with specific name
                    resp = queryFormatted(MOTION_TABLE_COLS, query)
		    d[name] = resp
                    queries.append(resp)

		data = zip(m, queries)

                return render_template('motions.html', d=d,m=m, data=data, cols=MOTION_TABLE_COLS, content_type='application/json')

                # queries = list of queries for each motion name [query for oregon, ... , ]
                # m = list of motion names

	    # DROPDOWN OPTIONS FOR INVENTORIES
	    elif select == 'overallInv': 
		r = inventories("Plays.genFormation != 'victory'")
		return render_template('inventories.html', data=r[0], runs=r[1], passes=r[2], total=r[3], content_type='application/json')

	    # FIRST 
	    elif select == 'first': 
		r = inventories("Plays.down = 1")
		return render_template('inventories.html', data=r[0], runs=r[1], passes=r[2], total=r[3], content_type='application/json')

	    # SECOND
	    elif select == 'second_13': 
		r = inventories("Plays.down = 2 and Plays.dist >= 1 and Plays.dist <= 3")
		return render_template('inventories.html', data=r[0], runs=r[1], passes=r[2], total=r[3], content_type='application/json')

	    elif select == 'second_46': 
		r = inventories("Plays.down = 2 and Plays.dist >= 4 and Plays.dist <= 6")
		return render_template('inventories.html', data=r[0], runs=r[1], passes=r[2], total=r[3], content_type='application/json')

	    elif select == 'second_710': 
		r = inventories("Plays.down = 2 and Plays.dist >= 7 and Plays.dist <= 10")
		return render_template('inventories.html', data=r[0], runs=r[1], passes=r[2], total=r[3], content_type='application/json')

	    elif select == 'second_11': 
		r = inventories("Plays.down = 2 and Plays.dist >= 11")
		return render_template('inventories.html', data=r[0], runs=r[1], passes=r[2], total=r[3], content_type='application/json')

 	    # THIRD
	    elif select == 'third_12': 
		r = inventories("Plays.down = 3 and Plays.dist >= 1 and Plays.dist <= 2")
		return render_template('inventories.html', data=r[0], runs=r[1], passes=r[2], total=r[3], content_type='application/json')

	    elif select == 'third_3': 
		r = inventories("Plays.down = 3 and Plays.dist = 3")
		return render_template('inventories.html', data=r[0], runs=r[1], passes=r[2], total=r[3], content_type='application/json')

	    elif select == 'third_46': 
		r = inventories("Plays.down = 3 and Plays.dist >= 4 and Plays.dist <= 6")
		return render_template('inventories.html', data=r[0], runs=r[1], passes=r[2], total=r[3], content_type='application/json')

	    elif select == 'third_710': 
		r = inventories("Plays.down = 3 and Plays.dist >= 7 and Plays.dist <= 10")
		return render_template('inventories.html', data=r[0], runs=r[1], passes=r[2], total=r[3], content_type='application/json')

	    elif select == 'third_11': 
		r = inventories("Plays.down = 3 and Plays.dist >= 11")
		return render_template('inventories.html', data=r[0], runs=r[1], passes=r[2], total=r[3], content_type='application/json')

	    # FOURTH
	    elif select == 'fourth_13': 
		r = inventories("Plays.down = 4 and Plays.dist >= 1 and Plays.dist <= 3")
		return render_template('inventories.html', data=r[0], runs=r[1], passes=r[2], total=r[3], content_type='application/json')

	    elif select == 'fourth_46': 
		r = inventories("Plays.down = 4 and Plays.dist >= 4 and Plays.dist <= 6")
		return render_template('inventories.html', data=r[0], runs=r[1], passes=r[2], total=r[3], content_type='application/json')

	    elif select == 'fourth_710': 
		r = inventories("Plays.down = 4 and Plays.dist >= 7 and Plays.dist <= 10")
		return render_template('inventories.html', data=r[0], runs=r[1], passes=r[2], total=r[3], content_type='application/json')

	    elif select == 'fourth_11': 
		r = inventories("Plays.down = 4 and Plays.dist >= 11")
		return render_template('inventories.html', data=r[0], runs=r[1], passes=r[2], total=r[3], content_type='application/json')

	    elif select == 'fifth': 
		r = inventories("Plays.down = 5")
		return render_template('inventories.html', data=r[0], runs=r[1], passes=r[2], total=r[3], content_type='application/json')


############################################################
@app.route("/players", methods=['POST', 'GET'])
def players():

    #r = dictionary returned from database query
    r = queryFormatted(PLAYER_COLS, PLAYERS_GET_QUERY)

    if request.method == "GET": # load queries
        display = [record for record in r if record["active"] == "1"]

        return render_template('players.html', result=display, content_type='application/json')

    form = request.form.get("form_type") # hidden input to specify which form: edit, delete, insert

    ### EDIT
    if form == "EDIT":
        name = request.form.get("name")
        position = request.form.get("position")
        playerTag = request.form.get("playerTag")
        height = request.form.get("height")
        weight = request.form.get("weight")
        active = request.form.get("active")

        # update db where playerTag = xxx
        query = 'UPDATE Players SET name="{}", position="{}", playerTag="{}", ' \
                'height="{}", weight="{}", active={} WHERE playerTag="{}";'.format(
                name, position, playerTag, height, weight, active, playerTag)
        
        try:
            cur.execute(query)
            cur.fetchall()
        except:
            flash("Invalid attribute entered - database not updated")

        r = queryFormatted(PLAYER_COLS, PLAYERS_GET_QUERY)
        display = [record for record in r]

        return render_template('players.html', result=display, content_type='application/json')


    ### INSERT - gets values from form
    elif form == "INSERT":
        temp = {}
        insert_name = request.form.get("name")
        values = ', '.join(['"' + insert_name + '"',
                            '"' + request.form.get("position") + '"',
                            '"' + request.form.get("playerTag") + '"',
                            request.form.get("height"),
                            request.form.get("weight"),
                            request.form.get("active")])
        query = 'INSERT INTO Players VALUES (' + values + ');'

        try:
            cur.execute(query)
            cur.fetchall()
        except:
            flash("Invalid attribute entered - database not updated")

        r = queryFormatted(PLAYER_COLS, PLAYERS_GET_QUERY)
        display = [record for record in r]

        # update database here
        return render_template('players.html', result=display, content_type='application/json')

    ### DELETE players - update where playerTag = xxx
    elif form == "DELETE":
        playerTag = request.form.get("deletePlayer")   # get playerTag of row to delete
        query = 'UPDATE Players SET active=0 WHERE playerTag="{}";'.format(playerTag)
        cur.execute(query)
        cur.fetchall()
        r = queryFormatted(PLAYER_COLS, PLAYERS_GET_QUERY)
        display = [record for record in r]

        return render_template('players.html', result=display, content_type='application/json')


if __name__ == "__main__":
    atexit.register(exitFunc, db=db)
    if len(sys.argv) != 2:
        print("Usage: python server.py PORT")
        exit(1)
    PORT = sys.argv[1]
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
    app.run(host='0.0.0.0', port=PORT, threaded=True)
