from flask import Flask, render_template, request, jsonify
from redis import Redis
from collections import Counter


def count_votes(votes, vote_list):
    # print('$$$$$$$$votes$$$$$',votes)
    # print('$$$$$$$$vote_list$$$$$',vote_list)
    i = votes.index(max(votes))
    # print('$$$$$$$$i$$$$$',i)
    most_popular = vote_list[i] 
    # print('$$$$$$$$most popullat$$$$$',most_popular)
    return most_popular

# placeholder for the ai program
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
def send_my_inst():
    u_instruct = request.args.get('u_instruct', 0)
    u_id = request.args.get('u_id', 1)
    if redis.get('state') == 'write': 
        # the the current instruction to far
        people_so_far = redis.lrange('input_ids', 0, -1)
        if u_id not in people_so_far:
            redis.lpush('inputs', u_instruct)
            redis.lpush('input_ids', u_id)

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
    print('########u_choice',u_choice)
    if redis.get('state') == 'vote':
        # add the vote if it's not in already
        proposers = redis.lrange('input_ids',0,-1)
        if u_id not in proposers:
            redis.rpush('inputs', u_choice)
            redis.rpush('input_ids', u_id)
            print('########u_choice',u_choice)

            # change state to find if all the votes are in
            if int(redis.llen('inputs')) == int(redis.get('total_players')):
                # append the most populat instruction to the list
                new_inst = count_votes(redis.lrange('inputs',0,-1),\
                                       redis.lrange('choices',0,-1))
                redis.rpush('instructions',new_inst)
                print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$4')
                redis.delete('inputs')
                redis.delete('input_ids')
                redis.delete('choices')
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
            print('$$$$$$$$$$$$$$$$$votes$$$$$$44',votes)
            counter = Counter(votes)
            winner = counter.most_common()[0][0]
            print('$$$$$$$$$$$$$$$$$winner$$$$$$44',winner,winner == 'no')
            redis.set('state','find' if winner == 'no' else 'finish')
            redis.delete('inputs')
            redis.delete('input_ids')

        return jsonify(result='finish vote received, thank you')
    else:
        return jsonify(result='this shouldnt be here')

@app.route('/updates')
def send_updates():
    #all updates require these
    state = redis.get('state')
    instructions = redis.lrange('instructions',0,-1)
    leader  = redis.get('leader')
    print("##### updates #####")
    print('state',state)
    print('instructions',instructions)
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
        # vote_list = '\n'.join(redis.lrange('choices',0,-1))
        vote_list = (redis.lrange('choices',0,-1))
        print('vote list',vote_list)
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

