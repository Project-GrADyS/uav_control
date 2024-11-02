import logging

def set_log_config(args):
    logging_config = {
        'version': 1,
        'formatters': {
            'console_formatter': {
                'format': f'[%(name)s-{args.sysid}] %(levelname)s - %(message)s'
            },
            'file_formatter': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        },
        'handlers': {
            'console_handler': {
                'class': 'logging.StreamHandler',
                'formatter': 'console_formatter'
            },
            'file_handler': {
                'class': 'logging.FileHandler',
                'filename': args.log_path,
                'formatter': 'file_formatter'
            }
        },
        'loggers': {
            'COPTER': {
                'level': 'INFO',
                'handlers': ['console_handler', 'file_handler']
            },
            'PROTOCOL': {
                'level': 'INFO',
                'handlers': ['console_handler', 'file_handler']
            }
        }
    }

    for name in logging_config["loggers"].keys():
        handlers = []

        if args.debug:
            logging_config["loggers"]["name"]["level"] = "DEBUG"

        if args.log_path != "":
            handlers.append("file_handler")
        
        if name in args.log_console:
            handlers.append("console_handler")

        logging_config["loggers"][name]["handlers"] = handlers

    logging.config.dictConfig(logging_config)