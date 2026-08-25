from http.server import BaseHTTPRequestHandler, HTTPServer
import json


TOKEN = "Bearer coreops-demo-token"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/assets", "/broken"):
            self.send_error(404)
            return

        if self.headers.get("Authorization") != TOKEN:
            self.send_error(401)
            return

        if self.path == "/broken":
            body = b'{"asset_id":'
        else:
            body = json.dumps(
                {"asset_id": "asset-01", "hostname": "lab.local"}
            ).encode()

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


HTTPServer(("127.0.0.1", 18081), Handler).serve_forever()