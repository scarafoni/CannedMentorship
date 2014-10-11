from flask import Flask, render_template, request, jsonify
from redis import Redis

# Initialize the Flask application
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_id')
def get_id():
    f = open('data/total_players.txt', 'r')
    x = int(''.join(f.read().split()))
    x += 1
    print(x)
    f.close()
    f = open('data/total_players.txt', 'w')
    f.write(str(x))
    f.close()
    return jsonify(result=x)


@app.route('/instruction_input')
def get_input():
    u_instruct = request.args.get('u_instruct', 0)
    # writ/e the result to the instructions
    with open("data/instructions.txt", 'a') as f:
        f.write(str(u_instruct) + ". " + u_instruct + "\n")

    return jsonify(result="recieve input "+u_instruct+" thank you!")


@app.route('/propose_instruct')
def propose_instruct():
    state = ''
    with open('data/state.txt','r') as f:
        state = f.read()
    if state != 'find':
        return jsonify(result="n")
    else:
        with open('data/state.txt','w') as f:
            f.write('getprops')
            return jsonify(result="y")


@app.route('/updates')
def send_choices():
    with open("data/choices.txt", 'r') as f_choice,\
         open('data/leader.txt','r') as f_lead,\
         open('data/state.txt','r') as f_state,\
         open('data/instructions.txt','r') as f_inst:
        choices = f_choice.read().strip()
        inst = f_inst.read().strip()
        leader = f_lead.read().rstrip()
        state = f_state.read().rstrip()
        return jsonify(choices=choices,instructions=inst,leader=leader,state=state)


if __name__ == '__main__':
    # initialize everything
    with open('data/instructions.txt', 'w') as instructions,\
         open('data/total_players.txt', 'w') as total_players,\
         open('data/choices.txt', 'w') as choices,\
         open('data/propositions.txt', 'w') as propositions,\
         open('data/state.txt','w') as state,\
         open('data/leader.txt', 'w') as leader:
            total_players.write('0')
            propositions.write('')
            instructions.write('get a girlfriend\nkiss her\n rule the world')
            leader.write('1')
            state.write('find')
            choices.write('talk about video games \n eat stuff')

    app.debug = True
    app.run()

