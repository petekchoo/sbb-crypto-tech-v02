from flask import Flask
from helpers.strategy import runStrategy
import helpers.indicators

application = Flask(__name__)

@application.route('/')
def hello_SBB():
    return 'working on it!'