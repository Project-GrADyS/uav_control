from argparse import ArgumentParser, ArgumentTypeError
import configparser

def parse_config_file(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    print(config.sections())

def parse_args():
    parser = ArgumentParser(description="Welcome to the UAV Runner, this script runs an API that interfaces with Ardupilots instances (real or simulated).")
    parse_mode(parser)
    parse_api(parser)
    parse_logs(parser)
    partial_args, _ = parser.parse_known_args()
    if partial_args.simulated:
        parse_simulated(parser)
    if partial_args.protocol:
        parse_protocol(parser)
    args = parser.parse_args()

    if args.config:
        #parse_config_file(args.config)
        config = configparser.ConfigParser()
        config.read(args.config)
        for section in config.sections():
            for key, value in config.items(section):
                if hasattr(args, key):
                    setattr(args, key, value)
                else:
                    print(f"Warning: {key} not found in args")
        print(config.sections())
    return args
    
# MODE PARSER
def parse_mode(mode_parser):

    mode_parser.add_argument(
        '--simulated',
        dest='simulated',
        type=bool,
        default=False,
        help="Wheter to simulate copter using Ardupilot's SITL or not"
    )

    mode_parser.add_argument(
        '--protocol',
        dest='protocol',
        type=bool,
        default=False,
        help="Wheter to start Protocol process for autonomous flight or not"
    )

    mode_parser.add_argument(
        '--config',
        dest='config',
        default=None,
        help="Configuration file for UAV execution"
    )

# API PARSER
def parse_api(api_parser):

    api_parser.add_argument(
        '--port',
        dest='port',
        type=int,
        default=8000,
        help='Port for api to run on'
    )

    api_parser.add_argument(
        '--uav_connection',
        dest='uav_connection',
        default='127.0.0.1:17171',
        help='Address used for copter connection'
    )

    api_parser.add_argument(
        '--connection_type',
        dest='connection_type',
        default='udpin',
        help="Connection type (client or server) for copter. Either udpin or udpout"
    )

    api_parser.add_argument(
        '--sysid',
        dest='sysid',
        type=int,
        default=10,
        help='Sysid for Copter'
    )

# SIMULATED PARSER
def parse_simulated(simulated_parser):

    simulated_parser.add_argument(
        '--location',
        dest='location',
        default="AbraDF",
        help="""Location name for UAV home. To register a new location name run the following command:
            bash scripts/registry_location [LOCATION_NAME] [GPS_LAT] [GPS_LONG] [GPS_ALT] [HEADING]
        """
    )

    simulated_parser.add_argument(
        '--gs_connection',
        dest='gs_connection',
        default=["172.26.176.1:15630", "172.31.16.1:15630", "172.23.192.1:15630"],
        help="Address for GroundStation connection",
        nargs='*'
    )

    simulated_parser.add_argument(
        '--speedup',
        dest='speedup',
        type=int,
        default=1,
        help="Multiplication factor for simulation time."
    )

    simulated_parser.add_argument(
        '--ardupilot_path',
        dest='ardupilot_path',
        default='~/gradys/ardupilot',
        help="Path for ardupilot repository"
    )

# PROTOCOL PARSER
def parse_protocol(protocol_parser):

    protocol_parser.add_argument(
        '--pos',
        dest='pos',
        default='[0,0,50]',
        help="Initial position of node in the protocol execution"
    )

    protocol_parser.add_argument(
        '--protocol_name',
        dest='protocol_name',
        default='',
        help='Uav Protocol to run'
    )

    protocol_parser.add_argument(
        '--collaborators',
        dest='collaborators',
        default=[],
        help='Uav collaborators api list. Format should be [<]',
        nargs='*'
    )

    protocol_parser.add_argument(
        '--communication_range',
        dest='communication_range',
        default=-1,
        help='Simulated communication range. -1 for no limit',
    )

def parse_logs(logs_parser):

    # Defines which values are accepted as a LOGGER input.
    def valid_loggers_type(value):
        valid_loggers = {'PROTOCOL', 'COPTER'}
        if not value in valid_loggers:
            raise ArgumentTypeError('Invalid value. Please choose one of the following: value1, value2, or both')
        return value
    
    logs_parser.add_argument(
        "--log_console",
        dest="log_console",
        default=[],
        type=valid_loggers_type,
        help="List of loggers to be handled in console. This loggers need to be a subset of: COPTER, PROTOCOL and API.",
        nargs='*'
    )

    logs_parser.add_argument(
        "--log_path",
        dest="log_path",
        default=None,
        help="If provided, saves log files to path. This log file will receive the logs from all loggers of that UAV. Which include: COPTER, PROTOCOL and API."
    )

    logs_parser.add_argument(
        "--debug",
        dest="debug",
        default=[],
        type=valid_loggers_type,
        help="Which loggers to apply debug level. Possible logger: COPTER, PROTOCOL and API."
    )