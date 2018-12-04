from flask import *
import sys
import json
import MySQLdb
import atexit
import itertools
import collections

#global variables for column names
PLAYER_COLS = ['name', 'position', 'playerTag', 'height', 'weight', 'active']
PLAYERS_GET_QUERY = "SELECT * FROM Players WHERE active=1;"
DRIVE_COLS = ['Down', 'Dist', 'Run/Pass', 'FieldPos', 'Gain', 'Result', 'Explosive']
EVENTS_COLS = ['id', 'game']
SERIES_COLS = ['series']

########## QUERIES FOR REPORTS ##########

# ex. format totals query with "and Plays.down = 2 and Plays.dist >= 1 and Plays.dist <= 3"
# ex format wins query with "and Plays.down = 2 and Plays.dist >= 1 and Plays.dist <= 3"
RP_TOTALS_COLS = ['RP', 'PlayCount', 'PlayTotal', 'PlayPercent']
RP_WINS_COLS = ['RP', 'WinCount', 'TotalRP', 'WinPercent']

TOTALS_QUERY_DOWNS = "(SELECT  Plays.rp as 'RP', count(Plays.rp) as 'PlayCount', max(tot.c) as PlayTotal, CONCAT(TRUNCATE(100*count(Plays.rp)/max(tot.c), 2), '%') as PlayPercent FROM  Plays,  (select count(*) as c from Plays where genFormation != 'victory' {0}) tot,  (select rp, count(*) as 'Wins'from Plays where winP like 'Y' group by rp) wins WHERE  Plays.genFormation != 'victory' {0} and wins.rp = Plays.rp GROUP BY Plays.rp) UNION ALL (SELECT  Plays.rp as 'RP', count(Plays.rp) as 'Count', max(tot.c) as Total, CONCAT(TRUNCATE(100*count(Plays.rp)/max(tot.c), 2), '%') as Percent FROM  Plays,  (select count(*) as c from Plays where genFormation != 'victory' {0}) tot WHERE  Plays.genFormation != 'victory' {0} and Plays.rp like 'N' GROUP BY Plays.rp);"


ALL_TOTALS_QUERY = "(SELECT  Plays.rp as 'RP', count(Plays.rp) as 'PlayCount', max(tot.c) as PlayTotal, CONCAT(TRUNCATE(100*count(Plays.rp)/max(tot.c), 2), '%') as PlayPercent FROM  Plays,  (select count(*) as c from Plays where genFormation != 'victory') tot,  (select rp, count(*) as 'Wins'from Plays where winP like 'Y'group by rp) wins WHERE  Plays.genFormation != 'victory' and wins.rp = Plays.rp GROUP BY Plays.rp) UNION ALL (SELECT  Plays.rp as 'RP', count(Plays.rp) as 'Count', max(tot.c) as Total, CONCAT(TRUNCATE(100*count(Plays.rp)/max(tot.c), 2), '%') as Percent FROM  Plays,  (select count(*) as c from Plays where genFormation != 'victory') tot WHERE  Plays.genFormation != 'victory' and Plays.rp like 'N' GROUP BY Plays.rp) ;"

# for sitrp
WINS_QUERY_DOWNS = "select Plays.rp as 'RP', count(Plays.rp) as 'WinCount', totalRP.Count as 'TotalRP',  CONCAT(TRUNCATE(100*count(Plays.rp)/totalRP.Count, 2), '%') as WinPercent from Plays, (select count(*) as c from Plays where genFormation != 'victory' and winP like 'Y' {0}) tot, (select Plays.rp, count(Plays.rp) as Count from Plays where Plays.genFormation != 'victory' {0} and Plays.rp != 'N' group by Plays.rp) totalRP where Plays.genFormation != 'victory' {0} and Plays.winP like 'Y' and totalRP.rp = Plays.rp group by Plays.rp UNION ALL select '-' as RP, '-' as WinCount,'-' as TotalRP, '-' as WinPercent;"

