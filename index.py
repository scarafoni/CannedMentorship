from flask import Flask, render_template, request, jsonify
import os

# Initialize the Flask application
app = Flask(__name__)


# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    return render_template('index.html')

# Route that will process the AJAX request, sum up two
# integer numbers (defaulted to zero) and return the
# result as a proper JSON response (Content-Type, etc.)
curr_instruct = 1
@app.route('/instruction_input')
def get_input():
    u_instruct = request.args.get('u_instruct', 0)
    
    #writ/e the result to the instructions
    with open("instructions.txt",'a') as f:
        print(u_instruct)
        f.write(str(curr_instruct)+". "+u_instruct+"\n")

    return jsonify(result="recieve input "+u_instruct+" thank you!")

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
    curr_instruct = 1
    app.run()

