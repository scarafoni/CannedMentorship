from flask import Flask, render_template
import redis
import os
import logging
import gevent
from flask_sockets import Sockets
from flask.ext.mail import Mail, Message
from cm_backend import cmBackend
import json

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


app = Flask(__name__)
sockets = Sockets(app)
app.config.update(
	DEBUG=True,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = 'cannedMentorship@gmail.com',
	MAIL_PASSWORD = 'cmpassword')
mail = Mail(app)

redis_url = os.getenv('REDISTOGO_URL','redis://redistogo:5e00cfed335a73ab9a5a515cef203d3d@greeneye.redistogo.com:10505/' )
redis = redis.from_url(redis_url)

cmbe = cmBackend(app, mail)
cmbe.start()

# receive messages from the websocket
@sockets.route('/ws')
def sub_ws(ws):
    '''websocket interface'''
    
    cmbe.register(ws)
    while not ws.closed:
        input = ws.receive()
        print('input',input)

        data = [] if input is None else json.loads(input)
        if 'close' in data:
            ws.close()

        elif 'prop_instruct' in data and cmbe.state == 'find' \
                and cmbe.leader == ws:
            cmbe.state = 'write' 
            print('changing from find to write') 

        elif 'u_instruct' in data:
            cmbe.add_input(ws, data['u_instruct'], 'proposals')
        
        elif 'u_choice' in data:
            cmbe.add_input(ws, data['u_choice'], 'proposal_votes')
    
        elif 'prop_finish' in data and cmbe.state == 'find':
            # print "right place"
            cmbe.state = 'vote_finish'

        elif 'u_vote' in data:
            cmbe.add_input(ws,data['u_vote'], 'finish_votes')

        gevent.sleep()

    cmbe.unregister(ws)

            

@app.before_first_request
def startup():
    redis.flushdb()
    redis.set('total_players', '0')
    redis.set('leader', '1')
    redis.set('next_id',0)
    redis.set('state', 'find')


@app.route('/')
def index():
    return render_template('index_ws.html')


if __name__ == '__main__':
    app.debug = True
    app.run()

