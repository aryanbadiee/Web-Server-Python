"""
A web-server with socket programming in Python

Author: https://github.com/aryanbadiee
"""

import socket
import time
import threading


def get_content_type(file_requested: str) -> str:
    if file_requested.__contains__(".htm") or file_requested.__contains__(".html"):
        return "text/html"
    elif file_requested.__contains__(".css"):
        return "text/css"
    elif file_requested.__contains__(".js"):
        return "text/javascript"
    elif file_requested.__contains__(".png"):
        return "image/png"
    elif file_requested.__contains__(".jpg") or file_requested.__contains__(".jpeg"):
        return "image/jpeg"
    elif file_requested.__contains__(".mp3"):
        return "audio/mpeg"

    # You can add support for other file formats - Like above!


def read_body_data(http: str) -> str:
    lines = http.splitlines(keepends=False)

    result = ""  # for return
    flag = False

    for line in lines:
        if line == "":  # means empty line between header and body in HTTP
            flag = True
        elif flag:
            result += line

    return result


def gen_headers(code, length: int, _type: str = None) -> str:
    """ Generates HTTP response Headers. Omits the first line! """

    h = ''
    if code == 200:
        h = 'HTTP/1.1 200 OK\n'
    elif code == 404:
        h = 'HTTP/1.1 404 Not Found\n'

    if _type is None:
        current_date = time.strftime("%A, %Y-%m-%d %H:%M:%S", time.localtime())
        h += 'Date: ' + current_date + '\n'
        h += 'Server: Simple-Python-HTTP-Server\n'
        h += 'Connection: close\n'
        h += 'Content-Length: %i\n\n' % length
        # \n\n, it's very important between header and body (because of the HTTP rules)
    else:
        current_date = time.strftime("%A, %Y-%m-%d %H:%M:%S", time.localtime())
        h += 'Date: ' + current_date + '\n'
        h += 'Content-Type: ' + _type + '\n'
        h += 'Server: Simple-Python-HTTP-Server\n'
        h += 'Connection: close\n'
        h += 'Content-Length: %i\n\n' % length
        # \n\n, it's very important between header and body (because of the HTTP rules)

    return h


class Server:
    """ Class describing a simple HTTP server objects """

    def __init__(self, host: str = "localhost", port: int = 80):
        self.host = host
        self.port = port
        self.root = "public/"  # The directory where the web-page files are stored

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
            print("I'll try another port")
            print(ex)

            user_port = self.port
            self.port = 8080

            try:
                print("Launching HTTP server on", self.host + ":" + str(self.port))
                self.socket.bind((self.host, self.port))
            except Exception as ex:
                print("Failed to acquire sockets for ports", user_port, "and 8080!")
                print("Try running the server in a privileged user mode")
                print(ex)

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

            data = connection.recv(1024)  # Receive data from client
            received_data = bytes.decode(data)  # Decode it to string

            parts = received_data.split(' ')  # Split with ' ' on HTTP data
            request_method = parts[0]
            req = parts[1]
            http_v = parts[2].split("\r\n")[0]

            print(address[0] + ":" + str(address[1]),
                  "[" + time.strftime("%A, %Y-%m-%d %H:%M:%S") + "]",
                  '"' + request_method, req, http_v + '"', "-")  # Logging

            threading.Thread(target=self.handler,
                             args=(connection, received_data, request_method),
                             daemon=True).start()  # Run thread

    def handler(self, connection, received_data, request_method):
        if (request_method == 'GET') or \
                (request_method == 'POST'):
            file_requested = received_data.split()[1]  # Request of the client

            if file_requested == '/' or \
                    file_requested == '/index' or \
                    file_requested == '/main':
                file_requested = 'index.html'  # Load index.html by default!

                # Load file content:
                try:
                    file_requested = self.root + file_requested  # public/...
                    with open(file_requested, "rb") as file_handler:
                        response_content = file_handler.read()
                        length = len(response_content)

                    response_headers = gen_headers(200, length, get_content_type(file_requested))
                except Exception as ex:  # The file not found!
                    print("The file not found. Serving response code 404\n", ex, sep=" | ")
                    response_content = \
                        b"<html><body><p>Error 404: File not found</p><p>Python HTTP server</p></body></html>"

                    response_headers = gen_headers(404, len(response_content))

                server_response = response_headers.encode()
                server_response += response_content

                connection.send(server_response)
                connection.close()
            elif file_requested == "/msg":
                data_of_body = read_body_data(received_data)
                if (index_of_variable := data_of_body.find("text=")) != -1:
                    index_of_value = index_of_variable + len("text=")
                    client_msg = data_of_body[index_of_value:]

                    header_resp = gen_headers(200, len(client_msg))
                    body_resp = client_msg

                    resp = header_resp + body_resp
                    resp = resp.encode("UTF-8")

                    connection.send(resp)
                connection.close()
            else:
                file_requested = file_requested[1:]  # Remove '/'

                # Load file content:
                try:
                    file_requested = self.root + file_requested  # public/...
                    with open(file_requested, "rb") as file_handler:
                        response_content = file_handler.read()
                        length = len(response_content)

                    response_headers = gen_headers(200, length, get_content_type(file_requested))
                except Exception as ex:  # The file not found!
                    print("The file not found. Serving response code 404\n", ex, sep=" | ")
                    response_content = \
                        b"<html><body><p>Error 404: File not found</p><p>Python HTTP server</p></body></html>"

                    response_headers = gen_headers(404, len(response_content))

                server_response = response_headers.encode()
                server_response += response_content

                connection.send(server_response)
                connection.close()


if __name__ == "__main__":
    print("Starting Web Server\n")

    serv = Server()
    serv.run()
