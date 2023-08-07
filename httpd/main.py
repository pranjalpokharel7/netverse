import logging
import socket
from contextlib import contextmanager

from constants import (
    HOST,
    HTTP_ENCODED_HEADER_200_OK,
    HTTP_ENCODED_HEADER_404_NOT_FOUND,
    HTTP_GET,
    INDEX_PAGE,
    NOT_FOUND_PAGE,
    PORT,
    SRC_DIR,
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

        yield _socket

    except Exception as e:
        logging.error(f"Error in create_tcp_socket: {e}")
        raise e

    finally:
        _socket.close()


@contextmanager
def create_client_connection(_socket):
    conn = None
    try:
        conn, addr = http_socket.accept()
        logging.info(f"Connected to client: {addr}")

        yield conn

    except Exception as e:
        logging.error(f"Error in create_client_connection")

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    with create_tcp_socket_server(HOST, PORT) as http_socket:
        http_socket.listen(1)

        while True:
            with create_client_connection(http_socket) as client_conn:
                # receive client request
                request = client_conn.recv(1024).decode()
                logging.info(request)

                request_headers = request.split("\n")
                request_line_args = request_headers[0].split()
                http_method = request_line_args[0]

                # only accept GET requests for now
                if http_method != HTTP_GET:
                    continue

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
                    continue

                # encode string to bytes and send to client connection
                client_conn.sendall(
                    HTTP_ENCODED_HEADER_200_OK + contents
                )
