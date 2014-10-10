from flask import Flask, render_template, request, jsonify, session
from redis import Redis
import os


# Initialize the Flask application
app = Flask(__name__)
redis = Redis()
total_players = 0

app.secret_key = '#d\xe9X\x00\xbe~Uq\xebX\xae\x81\x1fs\t\xb4\x99\xa3\x87\xe6.\xd1_'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_id')
def get_id():
    #total_players += 1
    return jsonify(result=1)

@app.route('/instruction_input')
def get_input():
    u_instruct = request.args.get('u_instruct', 0)
    
    #writ/e the result to the instructions
    with open("instructions.txt",'a') as f:
        print(u_instruct)
        f.write(str(curr_instruct)+ ". "+u_instruct+"\n")

    return jsonify(result="recieve input "+u_instruct+" thank you!")

@app.route('/propose_instruct')
def propose_instruct():
    print('proposing instruct')
    return jsonift(result="test")

@app.route('/vote_input')
def send_choices():
    with open("choices.txt",'r') as f:
        x = f.read()
        return jsonify(result=x.strip())

@app.route('/get_instructions')
def get_instructions():
    with open("instructions.txt",'r') as f:
        x = f.read()
        return jsonify(result=x.strip())


if __name__ == '__main__':
    '''
    with open('instructions.txt','w') as f:
        f.write("")
    '''
    global total_players
    total_players = 0
    curr_instruct = 1
    #total_players = 0
    #leader = None
    print('rolling')
    app.debug=True
    app.run()

