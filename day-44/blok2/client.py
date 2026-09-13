import argparse
import json
import sys

from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin


def fetch_json(url):
    request = Request(
        url,
        headers={
            "Accept": "application/json",
        },
    )

    try:
        with urlopen(request, timeout=3) as response:
            if response.headers.get_content_type() != "application/json":
                raise ValueError("Content-Type JSON degil!")

            body = response.read().decode("utf-8")

    except HTTPError as e:
        raise RuntimeError(
            f"HTTP error: {e.code} {e.reason}"
        ) from e

    except URLError as e:
        raise RuntimeError(
            f"Network error: {e.reason}"
        ) from e

    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        raise ValueError("JSON parse FAIL") from e

    if not isinstance(data, dict):
        raise ValueError("JSON root object olmali!")

    return data


def iter_assets(start_url):
    current_url = start_url

    while current_url is not None:
        response = fetch_json(current_url)

        if "items" not in response:
            raise ValueError("items eksik!")

        if not isinstance(response["items"], list):
            raise ValueError("items list olmali!")

        if "next" not in response:
            raise ValueError("next eksik!")

        next_value = response["next"]

        if next_value is not None and not isinstance(next_value, str):
            raise ValueError("next string veya None olmali!")

        for item in response["items"]:
            yield item

        if next_value is None:
            current_url = None
        else:
            current_url = urljoin(current_url, next_value)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    args = parser.parse_args()

    try:
        for asset in iter_assets(args.url):
            print(asset["hostname"])
    except (ValueError, RuntimeError) as e:
        print(str(e), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
