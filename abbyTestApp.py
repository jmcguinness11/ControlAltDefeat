from flask import *
import json

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

@app.route("/plays")
def plays():
    return render_template('plays.html')


@app.route("/players", methods=['POST', 'GET'])
def players():
    r = [{'name':"Josh Adams", 'position':"RB", 'playerTag':"INND 02", 'height':None, 'weight':None, 'active':1},
         {'name':"Ian Book", 'position':"QB", 'playerTag':"INND 04", 'height':None, 'weight':None, 'active':1},
         {'name':"Dexter Williams", 'position':"RB", 'playerTag':"INND 09", 'height':None, 'weight':None, 'active':1}
        ]
    # r = json returned from database query --> only return where active == 1


    if request.method == "GET": # load queries
        display =[] # display players where active == 1
        for record in r:
            if record["active"] == 1:
                display.append(record)
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
        # update db where playerTag = xxx
        for record in r:
            if record["playerTag"] == playerTag:
                record["name"] = name
                record["position"] = position
                record["height"] = height
                record["weight"] = weight

        display = []
        for record in r:
            if record["active"] == 1:
                display.append(record)

        return render_template('players.html', result=display, content_type='application/json')


    ### INSERT - gets values from form
    elif form == "INSERT":
        print("ENTERED INSERT")
        temp = {}
        temp["name"] = request.form.get("name")
        temp["position"] = request.form.get("position")
        temp["playerTag"] = request.form.get("playerTag")
        temp["height"] = request.form.get("height")
        temp["weight"] = request.form.get("weight")
        temp["active"] = int(request.form.get("active"))
        
        print("Player to insert: " + temp["name"]) # debug

        r.append(temp) # add to dictionary
        
        display = []
        for record in r:
            if record["active"] == 1:
                display.append(record)
        
        # update database here
        return render_template('players.html', result=display, content_type='application/json')

    ### DELETE players - update where playerTag = xxx
    elif form == "DELETE":
        print("ENTERED DELETE")
        playerTag = request.form.get("deletePlayer")   # get playerTag of row to delete

        for record in r:
            print(record["playerTag"] + " - " + record["name"] + " - " + str(record["active"]))
            if record["playerTag"] == str(playerTag):
                record["active"] = 0                # set active to 0 to 'delete'
                # print("Player to delete: " + playerTag + ", " + record["name"]) # debug
        
        display = []
        for record in r:
            if record["active"] == 1:
                display.append(record)

        return render_template('players.html', result=display, content_type='application/json')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5210', threaded=True)
0', threaded=True)
