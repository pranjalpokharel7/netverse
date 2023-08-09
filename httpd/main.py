import logging
import socket
from concurrent import futures
from contextlib import ExitStack, contextmanager

from constants import (
    HOST,
    HTTP_ENCODED_HEADER_200_OK,
    HTTP_ENCODED_HEADER_404_NOT_FOUND,
    HTTP_GET,
    INDEX_PAGE,
    NOT_FOUND_PAGE,
    PORT,
    SRC_DIR,
    WORKER_THREADS,
)

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s %(levelname)s::%(message)s"
)


@contextmanager
def create_tcp_socket_server(host, port):
    try:
        _socket = socket.socket(
            family=socket.AF_INET, type=socket.SOCK_STREAM
        )
        _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # bind socket to host and port
        _socket.bind((host, port))
        logging.info(f"Binding socket to {HOST}:{PORT}")

        _socket.listen(1)
        yield _socket

    except Exception as e:
        logging.error(f"Error in create_tcp_socket: {e}")
        raise e

    finally:
        _socket.close()


def process_client_connection(client_conn):
    with ExitStack() as stack:
        # defer connection close to the exit of with block
        stack.callback(client_conn.close)

        # receive client request
        request = client_conn.recv(1024).decode()
        logging.info(f"Received request: {request}")

        request_headers = request.split("\n")
        request_line_args = request_headers[0].split()
        http_method = request_line_args[0]

        # only accept GET requests for now
        if http_method != HTTP_GET:
            return

        request_filename = request_line_args[1]

        if request_filename == "/":
            # requested file is either the index.html page
            request_filename = INDEX_PAGE
        else:
            # or an html file inside the source directory
            request_filename = SRC_DIR + request_filename

        contents = ""
        try:
            with open(request_filename, "rb") as f:
                contents = f.read()
        except FileNotFoundError:
            with open(NOT_FOUND_PAGE, "rb") as f:
                contents = f.read()
            client_conn.sendall(
                HTTP_ENCODED_HEADER_404_NOT_FOUND + contents
            )
            return

        # encode string to bytes and send to client connection
        client_conn.sendall(HTTP_ENCODED_HEADER_200_OK + contents)


def run_httpd():
    with create_tcp_socket_server(HOST, PORT) as http_socket:
        with futures.ThreadPoolExecutor(
            max_workers=WORKER_THREADS
        ) as executer:
            while True:
                client_conn, _ = http_socket.accept()
                executer.submit(
                    process_client_connection,
                    client_conn,
                )


if __name__ == "__main__":
    run_httpd()
