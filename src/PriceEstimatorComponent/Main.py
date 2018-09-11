import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Program to predict lands prices.')
    parser.add_argument('--database', help='Database name.')
    parser.add_argument('--server', help='Server address.')
    parser.add_argument('--du', help='Database user name.')
    parser.add_argument('--connection_string', help='Connection string')
    parser.add_argument('--save', help='Save counted values into the database.',
                        action='store_true')
    return parser.parse_args()


def main():
    args = parse_args()
    if args.connection_string is None\
            and (args.database is None or args.server is None or args.du is None):
        print('ERROR')
    print(args)


if __name__ == '__main__':
    main()
