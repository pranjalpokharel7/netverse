from dotenv import dotenv_values

config = dotenv_values(".env")

# environment variables
DEBUG = config.get("DEBUG")

# server threads
WORKER_THREADS = 10

# host and port
HOST = "0.0.0.0"
PORT = 3500 if DEBUG else 80

# response headers
HTTP_ENCODED_HEADER_200_OK = "HTTP/1.0 200 OK\n\n".encode()
HTTP_ENCODED_HEADER_404_NOT_FOUND = (
    "HTTP/1.0 404 NOT FOUND\n\n".encode()
)

# response messages
ECHO_RESPONSE = "Pong!"

# http methods
HTTP_GET = "GET"
HTTP_POST = "POST"

# pages
INDEX_PAGE = "index.html"
NOT_FOUND_PAGE = "404.html"
SRC_DIR = "src/"
