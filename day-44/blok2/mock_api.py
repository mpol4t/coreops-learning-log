import json

from http.server import BaseHTTPRequestHandler, HTTPServer


request_count = 0


class MockAPIHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        global request_count

        request_count += 1

        print(f"request #{request_count} -> {self.path}")

        if request_count > 2:
            self.send_json(
                500,
                {
                    "error": "unexpected third request"
                }
            )
            return

        if self.path == "/assets?page=1":
            data = {
                "items": [
                    {
                        "hostname": "api-01.local"
                    },
                    {
                        "hostname": "db-01.local"
                    },
                ],
                "next": "/assets?page=2",
            }

            self.send_json(200, data)
            return

        if self.path == "/assets?page=2":
            data = {
                "items": [
                    {
                        "hostname": "cache-01.local"
                    }
                ],
                "next": None,
            }

            self.send_json(200, data)
            return

        self.send_json(
            404,
            {
                "error": "not found"
            }
        )

    def send_json(self, status, data):
        body = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


server = HTTPServer(
    ("127.0.0.1", 18081),
    MockAPIHandler,
)

print("Mock API running:")
print("http://127.0.0.1:18081")
print()

server.serve_forever()