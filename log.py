import logging
import os

def create_directory_if_not_exists(directory_name):
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

def set_log_config(args):

    log_config_logger = logging.getLogger("LOG_CONFIG")

    # Default log config
    logging_config = {
        'version': 1,
        'formatters': {
            'console_formatter': {
                'format': f"[%(name)s-{args.sysid}] %(levelname)s - %(message)s"
            },
            'file_formatter': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        },
        "handlers": {
            'console_handler': {
                'class': 'logging.StreamHandler',
                'formatter': 'console_formatter'
            },
            'file_handler': {
                'class': 'logging.FileHandler',
                'filename': f"./uav_logs/uav_{args.sysid}.log" if args.log_path == None else args.log_path,
                'formatter': 'file_formatter'
            }
        },
        'loggers': {
            'COPTER': {
                'level': 'INFO',
                'handlers': ['file_handler']
            },
            "uvicorn": {
                'level': 'INFO',
                'handlers': ['file_handler']
            },
            "uvicorn.access": {
                'level': 'INFO',
                'handlers': ['file_handler']
            },
            "uvicorn.error": {
                'level': 'INFO',
                'handlers': ['file_handler']
            },
            "API": {
                'level': 'INFO',
                'handlers': ['file_handler', 'console_handler']
            }
        }
    }

    for logger_name in args.log_console:
        if logger_name in logging_config["loggers"]:
            logging_config['loggers'][logger_name]['handlers'].append('console_handler')

    for logger_name in args.debug:
        if logger_name in logging_config["loggers"]:
            logging_config['loggers'][logger_name]['level'] = 'DEBUG'

    logging.config.dictConfig(logging_config)