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
    f = open('/datatotal_players.txt', 'w')
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
    return jsonify(result="test")


@app.route('/vote_input')
def send_choices():
    with open("data/choices.txt", 'r') as f:
        x = f.read()
        return jsonify(result=x.strip())


@app.route('/get_instructions')
def get_instructions():
    with open("data/instructions.txt", 'r') as f:
        x = f.read()
        return jsonify(result=x)


if __name__ == '__main__':
    # initialize everything
    with open('instructions.txt', 'w') as instructions,\
         open('total_players.txt', 'w') as total_players,\
         open('choices.txt', 'w') as choices,\
         open('propositions.txt', 'w') as propositions\
         open('leader.txt', 'w') as leader:
            total_players.write('0')
            propositions.write('')
            instructions.write('')
            leader.write('0')
            choices.write('')

    app.debug = True
    app.run()

