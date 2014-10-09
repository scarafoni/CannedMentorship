# In this example we are going to create a simple HTML
# page with 2 input fields (numbers), and a link.
# Using jQuery we are going to send the content of both
# fields to a route on our application, which will
# sum up both numbers and return the result.
# Again using jQuery we'l show the result on the page


# We'll render HTML templates and access data sent by GET
# using the request object from flask. jsonigy is required
# to send JSON as a response of a request
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
def add_numbers():
    u_instruct = request.args.get('u_instruct', 0)
    
    #writ/e the result to the instructions
    with open("instructions.txt",'a') as f:
        print(u_instruct)
        f.write(str(curr_instruct)+". "+u_instruct+"\n")

    return jsonify(result="recieve input "+u_instruct+" thank you!")

if __name__ == '__main__':
    with open('instructions.txt','w') as f:
        f.write("current instructions\n")
    curr_instruct = 1
    app.run()

