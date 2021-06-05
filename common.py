import os
import logging
import logging.config
import yaml

def setup_logging(log_config='logging.yaml', log_level=logging.INFO, log_file=None):
    if os.path.exists(log_config):
        with open(log_config, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                if log_file != None:
                    config["file_handler"]["filename"] = log_file
                logging.config.dictConfig(config)
                logging.getLogger().setLevel(log_level)
            except Exception as e:
                print(e)
                print('Error in Logging Configuration. Using default configs')
                logging.basicConfig(level=log_level)
    else:
        logging.basicConfig(level)
        print('Failed to load configuration file. Using default configs')
