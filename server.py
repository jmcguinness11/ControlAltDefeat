from flask import *
import json
import MySQLdb
import atexit
import itertools

#global variables for column names
PLAYER_COLS = ['name', 'position', 'playerTag', 'height', 'weight', 'active']
PLAYERS_GET_QUERY = "SELECT * FROM Players WHERE active=1;"
DRIVE_COLS = ['Down', 'Dist', 'Run/Pass', 'FieldPos', 'Gain', 'Result', 'Explosive']

########## QUERIES FOR REPORTS ##########

# ex. format totals query with "and Plays.down = 2 and Plays.dist >= 1 and Plays.dist <= 3"
# ex format wins query with "and Plays.down = 2 and Plays.dist >= 1 and Plays.dist <= 3"
RP_TOTALS_COLS = ['RP', 'PlayCount', 'PlayTotal', 'PlayPercent']
RP_WINS_COLS = ['RP', 'WinCount', 'TotalRP', 'WinPercent']

TOTALS_QUERY_DOWNS = "(SELECT  Plays.rp as 'RP', count(Plays.rp) as 'PlayCount', max(tot.c) as PlayTotal, 100*count(Plays.rp)/max(tot.c) as PlayPercent FROM  Plays,  (select count(*) as c from Plays where genFormation != 'victory' {0}) tot,  (select rp, count(*) as 'Wins'from Plays where winP like 'Y'group by rp) wins WHERE  Plays.genFormation != 'victory' {0} and wins.rp = Plays.rp GROUP BY Plays.rp) UNION ALL (SELECT  Plays.rp as 'RP', count(Plays.rp) as 'Count', max(tot.c) as Total, 100*count(Plays.rp)/max(tot.c) as Percent FROM  Plays,  (select count(*) as c from Plays where genFormation != 'victory' {0}) tot WHERE  Plays.genFormation != 'victory' and {0} and Plays.rp like 'N' GROUP BY Plays.rp);"


TOTALS_QUERY = "(SELECT  Plays.rp as 'RP', count(Plays.rp) as 'PlayCount', max(tot.c) as PlayTotal, 100*count(Plays.rp)/max(tot.c) as PlayPercent FROM  Plays,  (select count(*) as c from Plays where genFormation != 'victory') tot,  (select rp, count(*) as 'Wins'from Plays where winP like 'Y'group by rp) wins WHERE  Plays.genFormation != 'victory' and wins.rp = Plays.rp GROUP BY Plays.rp) UNION ALL (SELECT  Plays.rp as 'RP', count(Plays.rp) as 'Count', max(tot.c) as Total, 100*count(Plays.rp)/max(tot.c) as Percent FROM  Plays,  (select count(*) as c from Plays where genFormation != 'victory') tot WHERE  Plays.genFormation != 'victory' and Plays.rp like 'N' GROUP BY Plays.rp) ;"


WINS_QUERY_DOWNS = "select Plays.rp as 'RP', count(Plays.rp) as 'WinCount', totalRP.Count as 'TotalRP', 100*count(Plays.rp)/totalRP.Count as WinPercent from Plays, (select count(*) as c from Plays where genFormation != 'victory' and winP like 'Y' {0}) tot, (select Plays.rp, count(Plays.rp) as Count from Plays where Plays.genFormation != 'victory' {0} and Plays.rp != 'N' group by Plays.rp) totalRP where Plays.genFormation != 'victory' {0} and Plays.winP like 'Y' and totalRP.rp = Plays.rp group by Plays.rp UNION ALL select '', '','', '';"

WINS_QUERY = "select Plays.rp as 'RP', count(Plays.rp) as 'WinCount', totalRP.Count as 'TotalRP', 100*count(Plays.rp)/totalRP.Count as WinPercent from Plays, (select count(*) as c from Plays where genFormation != 'victory' and winP like 'Y') tot, (select Plays.rp, count(Plays.rp) as Count from Plays where Plays.genFormation != 'victory'and Plays.rp != 'N' group by Plays.rp) totalRP where Plays.genFormation != 'victory' and Plays.winP like 'Y' and totalRP.rp = Plays.rp group by Plays.rp UNION ALL select '-' as RP,'-' as WinCount,'-' as TotalRP,'-' as WinPercent;"

# MOTION

ALL_MOTION_COLS = ['Motion']
ALL_MOTIONS_QUERY = "select motions.List as Motion from (select distinct motion_shift as 'List', count(*) as 'rcount' from Plays where motion_shift != 'NULL' group by motion_shift order by count(*) desc) motions;"

