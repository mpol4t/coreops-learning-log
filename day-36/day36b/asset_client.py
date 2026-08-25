import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import argparse
import sys


def fetch_asset(url, token):
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
        },
    )

    try:
        with urlopen(request, timeout=3) as response:
            status = response.status

            if 200 <= status < 300:
                if response.headers.get_content_type() == "application/json":
                    body = response.read().decode("utf-8")

                    try:
                        data = json.loads(body)
                    except json.JSONDecodeError:
                        print("JSON parse FAIL", file=sys.stderr)
                        sys.exit(1)

                    if isinstance(data, dict):
                        if "asset_id" in data:
                            if not isinstance(data["asset_id"], str):
                                print("asset_id string olmali!", file=sys.stderr)
                                sys.exit(1)
                        else:
                            print("asset_id eksik!", file=sys.stderr)
                            sys.exit(1)

                        if "hostname" in data:
                            if not isinstance(data["hostname"], str):
                                print("hostname string olmali!", file=sys.stderr)
                                sys.exit(1)
                        else:
                            print("hostname eksik!", file=sys.stderr)
                            sys.exit(1)

                    else:
                        print("JSON root object olmali!", file=sys.stderr)
                        sys.exit(1)

                else:
                    print("Content-Type JSON degil!", file=sys.stderr)
                    sys.exit(1)

                print(f"status={status}")
                print(f"asset_id={data['asset_id']}")
                print(f"hostname={data['hostname']}")

    except HTTPError as e:
        print(f"HTTP error: {e.code} {e.reason}", file=sys.stderr)
        sys.exit(1)

    except URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("token")
    args = parser.parse_args()

    fetch_asset(args.url, args.token)
    return 0


if __name__ == "__main__":
    sys.exit(main())
