# comments/routes.py
from comments import app

@app.route('/api/resource2')
def resource2():
    return "Hello from Service 2, Resource 2!"