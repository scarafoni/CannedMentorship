from flask import Flask, render_template, request, jsonify
from redis import Redis

# Initialize the Flask application
def get_total_players():
    with open('data/total_players.txt', 'r') as f:
        return int(''.join(f.read().split()))

def set_state(state):
    with open('data/state.txt', 'w') as f:
        f.write(state)

def get_state(state):
    with open('data/state.txt', 'r') as f:
        return f.read()

#takes a list as input
def count_votes(votes):
    i = votes.index(max(votes))
    choice = ''
    with open('data.choices.txt','r') as f:
       choice = f.read().split('\n')[i] 
    write_instruction(choice)

def write_instruction(new_inst):
    print('write instruction')
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
    x = get_total_players()
    x += 1
    with open('data/total_players.txt', 'w') as f:
        f.write(str(x))
    return jsonify(result=x)


@app.route('/send_my_inst')
def get_input():
    u_instruct = request.args.get('u_instruct', 0)
    u_id = request.args.get('u_id', 1)
    # print(u_instruct,u_id) 
    # the the current instruction to far
    people_so_far = []
    with open('data/people_so_far.txt', 'r') as f:
        x = f.read()
        # print(x)
        people_so_far = x.split('\n')

    # writ/e the result to the list of proposals
    if not u_id in people_so_far:
        with open('data/people_so_far', 'a') as f,\
             open('data/propositions.txt', 'a') as f1:
            f.write(u_id) 
            f1.write(u_instruct)
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
    
    proposers = []
    with open('data/people_so_far.txt', 'r') as f:
        proposers = f.read().split('\n')

    if u_id not in proposers:
        with open('data/people_so_far.txt', 'a') as f:
            f.write(u_id+'\n')
        return jsonify(result="your vote for "+u_choice+" has been logged")
    else:
        return jsonify(result="you cannot vote twice")
            

@app.route('/updates')
def send_updates():
    choices = ''
    inst = ''
    leader = ''
    state = ''
    with open("data/propositions.txt", 'r') as f_props,\
         open('data/leader.txt','r') as f_lead,\
         open('data/state.txt','r') as f_state,\
         open('data/instructions.txt','r') as f_inst:
        props = f_props.read().strip()
        inst = f_inst.read().strip()
        leader = f_lead.read().rstrip()
        state = f_state.read().rstrip()

    # if we're in the writing stage and everyone's written a suggestion, change states
    print('state-',state,'totalp-',get_total_players(),'props-',props)
    if state == "write":
        tp = get_total_players()
        prop_list = props.split("\n")
        if not prop_list == [''] and len(prop_list) == tp:
            # voting algorithm result is done here
            do_ai(prop_list)
            # wipe the people who have proposed
            with open('data/people_so_far.txt', 'w') as f:
                f.write('')
            set_state('vote')

    # keep pushing the results if we're voting
    if state == "vote":
        with open('data/choices.txt','r') as f:
            x = f.read()
            # print('choices',x)
            # if we have all the votes, move to the first stage
            vote_list = []
            with open('data/people_so_far.txt', 'r') as f2:
                vote_list = f2.read().split('\n') 
            print(vote_list,get_total_players())
            if not vote_list == [''] and len(vote_list)-1 == get_total_players():
                count_votes(vote_list)
                with open('data/people_so_far.txt', 'w') as f3:
                    f3.write('')
                set_state('find')
                return jsonify(instructions=inst,\
                               leader=leader,\
                               state=state)

            return jsonify(choices=x,\
                       instructions=inst,\
                       leader=leader,\
                       state=state)

    return jsonify(instructions=inst,\
                   leader=leader,\
                   state=state)


if __name__ == '__main__':
    # initialize everything
    with open('data/instructions.txt', 'w') as instructions,\
         open('data/total_players.txt', 'w') as total_players,\
         open('data/choices.txt', 'w') as choices,\
         open('data/propositions.txt', 'w') as propositions,\
         open('data/state.txt','w') as state,\
         open('data/people_so_far.txt','w') as people_so_far,\
         open('data/leader.txt', 'w') as leader:
            total_players.write('0')
            propositions.write('')
            # instructions.write('get a girlfriend\nkiss her\n rule the world')
            instructions.write('')
            leader.write('1')
            state.write('find')
            people_so_far.write('')
            # choices.write('talk about video games \n eat stuff')
            choices.write('')

    app.debug = True
    app.run()