WINS_QUERY = "select Plays.rp as 'RP', count(Plays.rp) as 'WinCount', totalRP.Count as 'TotalRP', CONCAT(TRUNCATE(100*count(Plays.rp)/totalRP.Count, 2), '%') as WinPercent from Plays, (select count(*) as c from Plays where genFormation != 'victory' and winP like 'Y') tot, (select Plays.rp, count(Plays.rp) as Count from Plays where Plays.genFormation != 'victory'and Plays.rp != 'N' group by Plays.rp) totalRP where Plays.genFormation != 'victory' and Plays.winP like 'Y' and totalRP.rp = Plays.rp group by Plays.rp UNION ALL select '-' as RP,'-' as WinCount,'-' as TotalRP,'-' as WinPercent;"

# MOTION

ALL_MOTION_COLS = ['Motion']
ALL_MOTIONS_QUERY = "select motions.List as Motion from (select distinct motion_shift as 'List', count(*) as 'rcount' from Plays where motion_shift != 'NULL' group by motion_shift order by count(*) desc) motions;"

# format motion_query with "oregon" to get table for specific motion name
MOTION_TABLE_COLS = ['RUN', 'PASS', 'TOTAL']
MOTION_QUERY = "select runs.r as RUN, pass.p as PASS, total.tot as TOTAL from  (select count(*) as tot from Plays where motion_shift = {0} and rp != 'n') total, (select count(*) as r from Plays where motion_shift = {0} and rp = 'r') runs, (select count(*) as p from Plays where motion_shift = {0} and rp = 'p') pass UNION ALL select CONCAT(TRUNCATE(runs.r/total.tot*100, 2), '%') as RUN, CONCAT(TRUNCATE(runs.r/total.tot*100, 2), '%') as PASS, '-' as TOTAL from  (select count(*) as tot from Plays where motion_shift = {0} and rp != 'n') total, (select count(*) as r from Plays where motion_shift = {0} and rp = 'r') runs, (select count(*) as p from Plays where motion_shift = {0} and rp = 'p') pass;"

# BACKFIELDS

ALL_BACKFIELD_COLS = ['Backfield']
ALL_BACKFIELD_QUERY = "select distinct backfield as Backfield from Plays where  backfield != 'NULL' group by backfield order by count(*) desc;"

# format motion_query with "oregon" to get table for specific motion name
BACKFIELD_TABLE_COLS = ['RUN', 'PASS', 'TOTAL']
BACKFIELD_QUERY = "select runs.r as RUN, pass.p as PASS, total.tot as TOTAL from  (select count(*) as tot from Plays where backfield = {0} and rp != 'n') total, (select count(*) as r from Plays where backfield = {0} and rp = 'r') runs, (select count(*) as p from Plays where backfield = {0} and rp = 'p') pass UNION ALL  select CONCAT(TRUNCATE(runs.r/total.tot*100, 2), '%') as RUN, CONCAT(TRUNCATE(pass.p/total.tot*100, 2), '%') as PASS, '-' as TOTAL from  (select count(*) as tot from Plays where backfield = {0} and rp != 'n') total, (select count(*) as r from Plays where backfield = {0} and rp = 'r') runs, (select count(*) as p from Plays where backfield = {0} and rp = 'p') pass;"


# get downs for 'where down = x and dist <= ...' 

#DOWNS_QUERY = "select distinct Plays.genFormation as 'List', count(Plays.down) as 'Count', CONCAT(TRUNCATE((count(Plays.down)/tot.t)*100, 2), '%') as Percent from Plays, (select 'Total', count(*) as 't' from Plays where {0}) tot where {0}  group by Plays.genFormation " # fill in 'where down = {1 and dist = 5}

DOWNS_QUERY = "select distinct Plays.genFormation as 'List', count(Plays.down) as 'Count', CONCAT(TRUNCATE((count(Plays.down)/tot.t)*100, 2), '%') as Percent from Plays, (select 'Total', count(*) as 't' from Plays where Plays.genFormation != 'victory' and {0}) tot where Plays.genFormation != 'victory' and {0} group by Plays.genFormation order by count(*) desc;"

TOTALS_QUERY = "select count(*) as 't' from Plays where {0};"

# query to get running and passing plays for each GENFORMATION
	# fill in with: {genFormation}, {R or P}, {down and distance}
GEN_FORMATION = "select distinct Plays.genPlay as 'List', count(*) as 'Count', totals.Total as Num from Plays, (select count(*) as Total from Plays where Plays.genFormation = {0}  and Plays.rp = {1} and {2}) totals where Plays.genFormation = {0} and Plays.rp = {1} and {2} group by Plays.genPlay order by count(*) desc;"

