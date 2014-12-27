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
        self.finish_votes = []
        self.start_time = time.time()
        
    def register(self, client):
        '''registers a user'''
        self.clients.append(client)

    def unregister(self, client):
        '''unregisters a user'''
        self.clients.remove(client)

    def run_ai(props):
        '''run the ai sorter on the propositions'''
        print('raw votes', props)
        return props # sort_answers.filter_inputs(props)
    
    def count_votes(votes, vote_list):
        '''count a list of votes, return the most popular'''
        # print('count_votes',votes,vote_list)
        counts = [0] * len(votes)
        for choice in votes:
            counts[int(choice)] += 1
        i = counts.index(max(counts))
        most_popular = vote_list[i] 
        return most_popular

    def add_input(self, input, list):
        '''adds user input to the database'''
        
        # add to the list of proposals
        if self.state == 'write' and list == 'proposals':
            self.proposals.append(input)

        # add to the list of votes for proposals
        elif self.state == 'vote' and list == 'proposal_votes':
            self.proposal_votes.append(input)
        
        # add to the list of votes to finish
        elif self.state == 'vote_finish' and list == 'finish_votes':
            self.finish_votes.append(input)
        
        else:
            print 'cant add to list {} in state {}'.format(list, self.state)
        

    def send(self, client, data):
        '''send data to a client'''
        client.send(data)

    def update_backend(self):
        '''updates the backend state as needed'''
        
        # change write -> vote if the props are in
        if self.state == 'write' and \
                len(self.proposals) == len(self.clients):
            self.proposals = run_ai(self.proposals)
            self.state = 'vote'
        
        # change vote -> find if all the votes are in
        elif self.state == 'vote' and \
                len(self.proposal_votes) == len(self.clients):
            self.instructions.append(count_votes(self.proposals,\
                                                 self.proposal_votes))
            self.proposals = []
            self.proposals_votes = []
            self.state = 'find'
        
        # change vote_finish -> finish / write if votes are in
        elif self.state == 'vote_finish' and \
                len(self.finish_votes) == len(self.clients):
                 
            
            

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
        print('starting server')
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
        print('input',input)

        data = [] if input is None else json.loads(input)
        if 'close' in data:
            ws.close()
        elif 'u_instruct' in data:
            cmbe.add_input(data['u_instruct']) 
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
    return render_template('index_test.html')


if __name__ == '__main__':
    app.debug = True
    app.run()

