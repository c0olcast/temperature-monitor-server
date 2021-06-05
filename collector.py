#
#
#
import config
import serial
import json
import redis
import common
from datetime import datetime

import os
import sys
import getopt
import logging

def show_help():
    pass

# Main process
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

    logging.info(f"Starting serial communications [device: {config.comm_port}] [baud: {config.comm_baud}]")
    with serial.Serial(port=config.comm_port, baudrate=config.comm_baud, timeout=10) as ser:
        logging.info(f"Serial communications started")
        while True:
            line = ser.readline()
            logging.debug(f"New sensors packet: {line}")
            sensors = json.loads(line)
            sensors_hash = {"temp-monitor:sensor:" + sensor["sensor_id"]: sensor for sensor in sensors}
            logging.debug(f"Sending new sensor packet to Redis")
            with redis.Redis(host=config.redis_host, port=config.redis_port, db=0).pipeline() as pipe:
                logging.debug(f"Connecting to Redis server: [host {config.redis_host}] [port: {config.redis_port}]")
                right_now = datetime.now().__str__()
                for sensor_id, sensor in sensors_hash.items():
                    sensor["last_update"] = right_now
                    pipe.hset(name=sensor_id, key=None, value=None, mapping=sensor)
                pipe.execute()
            logging.debug("Done sending sensor packet to Redis")


if __name__ == '__main__':
    script_root = os.path.dirname(os.path.realpath(__file__))
    os.chdir(script_root)
    main(sys.argv[1:])
