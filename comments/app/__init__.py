from flask import Flask

app = Flask(__name__)

@app.route('/api/resource2')
def resource2():
    return "Hello from Service 2, Resource 2!"