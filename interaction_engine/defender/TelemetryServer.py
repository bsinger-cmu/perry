# Simple server for receiving telemetry data
from flask import Flask
from flask import request

app = Flask(__name__)
port = 5000

@app.route("/alert", methods = ['POST', 'GET'])
def handle_alert():
    data = request.form
    honey_type = data['type']
    service_type = data['protocol']

    # ToDo send this to defender

    return "Received!"


if __name__ == '__main__':
    app.run(host="localhost", port=port)

