from flask import *
import json
app = Flask(__name__)

@app.route("/")
def main():
    return None

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
    r = [{'PlayerName':'Josh Adams', 'Position':'RB', 'PlayerTag':'123'}, {'PlayerName':'Ian Book', 'Position':'QB', 'PlayerTag':'456'}]
    # r = json returned from database query
    
    if request.method == "GET":
        return render_template('players.html', t="ABBY", result=r, content_type='application/json')
        
    else: 
        temp = {}
        temp["PlayerName"] = request.form.get("PlayerName")
        temp["Position"] = request.form.get("Position")
        temp["PlayerTag"] = request.form.get("PlayerTag")

        r.append(temp) # add to dictionary
        # update database here
        return render_template('players.html', t="ABBY", result=r, content_type='application/json')

if __name__ == "__main__":
    app.run()
