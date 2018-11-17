from os import getcwd
from argparse import ArgumentParser

from tas.web.servers import TextAnalysisServiceServer


def run(args):
    configuration_path = getcwd()

    tas_server = TextAnalysisServiceServer(configuration_path)

    tas_server.run()


def get_arguments():
    parser = ArgumentParser(description="Text analysis service cli tool")

    subparsers = parser.add_subparsers()

    run_parser = subparsers.add_parser("server", help="Start the tas server")
    run_parser.set_defaults(func=run)

    return parser.parse_args()


def main():
    args = get_arguments()

    args.func(args)
