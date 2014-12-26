from flask import Flask, render_template
import redis
import os
import logging
import sort_answers
import gevent
from flask_sockets import Sockets
import time
import json

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


def count_votes(votes, vote_list):
    # print('count_votes',votes,vote_list)
    counts = [0] * len(votes)
    for choice in votes:
        counts[int(choice)] += 1
    i = counts.index(max(counts))
    most_popular = vote_list[i] 
    return most_popular

# placeholder for the ai program
def run_ai(props):
    print('raw votes', props)
    return props # sort_answers.filter_inputs(props)


app = Flask(__name__)
sockets = Sockets(app)

redis_url = os.getenv('REDISTOGO_URL','redis://redistogo:5e00cfed335a73ab9a5a515cef203d3d@greeneye.redistogo.com:10505/' )
redis = redis.from_url(redis_url)

class Input(object):
    '''store user inputs'''
            
    __slots__ = 'user', 'val', 'time'

    def __init__(self, user, val, time):
        self.user = user
        self.val = val
        self.time = time


class cmBackend(object):
    """the backend for cm: coordinates all the info"""

    def __init__(self):
        self.clients = []
        self.state = 'find'
        self.previous_state = 'find'
        self.instructions = []
        # proposed instructions this round
        self.proposals = []
        # voting on propositions info
        self.proposal_votes = []
        # votes on whether to stop
        self.finishvotes = []
        self.start_time = time.time()
        
    def register(self, client):
        '''registers a user'''
        print('client registered:',client)
        self.clients.append(client)

    def unregister(self, client):
        '''unregisters a user'''
        print('unregistered',client)
        self.clients.remove(client)
        print('new clients',self.clients)

    def add_input(self, input):
        '''adds user input to the database'''
        print('add_input')
        self.inputs.append(input)

    def send(self, client, data):
        '''send data to a client'''
        client.send(data)

    def update_backend(self):
        '''updates the backend state as needed'''
        
        # change write -> vote if the votes are in
        if self.state == 'write' and \
                len(self.proposals) == len(self.clients):
            self.proposals = run_ai(self.proposals)
            self.state = 'vote'
        
        elif self.state == 'vote' and \
                len(self.proposal_votes) == len(self.clients):
            self.instructions.append(count_votes(self.proposals,\
                                                 self.proposal_votes))
            self.proposals = []
            self.proposals_votes = []
            self.state = 'find'
            

    def run(self):
        '''send updates to the clients'''
        self.update_backend()
        while not self.state == 'finish':
            for client in self.clients:
                to_send = {}

                if self.state == 'find':
                    to_send = {
                        'inputs' : '\n'.join(self.proposals)
                    }

                else:
                    print('ERROR')

                to_send = json.dumps({
                    'numPlayers' : len(self.clients)
                })
                gevent.spawn(self.send, client, to_send)
            gevent.sleep(seconds=1)

    def start(self):
        print('start')
        gevent.spawn(self.run)

cmbe = cmBackend()
cmbe.start()

# receive messages from the websocket
@sockets.route('/ws')
def sub_ws(ws):
    '''websocket interface'''
    
    cmbe.register(ws)
    while not ws.closed:
        input = ws.receive()
        print(input)
        if input == 'close':
            ws.close()
        else:
            print('error')
        gevent.sleep()

    print('unregister')
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
    return render_template('index_test.html')


if __name__ == '__main__':
    app.debug = True
    app.run()

