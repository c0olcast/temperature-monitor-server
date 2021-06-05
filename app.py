import json

import config
import common
import os
import sys
import getopt
import logging

import redis

from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/v1/sensors", methods=['GET'])
def sensors():
    logging.debug("Request for sensors data")
    if request.method == 'GET':
        with redis.Redis(host=config.redis_host, port=config.redis_port, db=0) as redis_conn:
            logging.debug("Fetching sensor data from Redis")
            sensor_keys = redis_conn.keys("temp-monitor:sensor:*")
            sensor_keys.sort()
            ret_val_t = []
            for sensor_key in sensor_keys:
                ret_val_t.append(redis_conn.hgetall(sensor_key))
            ret_val = []
            for sensor in ret_val_t:
                ret_val.append({k.decode("UTF-8"): v.decode("UTF-8") for k, v in sensor.items()})
    return json.dumps(ret_val)

@app.route("/api/v1/sensors/<int:sensor_id>", methods=['GET'])
def sensor(sensor_id):
    logging.debug("Request for a sensor's data")
    if request.method == 'GET':
        with redis.Redis(host=config.redis_host, port=config.redis_port, db=0) as redis_conn:
            logging.debug("Fetching sensor data from Redis")
            ret_val_t = redis_conn.hgetall(f"temp-monitor:sensor:{sensor_id}")
            ret_val = {k.decode("UTF-8"): v.decode("UTF-8") for k, v in ret_val_t.items()}
    return json.dumps(ret_val)

def show_help():
    pass


def main(argv):
    args, values = getopt.getopt(argv, "hc:", ["help", "log_level=", "log_file=", "log_config="])

    log_level = logging.INFO
    log_config = "logging.yaml"
    log_file = None

    for option, value in args:
        if option == "-h" or option == "--help":
            show_help()
            exit(0)
        elif option == "--log_level":
            numeric_level = getattr(logging, value.upper(), None)
            if not isinstance(numeric_level, int):
                raise ValueError('Invalid log level: %s' % value.upper())
            log_level = numeric_level
        elif option == "--log_config" or option == "-c":
            log_config = value
        elif option == "--log_file":
            log_file = value

    # Setup logging
    common.setup_logging(log_config=log_config, log_level=log_level, log_file=log_file)

    # Start app
    app.run(debug=log_level >= logging.DEBUG, host="0.0.0.0")


if __name__ == '__main__':
    script_root = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_root)
    main(sys.argv[1:])