############################################################

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
		#print(k, col)
                col = str(col)
                row_dict[colNames[k]] = col.decode('ascii', 'ignore').encode('ascii')
        res_list.append(row_dict)
    return res_list


app = Flask(__name__)

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/home")
def home():
    return render_template('index.html')



#TODO - eventually change to "drives"
@app.route("/plays", methods=['GET', 'POST'])
def plays():
    # Search query
    if request.method == "GET": # load queries
        eventquery = '''SELECT id, game FROM Events'''
        allGames = queryFormatted(EVENTS_COLS, eventquery)
        gameList = []
        for a in allGames:
            if a['game'] not in gameList:
                gameList.append(a['game'])
	print(gameList)
        return render_template('plays.html', result=gameList, content_type='application/json')

    form = request.form.get("form_type")
    if request.method == "POST":
        if form == 'GENERATE_DRIVES':
            select = request.form.get("selectGame")
            seriesQuery = "SELECT DISTINCT series from Events where game=\'" + str(select) + "\' ORDER BY series ASC"
            totalSeriesNums = queryFormatted(SERIES_COLS, seriesQuery)

	    seriesResults = []
            for t in totalSeriesNums:
                playquery = "SELECT down, dist, rp, fieldPos, gain, result, explosive FROM Plays, Events WHERE Plays.event_id = Events.id and Events.game=\'" + str(select) + "\' and Events.series=" + t['series']
                re = queryFormatted(DRIVE_COLS, playquery)
		for r in re:
		    r['Series'] = t['series']
                seriesResults.append(re)
	    print(seriesResults)
            return render_template('plays.html', data=seriesResults, content_type='application/json')


