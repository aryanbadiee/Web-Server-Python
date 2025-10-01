"""
A web-server with socket programming in Python

Author: https://github.com/aryanbadiee
"""

import socket
import time
import threading
from os import path


def get_content_type(request: str, /) -> str:
    """ Returns the appropriate Content-Type based on file extension. """

    if request.endswith((".htm", ".html")):
        return "text/html"
    elif request.endswith(".css"):
        return "text/css"
    elif request.endswith(".js"):
        return "text/javascript"
    elif request.endswith(".png"):
        return "image/png"
    elif request.endswith((".jpg", ".jpeg")):
        return "image/jpeg"
    elif request.endswith(".mp3"):
        return "audio/mpeg"
    else:
        return "text/plain"  # Default


def read_body(http: str, /) -> str:
    """ Extracts body from raw HTTP data. """

    parts = http.split("\r\n\r\n", 1)

    return parts[1] if len(parts) > 1 else ""


def gen_headers(code: int, length: int, content_type: str, /) -> str:
    """ Generates HTTP response headers. """

    status_messages = {
        200: "200 OK",
        404: "404 Not Found",
    }

    response_line = f"HTTP/1.1 {status_messages.get(code, '200 OK')}\n"
    current_date = time.strftime("%A, %Y-%m-%d %H:%M:%S", time.localtime())

    headers = (
        f"Date: {current_date}\n"
        f"Content-Type: {content_type}\n"
        f"Server: Simple-Python-HTTP-Server\n"
        f"Connection: close\n"
        f"Content-Length: {length}\n\n"
    )

    return response_line + headers


class Server:
    """ Class describing a simple HTTP server objects """

    def __init__(self, host: str = "127.0.0.1", port: int = 80):
        self.host = host
        self.port = port
        self.root = "./public"  # The directory where the web-page files are stored
        self.buffer_size = 2_048

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # SOCK_STREAM = TCP Protocol
        # SOCK_DGRAM = UDP Protocol
        # AF_INET = using ipv4
        # AF_INET6 = using ipv6

    def run(self):
        try:
            self.socket.bind((self.host, self.port))
        except Exception as ex:
            print("Cannot acquire port", self.port)
            print(ex)
            print("I'll try another port")

            self.port = 8080

            try:
                print("Launching HTTP server on", self.host + ":" + str(self.port))
                self.socket.bind((self.host, self.port))
            except Exception as ex:
                print("Failed to get socket for port", self.port)
                print(ex)
                print("Try running the server in a privileged user mode")

                self.socket.close()

                import sys
                sys.exit(3)

        print("Server acquired successfully the socket with port", self.port)
        print('-' * 20)

        self.socket.listen(5)  # Maximum number of connections in the queue

        while True:
            connection, address = self.socket.accept()
            # connection - socket (socket)
            # address - client address (tuple)
            # address[0] = ip (str)
            # address[1] = port (int)

            data = connection.recv(self.buffer_size)  # Receives data from client
            received_data = bytes.decode(data)  # Decodes it to string

            http_method, uri, http_version = received_data.splitlines(keepends=False)[0].split()

            print(address[0] + ':' + str(address[1]),
                  '[' + time.strftime("%A, %Y-%m-%d %H:%M:%S") + ']',
                  '"' + http_method, uri, http_version + '"', '-')  # Logging

            threading.Thread(target=self.handler,
                             args=(connection, http_method, uri, received_data),
                             daemon=True).start()  # Run thread

    def handler(self, connection: socket.socket,
                http_method: str, uri: str, received_data: str, /):
        if http_method == "GET" or http_method == "POST":
            if uri == '/' or \
                    uri == '/index' or \
                    uri == '/main':
                request = 'index.html'  # Loads index.html by default!

                # Loads file content
                try:
                    request_path = path.join(self.root, request)
                    with open(request_path, "rb") as file:
                        response_content = file.read()
                        length = len(response_content)

                    response_headers = gen_headers(200,
                                                   length,
                                                   get_content_type(request_path))
                except Exception as ex:  # File not found!
                    print("404 not found error!", ex,
                          sep='\n', end='\n' + '-' * 20 + '\n')
                    response_content = \
                        b"<html><body><p>Error 404: File not found</p><p>Python HTTP server</p></body></html>"

                    response_headers = gen_headers(404,
                                                   len(response_content),
                                                   get_content_type(".html"))

                server_response = response_headers.encode()
                server_response += response_content

                connection.send(server_response)
            elif uri == "/msg":
                body_data = read_body(received_data)
                if (index_of_variable := body_data.find("text=")) != -1:
                    index_of_value = index_of_variable + len("text=")
                    client_msg = body_data[index_of_value:]

                    header_resp = gen_headers(200,
                                              len(client_msg),
                                              get_content_type("plain"))
                    body_resp = client_msg

                    resp = header_resp + body_resp
                    resp = resp.encode("UTF-8")

                    connection.send(resp)
            else:
                request = uri.removeprefix('/')  # Removes '/' from the beginning!

                # Loads file content
                try:
                    request_path = path.join(self.root, request)

                    with open(request_path, "rb") as file:
                        response_content = file.read()
                        length = len(response_content)

                    response_headers = gen_headers(200,
                                                   length,
                                                   get_content_type(request_path))
                except Exception as ex:  # File not found!
                    print("404 not found error!", ex,
                          sep='\n', end='\n' + '-' * 20 + '\n')
                    response_content = \
                        b"<html><body><p>Error 404: File not found</p><p>Python HTTP server</p></body></html>"

                    response_headers = gen_headers(404,
                                                   len(response_content),
                                                   get_content_type(".html"))

                server_response = response_headers.encode()
                server_response += response_content

                connection.send(server_response)

        connection.close()


if __name__ == "__main__":
    print("Starting Web Server...", end='\n' * 2)

    serv = Server()
    serv.run()