# format motion_query with "oregon" to get table for specific motion name
MOTION_TABLE_COLS = ['RUN', 'PASS', 'TOTAL']
MOTION_QUERY = "select runs.r as RUN, pass.p as PASS, total.tot as TOTAL from  (select count(*) as tot from Plays where motion_shift = {0} and rp != 'n') total, (select count(*) as r from Plays where motion_shift = {0} and rp = 'r') runs, (select count(*) as p from Plays where motion_shift = {0} and rp = 'p') pass UNION ALL select TRUNCATE(runs.r/total.tot*100, 2) as RUN, TRUNCATE(pass.p/total.tot*100, 2) as PASS, '-' as TOTAL from  (select count(*) as tot from Plays where motion_shift = {0} and rp != 'n') total, (select count(*) as r from Plays where motion_shift = {0} and rp = 'r') runs, (select count(*) as p from Plays where motion_shift = {0} and rp = 'p') pass;"


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
@app.route("/plays")
def plays():
    # Search query
    query = '''SELECT down, dist, rp, fieldPos, gain, result, explosive
            FROM Plays, Events
            WHERE Plays.event_id = Events.id
                and Events.game='Stanford' and Events.series=1'''
    r = queryFormatted(DRIVE_COLS, query)
    display = [record for record in r]

    return render_template('plays.html', result=display, content_type='application/json')


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

                print("PRINTING TOTALS QUERY")

                totalsResp = queryFormatted(RP_TOTALS_COLS, TOTALS_QUERY)
                winsResp = queryFormatted(RP_WINS_COLS, WINS_QUERY)
                print("\ntotals resp\n")
                print(totalsResp)
                print("\nwins resp\n")
                print(winsResp)
                print("\n")

                COLS = RP_TOTALS_COLS + RP_WINS_COLS
                zipdata = zip(totalsResp, winsResp)
                display = 'display'

                return render_template('reports.html', data=zipdata, display=display, cols=COLS, content_type='application/json')



            # TODO
            elif select == 'sitRP': # FIRST DOWN
                print("####### SECOND AND SHORT #######")

                titles = ["First Down", "Second and Short"]

                FIRST_TOTALS = TOTALS_QUERY.format("and Plays.down = 1")
                FIRST_WINS = SECOND_SHORT_WINS_QUERY.format("and Plays.down = 1")
                first_totals_resp = queryFormatted(RP_TOTALS_COLS, FIRST_TOTALS)
                first_wins_resp = queryFormatted(RP_TOTALS_COLS, FIRST_WINS)

                SECOND_SHORT_TOTALS = TOTALS_QUERY.format("and Plays.down = 2 and Plays.dist >= 1 and Plays.dist <= 3")
                SECOND_SHORT_WINS = SECOND_SHORT_WINS_QUERY.format("and Plays.down = 2 and Plays.dist >= 1 and Plays.dist <= 3")
                second_short_totalsResp = queryFormatted(RP_TOTALS_COLS, SECOND_SHORT_TOTALS)
                second_short_winsResp = queryFormatted(RP_WINS_COLS, SECOND_SHORT_WINS)

                print("\ntotals resp\n")
                print(totalsResp)
                print("\nwins resp\n")
                print(winsResp)
                print("\n")

                COLS = RP_TOTALS_COLS + RP_WINS_COLS
                zipdata = zip(totalsResp, winsResp)

                return render_template('reports.html', data=zipdata, cols=COLS, titles=titles, content_type='application/json')

            elif select == 'motions':
                print("####### MOTIONS #######")

                motionResp = queryFormatted(ALL_MOTION_COLS, ALL_MOTIONS_QUERY)
                m = []
                queries = []
                for i in motionResp:    # create list of all motion names
                    name = i['Motion']
                    name = "\'" + name + "\'"
                    m.append(name)
                    query = MOTION_QUERY.format(name) # run query with specific name
                    resp = queryFormatted(MOTION_TABLE_COLS, query)

                    queries.append(resp)
                print(queries[3])

                return render_template('reports.html', queries=queries, motionNames=m, cols=MOTION_TABLE_COLS, content_type='application/json')

                # queries = list of queries for each motion name [query for oregon, ... , ]
                # m = list of motion names


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
    app.run(host='0.0.0.0', port='5212', threaded=True)
