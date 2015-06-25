from flask import Flask
application = Flask(__name__)

@application.route('/')
def hello():
    return "<b>Hello, world!</b>"

if __name__ == "__main__":
    application.run(host="0.0.0.0")

