import ast
import json
from http.server import BaseHTTPRequestHandler

from it.inspector import Inspector
from it.session import Session
from it.utils import Group, logger


class InspectorServer(BaseHTTPRequestHandler):
    def do_GET(self, *args, **kwargs):
        self.respond(200, message="use post method")

    def do_POST(self, *args, **kwargs):
        content_length = int(self.headers.get("Content-Length", "-1"))
        body = self.rfile.read(content_length)
        logger.info("Got this: {}")
        try:
            body = json.loads(body.decode())
        except json.JSONDecodeError:
            logger.exception("Couldn't parse body")
            return self.fail("Request body should be JSON!")

        source = body.get("source")
        if source is None:
            logger.exception("Missing body item")
            return self.fail("Request body should contain a source field!")

        try:
            source = ast.parse(source)
        except (SyntaxError, TypeError) as exc:
            logger.exception("Couldn't parse source")
            return self.fail(
                message=f"Couldn't parse the source code. {exc!r}"
            )

        session = Session()
        session.start()

        inspection = session.single_inspection(source)
        return self.respond(
            status="success",
            result=dict(session.group_by(inspection, group=Group.LINENO)),
        )

    def _respond(self, code):
        self.send_response(code)
        self.end_headers()

    def respond(self, code=200, **data):
        self._respond(code)
        self.wfile.write(json.dumps(data).encode())

    def fail(self, message, code=400):
        self.respond(code=code, status="fail", message=message)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET")
        self.send_header(
            "Cache-Control", "no-store, no-cache, must-revalidate"
        )
        return super().end_headers()
