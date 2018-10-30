## RESTful server for interfacing with database

from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home_page():
	return 'Home Page - will link to /players, /events, and /games'

@app.route('/players/', methods=['GET'])
def players():
	return 'GET players'

@app.route('/players/<pid>', methods=['PUT', 'POST', 'DELETE'])
def player(pid):
	if request.method == 'PUT':
		return 'EDIT player {}'.format(pid)
	elif request.method == 'POST':
		return 'ADD player {}'.format(pid)
	elif request.method == 'DELETE':
		return 'DELETE player {}'.format(pid)

@app.route('/events/', methods=['GET'])
def eventss():
	return 'GET events'

@app.route('/events/<eid>', methods=['PUT', 'POST', 'DELETE'])
def event(eid):
	if request.method == 'PUT':
		return 'EDIT event {}'.format(eid)
	elif request.method == 'POST':
		return 'ADD event {}'.format(eid)
	elif request.method == 'DELETE':
		return 'DELETE event {}'.format(eid)

@app.route('/plays/', methods=['GET'])
def plays():
	return 'GET plays'

@app.route('/plays/<pid>', methods=['PUT', 'POST', 'DELETE'])
def play(pid):
	if request.method == 'PUT':
		return 'EDIT play {}'.format(pid)
	elif request.method == 'POST':
		return 'ADD play {}'.format(pid)
	elif request.method == 'DELETE':
		return 'DELETE play {}'.format(pid)

def main():
	app.run(port=9111, debug=True)

if __name__=='__main__':
	main()
