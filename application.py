from flask import Flask
# import sys
# sys.path.append('/helpers/')

import helpers.indicators
import helpers.strategy

application = Flask(__name__)

@application.route('/')
def hello_SBB():
    return helpers.strategy.runStrategy()