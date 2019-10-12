import argparse
import ast
import json
import logging
import socketserver
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler
from typing import Any, Dict

from inspectortiger.inspector import Inspector
from inspectortiger.inspects import _obtain, start_core_session

logger = logging.getLogger("inspectortiger.server")


class Server(BaseHTTPRequestHandler):
    def do_POST(self, *args, **kwargs):
        content_length = int(self.headers.get("Content-Length", "-1"))
        body = self.rfile.read(content_length)
        try:
            body = json.loads(body.decode())
        except json.JSONDecodeError:
            logger.exception("Couldn't parse body")
            return self.fail("Request body should be JSON!")

        source = body.get("source")
        if source is None:
            return self.fail("Request body should contain a source field!")

        try:
            source = ast.parse(source)
        except (SyntaxError, TypeError) as exc:
            logger.exception("Couldn't parse source")
            return self.respond(
                status="fail",
                message=f"Couldn't parse the source code. {exc!r}",
            )

        start_core_session()
        inspector = Inspector(source)
        reports = inspector.handle()
        return self.respond(status="success", result=_obtain((), reports))

    def respond(self, code=200, **data):
        self.send_response(code)
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def fail(self, message, code=400):
        self.respond(code=code, status="fail", message=message)


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="inspectortiger.server | Inspector Tiger Web API"
    )

    parser.add_argument(
        "-H", "--host", help="Server host", default="0.0.0.0", type=str
    )
    parser.add_argument(
        "-P", "--port", help="Server port", default=8000, type=int
    )
    parser.add_argument(
        "-T",
        "--threaded",
        help="Run server in threaded mode",
        action="store_true",
        default=False,
    )

    server = parser.parse_args()
    if server.threaded:
        runner = ThreadedTCPServer
    else:
        runner = socketserver.TCPServer
    with runner((server.host, server.port), Server) as httpd:
        logger.info("Starting server at %s:%s", *httpd.server_address)
        httpd.serve_forever()
