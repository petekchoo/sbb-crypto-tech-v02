from flask import Flask
# import sys
# sys.path.append('/helpers/')

import indicators
import strategy

application = Flask(__name__)

@application.route('/')
def hello_SBB():
    return strategy.runStrategy()