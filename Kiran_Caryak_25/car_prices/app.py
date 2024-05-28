from flask import Flask, request, abort, Response
import requests
from car_prices.ipc_socket import Server
from datetime import datetime


# from logging.config import dictConfig


# dictConfig({
#     'version': 1,
#     'formatters': {'default': {
#         'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
#     }},
#     'handlers': {'wsgi': {
#         'class': 'logging.StreamHandler',
#         'stream': 'ext://flask.logging.wsgi_errors_stream',
#         'formatter': 'default'
#     }},
#     'root': {
#         'level': 'DEBUG',
#         'handlers': ['wsgi']
#     }
# })


app = Flask(__name__)


@app.get("/")
def homepage():
    return 'Nothing to see here.'


job_result_buffer_size = 2**20
job_timeout_in_seconds = 600


@app.post('/schedule.json')
def schedule_job():
    socket_dir = f'./sockets'
    data = b''

    with Server(socket_dir=socket_dir) as server:
        job_response = requests.post(
            url='http://localhost:6800/schedule.json',
            params={'socket_file': server.address} | {key: value for key, value in request.form.items()},
        )

        if job_response.json()['status'] != 'ok':
            abort(500)

        start_time = datetime.utcnow()

        with server.accept(job_timeout_in_seconds) as conn:
            time_left = job_timeout_in_seconds - (datetime.utcnow() - start_time).total_seconds()

            if time_left > 0:
                data = conn.recv(time_left)

            else:
                raise TimeoutError

    return Response(response=data, mimetype='application/json')
