import argparse
import logging

from src.PriceEstimatorComponent.Utils.logger import create_loggers_helper


def create_logger():
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    return create_loggers_helper(_logger)


logger = create_logger()


def parse_args():
    parser = argparse.ArgumentParser(description='Program to predict lands prices.')
    parser.add_argument('--database', help='Database name.')
    parser.add_argument('--server', help='Server address.')
    parser.add_argument('--database_user', help='Database user name.')
    parser.add_argument('--connection_string', help='Connection string')
    parser.add_argument('--save', help='Save counted values into the database.',
                        action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()
    # Not ending the program because model may be serialized
    if args.connection_string is None \
            and (args.database is None or args.server is None or args.database_user is None):
        logger.warning('Unable to connect to database.')
        

if __name__ == '__main__':
    main()
