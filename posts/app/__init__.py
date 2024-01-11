from flask import Flask

app = Flask(__name__)


@app.route('/api')
def resource2():
    return "Hello from Service 1, Resource 1!"
