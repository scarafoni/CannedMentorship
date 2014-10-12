from flask import Flask, render_template, request, jsonify
from redis import Redis


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

#returns a list
def get_people_so_far():
    with open('data/people_so_far.txt', 'r') as f:
        x = f.read()
        x = x.split('\n')
        return trim_null(x)

def reset_people_so_far():
    with open('data/people_so_far.txt', 'w') as f:
        f.write('')
    
def add_client_input(id, input):
    with open('data/people_so_far.txt', 'a') as f,\
         open('data/user_inputs.txt', 'a') as f1:
        f.write(id+'\n') 
        f1.write(input+'\n')

#takes a list as input
def count_votes(votes):
    i = votes.index(max(votes))
    user_inputs = get_suggestions()
    most_popular = user_inputs[i] 
    write_instruction(most_popular)

def get_suggestions():
    with open('data/user_inputs.txt','r') as f:
        x = f.read().split('\n')
        return trim_null(x)

def get_instructions():
    with open('data/instructions.txt') as f:
        return f.read().strip()

def write_instruction(new_inst):
    with  open('data/instructions.txt','a') as f:
        f.write(new_inst+'\n')

# placeholder for the ai program
# takes in a list of strings
def do_ai(props):
    with open('data/choices.txt', 'w') as f:
        f.write(props[0])

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_id')
def get_id():
    add_player()
    x = get_total_players()
    return jsonify(result=x)


@app.route('/send_my_inst')
def get_input():
    u_instruct = request.args.get('u_instruct', 0)
    u_id = request.args.get('u_id', 1)
    # print(u_instruct,u_id) 
    # the the current instruction to far
    people_so_far = get_people_so_far()

    # writ/e the result to the list of proposals
    print('people so far-',people_so_far)
    if not u_id in people_so_far:
        add_client_input(u_id, u_instruct)
        return jsonify(result="recieve input "+u_instruct+" thank you!")

    else:
        return jsonify(result="you have already submitted an instruction")


@app.route('/propose_instruct')
def propose_instruct():
    with open('data/state.txt','w') as f:
        f.write('write')
        return jsonify(result="ok lets write an instruction!")

@app.route('/send_my_vote')
def send_my_vote():
    u_choice = request.args.get('u_choice', 0)
    u_id = request.args.get('u_id', 1)
    
    # add the vote if it's not in already
    proposers = get_people_so_far()
    if not u_id in proposers:
        add_client_input(u_id, u_choice)
        return jsonify(result="your vote for "+u_choice+" has been logged")
    else:
        return jsonify(result="you cannot vote twice")
            

@app.route('/updates')
def send_updates():
    #obligated to send  
        # vote choices
        # instructions
        # state
        # leader

    instructions = get_instructions()
    leader = get_leader()
    state = get_state()
    # print the current info
    print('updates- \n\tstate- '+state+'\n\ttotalp- '+str(get_total_players()))
    
    #if we're in find, we need to send the instructions
    if state == 'find':
        return jsonify(instructions=instructions,\
                   leader=leader,\
                   state=state)
        

    #check if all the writings are in
        # if yes run the collate algorithm and switch to voting
    elif state == "write":
        tp = get_total_players()
        suggesters_so_far = get_people_so_far()
        suggestions_so_far = get_suggestions()
        if len(suggesters_so_far) == tp:
            # voting algorithm result is done here
            do_ai(suggestions_so_far)
            # wipe the people who have proposed
            reset_people_so_far()
            set_state('vote')
        return jsonify(choices='',\
                   instructions=instructions,\
                   leader=leader,\
                   state=state)

    #check of all the votes are in
        #if yes run the counting algorithm
    elif state == "vote":
        vote_list = get_suggestions()
        print('vote list',vote_list)
        tp = get_total_players()
        voters_so_far = get_people_so_far()
        # if everyone's checked in then tally the votes
        if len(voters_so_far) == tp:
            count_votes(vote_list)
            reset_people_so_far()
            set_state('find')
        return jsonify(instructions=instructions,\
                       choices=vote_list,\
                       leader=leader,\
                       state=state)

    else:
        print('ERROR')
        return jsonify(state="err")



if __name__ == '__main__':
    # initialize everything
         # the instruction list being made
    with open('data/instructions.txt', 'w') as instructions,\
         open('data/total_players.txt', 'w') as total_players,\
         open('data/choices.txt', 'w') as choices,\
         open('data/user_inputs.txt', 'w') as user_inputs,\
         open('data/state.txt','w') as state,\
         open('data/people_so_far.txt','w') as people_so_far,\
         open('data/leader.txt', 'w') as leader:
            total_players.write('0')
            user_inputs.write('')
            # instructions.write('get a girlfriend\nkiss her\n rule the world')
            instructions.write('')
            leader.write('1')
            state.write('find')
            people_so_far.write('')
            # choices.write('talk about video games \n eat stuff')
            choices.write('')

    app.debug = True
    app.run()

