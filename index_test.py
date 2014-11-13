from flask import Flask, render_template, request, jsonify
import redis
from collections import Counter
import os
import logging
import sort_answers
import gevent
from flask_sockets import Sockets
import random
import json
# import sys

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
    print('raw votes',props)
    return props # sort_answers.filter_inputs(props)


app = Flask(__name__)
sockets = Sockets(app)

redis_url = os.getenv('REDISTOGO_URL','redis://redistogo:5e00cfed335a73ab9a5a515cef203d3d@greeneye.redistogo.com:10505/' )
redis = redis.from_url(redis_url)

class Input(object):
    '''store user inputs'''
            
    __slots__ = 'user', 'val', 'time'

    def __init__(user, val, time):
        self.user = user
        self.val = val
        self.time = time


class cmBackend(object):
    def __init__(self):
        self.clients = list()
        self.db = redis
        self.state = 'find'
        self.inputs = []
        
    def register(self, client):
        '''registers a user'''
        print('client registered:',client)
        self.clients.append(client)

    def add_input(self, input):
        '''adds user input to the database'''
        print('add_input')
        self.inputs.append(input)

    def send(self, client, data):
        '''send data to a client'''
        try:
            client.send(data)
        except Exception:
            self.clients.remove(client)
            print('client logged out:',client)

    def update_backend(self):
        '''updates the backend state as needed'''
        self.state = 'find' 

    def run(self):
        '''send updates to the clients'''
        self.update_backend()
        while not self.state == 'finish':
            for client in self.clients:
                to_send = {}


                if self.state == 'find':
                    to_send = {
                        'inputs' : '\n'.join(self.inputs)
                    }

                else:
                    print('ERROR')

                to_send = json.dumps(to_send)
                gevent.spawn(self.send, client, to_send)
            gevent.sleep(seconds=1)

    def start(self):
        print('start')
        gevent.spawn(self.run)

cmbe = cmBackend()
cmbe.start()

@sockets.route('/submit')
def sub_ws(ws):
    '''get incoming websocket messages'''
    print('connect subws')
    while not ws.closed:
        gevent.sleep()

        message = ws.receive()
        if message:
            cmbe.add_input(message)
            print('message',message)

            
@sockets.route('/wsupdate')
def wsupdate(ws):
    print('connect update')
    cmbe.register(ws)

    while not ws.closed:
        # ws.send(json.dumps(dict(data="1")))
        gevent.sleep()

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

@app.route('/leave')
def logout():
    redis.decr('total_players')

    '''
    u_id = request.args.get('u_id',0)
    print('id to remove',u_id)
    # remove the id from registered
    redis.lrem('registered_ids',u_id)
    print('after removal ids',redis.lrange('registered_ids',0,-1))
    '''

    # change states as needed
    if redis.get('state') == 'write':
        # change the state to vote if all the votes are in
        if int(redis.llen('inputs')) == int(redis.get('total_players')):
            # run the ai, make the list of choices
            choices  = run_ai(redis.lrange('inputs',0,-1))
            for choice in choices:
                redis.rpush('choices',choice)
            # reset the inputs and input_ids
            redis.delete('inputs')
            redis.delete('input_ids')
            redis.set('state', 'vote')

    elif redis.get('state') == 'vote':
        if int(redis.llen('inputs')) == int(redis.get('total_players')):
            # append the most populat instruction to the list
            # print('count votes',redis.lrange('inputs',0,-1),\
            #                    redis.lrange('choices',0,-1))
            new_inst = count_votes(redis.lrange('inputs',0,-1),\
                                   redis.lrange('choices',0,-1))

            # print the instructions for the log
            redis.rpush('instructions',new_inst)
            redis.delete('inputs')
            redis.delete('input_ids')
            redis.delete('choices')
            redis.set('state','find')

    elif redis.get('state') == 'vote_finish':
        if redis.llen('input_ids') == int(redis.get('total_players')):
            # tally the votes
            votes = redis.lrange('inputs',0,-1)
            counter = Counter(votes)
            winner = counter.most_common()[0][0]
            redis.set('state','find' if winner == 'no' else 'finish')
            # print out the final instructions
            if redis.get('state') == 'finish':
                print('final instructions',redis.lrange('instructions',0,-1))
            redis.delete('inputs')
            redis.delete('input_ids')
        
    return jsonify(result='goodbye')
       

@app.route('/get_id')
def get_id():
    redis.incr('total_players')
    print('logging',redis.get('total_players'))
    redis.incr('next_id')
    '''
    ids = redis.lrange('registered_ids',0,-1)
    print('$$$$$$$$',ids)
    for i in range(1,int(redis.get('total_players'))+1):
       if str(i) not in ids:
           print('registering at- ',i)
           redis.rpush('registered_ids',i) 
           print('new registered- ',redis.lrange('registered_ids',0,-1))
           return jsonify(result=str(i))
    '''
    i = redis.get('next_id')
    return jsonify(result=i)
    return jsonify(result="id make error")


@app.route('/propose_instruct')
def propose_instruct():
    u_id = request.args.get('u_id', 0)
    u_id = request.args.get('u_id', 0)
    # print('args',request.args)
    if redis.get('state') == 'find' and u_id == redis.get('leader'):
        redis.set('state', 'write')
        return jsonify(result="ok lets write an instruction!")
    else:
        return jsonify(result="you cannot propose a new instruction now")


