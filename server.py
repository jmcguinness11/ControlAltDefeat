from flask import *
import json
import MySQLdb
import atexit

#global variables for column names
PLAYER_COLS = ['name', 'position', 'playerTag', 'height', 'weight', 'active']
PLAYERS_GET_QUERY = "SELECT * FROM Players WHERE active=1;"
DRIVE_COLS = ['Down', 'Dist', 'Run/Pass', 'FieldPos', 'Gain', 'Result', 'Explosive']

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

app = Flask(__name__)

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/home")
def home():
    return render_template('index.html')

@app.route("/events")
def events():
    return render_template('events.html')

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


@app.route("/players", methods=['POST', 'GET'])
def players():
    
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
    app.run(host='0.0.0.0', port='5210', threaded=True)
