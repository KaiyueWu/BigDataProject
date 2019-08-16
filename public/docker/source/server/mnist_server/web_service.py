# -*- coding: utf-8 -*-
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from flask import Flask, request, send_file, make_response, json
from flask_cors import CORS, cross_origin

from mnist_server.predictor import predictor
from mnist_server.db_helper import db_helper

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024
CORS(app, supports_credentials=True)

logger = logging.getLogger('MnistServer')


@app.route("/")
def hello():
    return "Hello world!"


@app.route("/api/mnist/identify", methods=['POST'])
@cross_origin(supports_credentials=True)
def mnist_identify():
    params = json.loads(request.data)
    predict = predictor.predict(params['data'])
    db_helper.insert_data(params['data'], str(predict))
    return json.dumps({'predict': predict})


def _init_log(level):
    logger.setLevel(level=level)
    if not os.path.exists('./logs'):
        os.mkdir('./logs')
    rHandler = RotatingFileHandler("./logs/mnist_server.log", maxBytes=8 * 1024 * 1024, backupCount=3,
                                   encoding='utf-8')
    rHandler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    rHandler.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(formatter)

    logger.addHandler(rHandler)
    logger.addHandler(console)


def reset_db(db_address='127.0.0.1', port=9042):
    _init_log(logging.INFO)
    db_helper.init_db(address=db_address, port=int(port))
    db_helper.reset_db()


def init_db(db_address='127.0.0.1', port=9042):
    _init_log(logging.INFO)
    db_helper.init_db(address=db_address, port=int(port))
    db_helper.init_db()


def run(port=8888, db_address='127.0.0.1', db_port=9042, debug=False):
    port = int(sys.argv[1]) if len(sys.argv) > 1 else port
    db_address = sys.argv[2] if len(sys.argv) > 2 else db_address
    db_port = sys.argv[3] if len(sys.argv) > 3 else db_port

    _init_log(logging.INFO)
    logger.info("Run server port:{}, db address:{} port:{}".format(port, db_address, db_port))
    db_helper.init(address=db_address,port=int(db_port))
    logger.info("Web service starting run...")
    app.config['JSON_AS_ASCII'] = False
    app.run(port=int(port), debug=debug, use_reloader=False)


def stop():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    logger.info("Web service stop...")


if __name__ == "__main__":
    # db_helper.init()
    # # db_helper.reset_db()
    # db_helper.init_db()
    # db_helper.insert_data('sssss', '222')
    # res = db_helper.query_data()
    # for s in res:
    #     print(s)

    import os

    os.environ['FLASK_ENV'] = 'development'

    run(debug=True)
    stop()