# receives the users instruction text
@app.route('/send_my_inst')
def send_my_inst():
    u_instruct = request.args.get('u_instruct', 0)
    u_id = request.args.get('u_id', 1)
    if redis.get('state') == 'write': 
        # the the current instruction to far
        people_so_far = redis.lrange('input_ids', 0, -1)
        if u_id not in people_so_far:
            redis.rpush('inputs', u_instruct)
            redis.rpush('input_ids', u_id)

            # change the state to vote if all the votes are in
            if int(redis.llen('inputs')) == int(redis.get('total_players')):
                # print the inputs for logging
                # run the ai, make the list of choices
                choices  = run_ai(redis.lrange('inputs',0,-1))
                for choice in choices:
                    redis.rpush('choices',choice)
                # reset the inputs and input_ids
                redis.delete('inputs')
                redis.delete('input_ids')
                redis.set('state', 'vote')

            return jsonify(result="recieve input, \""+u_instruct+"\" thank you!")

        else:
            return jsonify(result="you have already submitted an instruction")
    else:
        return jsonify(result="you cannot submit instructions yet")


# track a vote
@app.route('/send_my_vote')
def send_my_vote():
    u_choice = request.args.get('u_choice', 0)
    choice_text = redis.lindex('choices',int(u_choice))
    u_id = request.args.get('u_id', 1)
    if redis.get('state') == 'vote':
        # add the vote if it's not in already
        proposers = redis.lrange('input_ids',0,-1)
        if u_id not in proposers:
            redis.rpush('inputs', u_choice)
            redis.rpush('input_ids', u_id)

            # change state to find if all the votes are in
            if int(redis.llen('inputs')) == int(redis.get('total_players')):
                # print('count votes',redis.lrange('inputs',0,-1),\
                                    #redis.lrange('choices',0,-1))
                new_inst = count_votes(redis.lrange('inputs',0,-1),\
                                       redis.lrange('choices',0,-1))

                # print the instructions for the log
                # print('choices',redis.lrange('choices',0,-1))
                redis.rpush('instructions',new_inst)
                redis.delete('inputs')
                redis.delete('input_ids')
                redis.delete('choices')
                redis.set('state','find')
                
            return jsonify(result = "your vote for choice \"" + choice_text
                           +"\" has been logged")
        else:
            return jsonify(result="you cannot vote twice")
    else:
        return jsonify(result="you cannot vote yet!")


# 
@app.route('/finish')
def receive_finish():
    # we can only finish if we're in the find stage
    if redis.get('state') == 'find':
        redis.set('state', 'vote_finish')
        
        #change state to vote_finish
        redis.set('state','vote_finish') 

        return jsonify(result='stuff')
    else:
        return jsonify(result='false', msg="you cannot finish now")


# collect votes to see if we're finished
@app.route('/vote_finish')
def vote_finish():
    u_id = request.args.get('u_id', 0) 
    u_vote = request.args.get('u_vote', 1)
    if redis.get('state') == 'vote_finish' and u_id not in redis.lrange('input_ids',0,-1):
        redis.rpush('inputs', u_vote)
        redis.rpush('input_ids', u_id)
        
        # if all the votes are in, tally the votes
        if redis.llen('input_ids') == int(redis.get('total_players')):
            # tally the votes
            votes = redis.lrange('inputs',0,-1)
            counter = Counter(votes)
            winner = counter.most_common()[0][0]
            redis.set('state','find' if winner == 'no' else 'finish')
            if redis.get('state') == 'finish':
                print('final instructions',redis.lrange('instructions',0,-1))
            redis.delete('inputs')
            redis.delete('input_ids')

        return jsonify(result='finish vote received, thank you')
    else:
        return jsonify(result='this shouldnt be here')

@app.route('/updates')
def send_updates():
    #all updates require these
    u_id = request.args.get('u_id',0)
    state = redis.get('state')
    instructions = redis.lrange('instructions',0,-1)
    leader  = redis.get('leader')
    '''
    print("##### updates #####")
    print('state',state)
    print('instructions',instructions)
    print('total players',redis.get('total_players'))
    print('inputs', redis.lrange('inputs',0,-1))
    print('input_ids,',redis.lrange('input_ids',0,-1))
    print('registered ids',redis.lrange('registered_ids',0,-1))
    '''

    if state == 'find':
        return jsonify(instructions=instructions,\
                   leader=leader,\
                    state=state)

    #write state
    elif state == "write":
        got_my_input = u_id in redis.lrange('input_ids',0,-1)
        # print('got_my_input',got_my_input)
        return jsonify(inputs=str(len(redis.lrange('inputs',0,-1))),\
                   got_my_input=got_my_input,\
                   total_players=redis.get('total_players'),\
                   instructions=instructions,\
                   leader=leader,\
                   state=state)

    # vote state
    elif state == "vote":
        # vote_list = '\n'.join(redis.lrange('choices',0,-1))
        vote_list = (redis.lrange('choices',0,-1))
        got_my_input = u_id in redis.lrange('input_ids',0,-1)
        return jsonify(inputs=str(len(redis.lrange('inputs',0,-1))),\
                       got_my_input=got_my_input,\
                       total_players=redis.get('total_players'),\
                       instructions=instructions,\
                       choices=vote_list,\
                       leader=leader,\
                       state=state)

    elif state == 'finish':
        return jsonify(instructions=instructions,\
                       choices=['Instructions complete, thank you for helping!'],\
                       leader=leader,\
                       state=state)
        

    elif state == 'vote_finish':
        got_my_input = u_id in redis.lrange('input_ids',0,-1)
        return jsonify(inputs=str(len(redis.lrange('inputs',0,-1))),\
                       got_my_input=got_my_input,\
                       total_players=redis.get('total_players'),\
                       instructions=instructions,\
                       leader=leader,\
                       state=state)
    else:
        print('ERROR')
        return jsonify(state="err")

if __name__ == '__main__':
    app.debug = True
    app.run()