############################################################
@app.route("/reports", methods=['POST', 'GET'])
def reports():

    print("entered reports")

    if request.method == "GET": # load queries
        return render_template('reports.html', result=[], content_type='application/json')

    # get dropdown option
    form = request.form.get("form_type")
    if request.method == "POST":
        if form == 'GENERATE_REPORT':
            select = request.form.get("selectReport")

            print("selected dropdown value: " + str(select))
            # run query based on dropdown value
            if select == "totalRPN": # totalRPN
                print("####### TOTAL RPN #######")

		print(TOTALS_QUERY)

                totalsResp = queryFormatted(RP_TOTALS_COLS, ALL_TOTALS_QUERY)
                winsResp = queryFormatted(RP_WINS_COLS, WINS_QUERY)
                print("\ntotals resp\n")
                print(totalsResp)
                print("\nwins resp\n")
                print(winsResp)
                print("\n")

                COLS = RP_TOTALS_COLS + RP_WINS_COLS
                zipdata = zip(totalsResp, winsResp)

                return render_template('reports.html', data=zipdata, cols=COLS, content_type='application/json')



            # TODO
            elif select == 'sitRP': 
                print("####### SITUATIONAL RP #######")

		# first down
                first_totals_resp = queryFormatted(RP_TOTALS_COLS, TOTALS_QUERY_DOWNS.format("and Plays.down = 1") )
                first_wins_resp = queryFormatted(RP_TOTALS_COLS,WINS_QUERY_DOWNS.format("and Plays.down = 1") )

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

		# TODO: TODO: TODO: add 5th, high red, red, white, blue, black


        	# zip data
        	first_zip = zip(first_totals_resp, first_wins_resp)

        	second_short_zip = zip(second_short_totalsResp, second_short_winsResp)
        	second_mid_zip = zip(second_mid_totalsResp, second_mid_winsResp)
        	second_long_zip = zip(second_long_totalsResp, second_long_winsResp)
        	second_11_zip = zip(second_11_totalsResp, second_11_winsResp)

		third_short_zip = zip(third_short_totalsResp, third_short_winsResp)
		third_3_zip = zip(third_3_totalsResp, third_3_winsResp)
		third_mid_zip = zip(third_mid_totalsResp, third_mid_winsResp)
		third_long_zip = zip(third_long_totalsResp, third_long_winsResp)
		third_11_zip = zip(third_11_totalsResp, third_11_winsResp)

        	fourth_short_zip = zip(fourth_short_totalsResp, fourth_short_winsResp)
        	fourth_mid_zip = zip(fourth_mid_totalsResp, fourth_mid_winsResp)
        	fourth_long_zip = zip(fourth_long_totalsResp, fourth_long_winsResp)
        	fourth_11_zip = zip(fourth_11_totalsResp, fourth_11_winsResp)

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

            	COLS = RP_TOTALS_COLS + RP_WINS_COLS

		return render_template('sitRP.html', data=d, cols=COLS, content_type='application/json')
            	#return render_template('reports.html', data=data, cols=COLS, titles=titles, content_type='application/json')



	    elif select == 'backfields':
		print("###BACKFIELDS#####")
		backResp = queryFormatted(ALL_BACKFIELD_COLS, ALL_BACKFIELD_QUERY)

		print(backResp)
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
                print("####### MOTIONS #######")

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

                print(data)

                return render_template('motions.html', d=d,m=m, data=data, cols=MOTION_TABLE_COLS, content_type='application/json')

                # queries = list of queries for each motion name [query for oregon, ... , ]
                # m = list of motion names

		
	    elif select == 'first': 
		print("####### FIRST  #######")
		FIRST_QUERY = DOWNS_QUERY.format("Plays.down = 1")
		firstResp = queryFormatted(['List', 'Count', 'Percent'], FIRST_QUERY)
		
		TOTALS_Q = TOTALS_QUERY.format('Plays.down =1')
		tResp = queryFormatted(['t'], TOTALS_Q) 
		total = tResp[0]['t']
	
		names = [] # list of all formations
		for formation in firstResp: 
			name = formation['List']
			#name = name.replace("\'", '')
			names.append(name)

		# loop through names and get run and pass tables for each formation in 1st down
		data = {}
		for name in names: 
		# format with play name, r/p, down and distance
			nameNew = "\'" + name + "\'"
			runs = GEN_FORMATION.format(nameNew, '\'r\'', "Plays.down = 1")
			passes = GEN_FORMATION.format(nameNew, '\'p\'', "Plays.down = 1")
			
			run_q = queryFormatted(['List', 'Count', 'Num'], runs)
			pass_q = queryFormatted(['List', 'Count', 'Num'], passes)

			data[name] = run_q + pass_q
		
		print(data)
		return render_template('inventories.html', data=firstResp, total=total, content_type='application/json')

############################################################
@app.route("/players", methods=['POST', 'GET'])
def players():

    print("entered players")
    #r = dictionary returned from database query
    r = queryFormatted(PLAYER_COLS, PLAYERS_GET_QUERY)
    print(r)

    if request.method == "GET": # load queries
        display = [record for record in r if record["active"] == "1"]

        return render_template('players.html', result=display, content_type='application/json')

    form = request.form.get("form_type") # hidden input to specify which form: edit, delete, insert
    print("FORM: " + form)

    ### EDIT
    if form == "EDIT":
        print("ENTERED EDIT")
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

        cur.execute(query)
        cur.fetchall()
        r = queryFormatted(PLAYER_COLS, PLAYERS_GET_QUERY)

        display = [record for record in r]

        return render_template('players.html', result=display, content_type='application/json')


    ### INSERT - gets values from form
    elif form == "INSERT":
        print("ENTERED INSERT")
        temp = {}
        insert_name = request.form.get("name")
        values = ', '.join(['"' + insert_name + '"',
                            '"' + request.form.get("position") + '"',
                            '"' + request.form.get("playerTag") + '"',
                            request.form.get("height"),
                            request.form.get("weight"),
                            request.form.get("active")])
        query = 'INSERT INTO Players VALUES (' + values + ');'
        print(query)

        print("Player to insert: " + insert_name) # debug

        cur.execute(query)
        cur.fetchall()
        r = queryFormatted(PLAYER_COLS, PLAYERS_GET_QUERY)
        display = [record for record in r]

        # update database here
        return render_template('players.html', result=display, content_type='application/json')

    ### DELETE players - update where playerTag = xxx
    elif form == "DELETE":
        print("ENTERED DELETE")
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
    app.run(host='0.0.0.0', port=PORT, threaded=True)
