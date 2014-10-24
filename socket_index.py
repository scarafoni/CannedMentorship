from flask import Flask, render_template, request, jsonify
from redis import Redis
from collections import Counter


# Initialize the Flask application
def get_total_players():
    with open('data/total_players.txt', 'r') as f:
        return int(''.join(f.read().split()))


def get_leader():
    with open('data/leader.txt','r') as f:
        return f.read().rstrip()


def add_player():
    x = get_total_players()
    x += 1
    with open('data/total_players.txt', 'w') as f:
        f.write(str(x))


def set_state(state):
    with open('data/state.txt', 'w') as f:
        f.write(state)


def get_state():
    with open('data/state.txt', 'r') as f:
        return f.read()


def trim_null(x):
    if '' in x:
        x.remove('')
    return x


# returns a list
def get_people_so_far():
    with open('data/people_so_far.txt', 'r') as f:
        x = f.read()
        x = x.split('\n')
        return trim_null(x)


def reset_people_so_far():
    with open('data/people_so_far.txt', 'w') as f:
        f.write('')

def reset_user_inputs():
    with open('data/user_inputs.txt','w') as f:
        f.write('')


def add_client_input(id, input):
    with open('data/people_so_far.txt', 'a') as f,\
         open('data/user_inputs.txt', 'a') as f1:
        f.write(id+'\n') 
        f1.write(input+'\n')


# takes a list as input
def count_votes(votes, vote_list):
    i = votes.index(max(votes))
    most_popular = vote_list[i] 
    write_instruction(most_popular)


def get_user_inputs():
    with open('data/user_inputs.txt','r') as f:
        x = f.read().split('\n')
        return trim_null(x)


def get_instructions():
    with open('data/instructions.txt') as f:
        return f.read().strip()


def write_instruction(new_inst):
    with  open('data/instructions.txt','a') as f:
        f.write(new_inst+'\n')


def get_choices():
    with open('data/choices.txt', 'r') as f:
        x = f.read().split('\n')
        return trim_null(x)


def reset_choices():
    with open('data/choices.txt', 'w') as f:
        f.write('')


def add_finish_vote(u_vote):
    with open('data/finish_votes.txt','a') as f:
       f.write(u_vote+'\n') 

# placeholder for the ai program
# takes in a list of strings
def run_ai(props):
    return props

app = Flask(__name__)

redis = Redis()


@app.before_first_request
def startup():
    redis.flushdb()
    redis.set('total_players', '0')
    redis.set('leader', '1')
    redis.set('state', 'find')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_id')
def get_id():
    '''
    x += 1
    redis.set('total_players', str(x))
    '''
    redis.incr('total_players')
    return jsonify(result=redis.get('total_players'))


@app.route('/propose_instruct')
def propose_instruct():
    u_id = request.args.get('u_id', 0)
    if redis.get('state') == 'find' and u_id == redis.get('leader'):
        redis.set('state', 'write')
        return jsonify(result="ok lets write an instruction!")
    else:
        return jsonify(result="you cannot propose a new instruction now")


# receives the users instruction text
@app.route('/send_my_inst')
def get_inst_text():
    u_instruct = request.args.get('u_instruct', 0)
    u_id = request.args.get('u_id', 1)
    if redis.get('state') == 'write': 
        # the the current instruction to far
        people_so_far = redis.lrange('input_ids', 0, -1)
        if u_id not in people_so_far:
            print('people so far',people_so_far)
            redis.rpush('inputs', u_instruct)
            redis.rpush('input_ids', u_id)

            # change the state to vote if all the votes are in
            if int(redis.llen('inputs')) == int(redis.get('total_players')):
                # run the ai, make the list of choices
                choices  = run_ai(redis.lrange('inputs',0,-1))
                for choice in choices:
                    redis.lpush('choices',choice)
                # reset the inputs and input_ids
                redis.delete('inputs')
                redis.delete('input_ids')
                redis.set('state', 'vote')

            return jsonify(result="recieve input "+u_instruct+" thank you!")

        else:
            return jsonify(result="you have already submitted an instruction")
    else:
        return jsonify(result="you cannot submit instructions yet")


# track a vote
@app.route('/send_my_vote')
def send_my_vote():
    u_choice = request.args.get('u_choice', 0)
    u_id = request.args.get('u_id', 1)
    if redis.get('state') == 'vote':
        # add the vote if it's not in already
        proposers = redis.lrange('input_ids',0,-1)
        if u_id not in proposers:
            redis.rpush('inputs', u_choice)
            redis.rpush('input_ids', u_id)

            # change state to find if all the votes are in
            if len(proposers) == redis.get('total_players'):
                redis.delete('inputs')
                redis.delete('input_ids')
                redis.set('state','find')
                
            return jsonify(result = "your vote for choice " + \
                           str(int(u_choice)+1)+" has been logged")
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
            winner = counter.most_common()[0]
            redis.set('state','find' if winner == 'no' else 'finish')

        return jsonify(result='finish vote received, thank you')
    else:
        return jsonify(result='this shouldnt be here')

@app.route('/updates')
def send_updates():
    #all updates require these
    state = redis.get('state')
    instructions = '\n'.join(redis.lrange('instructions',0,-1))
    leader  = redis.get('leader')
    print("##### updates #####")
    print('state',state)
    print('total players',redis.get('total_players'))
    print('inputs', redis.lrange('inputs',0,-1))
    print('input_ids,',redis.lrange('input_ids',0,-1))

    if state == 'find':
        return jsonify(instructions=instructions,\
                   leader=leader,\
                    state=state)

    #write state
    elif state == "write":
        return jsonify(instructions=instructions,\
                   leader=leader,\
                   state=state)

    # vote state
    elif state == "vote":
        vote_list = '\n'.join(redis.lrange('choices',0,-1))
        return jsonify(instructions=instructions,\
                       choices=vote_list,\
                       leader=leader,\
                       state=state)

    elif state == 'finish':
        return jsonify(instructions=instructions,\
                       choices=['Instructions complete, thank you for helping!'],\
                       leader=leader,\
                       state=state)
        

    elif state == 'vote_finish':
        return jsonify(instructions=instructions,\
                           leader=leader,\
                           state=state)
    else:
        print('ERROR')
        return jsonify(state="err")


if __name__ == '__main__':
    app.debug = True
    app.run()

