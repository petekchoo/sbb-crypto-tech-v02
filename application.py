from flask import Flask
application = Flask(__name__)

@application.route('/')
def hello_SBB():
    return 'Welcome to SBB crypto tech trading'