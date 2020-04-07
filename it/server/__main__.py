import argparse
import socketserver

from it.server import InspectorServer
from it.utils import logger, prepare_logger


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="it.server | Inspector Tiger Web API"
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
    prepare_logger()
    if server.threaded:
        runner = ThreadedTCPServer
    else:
        runner = socketserver.TCPServer
    with runner((server.host, server.port), InspectorServer) as httpd:
        logger.info("Starting server at %s:%s", *httpd.server_address)
        httpd.serve_forever()
