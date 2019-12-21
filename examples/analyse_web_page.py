from argparse import ArgumentParser
import json
from urllib.parse import urljoin

import requests


def get_arguments():
    parser = ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--output", default="result.json")
    parser.add_argument("--tas-address", default="http://192.168.1.103:8020")

    return parser.parse_args()


def main():
    args = get_arguments()

    page_response = requests.get(args.url, timeout=10)
    page_response.raise_for_status()

    tas_process_url = urljoin(args.tas_address, "api/v1/process")
    tas_response = requests.post(
        tas_process_url,
        timeout=10,
        json={
            "content_type": "html",
            "content": {
                "url": args.url,
                "headers": dict(page_response.headers),
                "html": page_response.text
            }
        }
    )

    tas_response.raise_for_status()

    with open(args.output, "w") as f:
        json.dump(tas_response.json(), f)


if __name__ == "__main__":
    main()
