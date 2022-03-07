from flask import Flask
# import sys
# sys.path.append('/helpers/')

import indicators

application = Flask(__name__)

@application.route('/')
def hello_SBB():
    return "Hello!"