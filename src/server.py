# @author -> https://www.github.com/aryanbadiee

import socket  # Networking support
import time  # Current time
import _thread  # multi-threading
import threading  # new library of multi-thread


myPort = 80  # your own port
myHost = "0.0.0.0"  # your own host
myRoot = "public/"  # your own root (folder for client-side code)


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


# for getting data from body of HTTP:
def read_body_data(http: str) -> str:
    lines = http.splitlines()

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

    # determine response code
    h = ''
    if code == 200:
        h = 'HTTP/1.1 200 OK\n'
    elif code == 404:
        h = 'HTTP/1.1 404 Not Found\n'

    if _type is None:
        # write further headers
        current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        h += 'Date: ' + current_date + '\n'
        h += 'Server: Simple-Python-HTTP-Server\n'
        h += 'Connection: close\n'
        h += 'Content-Length: %i\n\n' % length
        # signal that the connection will be closed after completing the request
        # \n\n, it's very important between for header and body(because of the http rules)
    else:
        # write further headers
        current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        h += 'Date: ' + current_date + '\n'
        h += 'Content-Type: ' + _type + '\n'
        h += 'Server: Simple-Python-HTTP-Server\n'
        h += 'Connection: close\n'
        h += 'Content-Length: %i\n\n' % length
        # signal that the connection will be closed after completing the request
        # \n\n, it's very important between for header and body(because of the http rules)

    return h


class Server:
    """ Class describing a simple HTTP server objects."""

    def __init__(self, host: str = myHost, port: int = myPort):
        """ Constructor """

        self.host = host
        self.port = port
        self.root = myRoot  # Directory where web-page files are stored

        """ Attempts to acquire the socket and launch the server """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # SOCK_STREAM = TCP Protocol
        # SOCK_DGRAM = UDP Protocol
        # AF_INET = using ipv4
        # AF_INET6 = using ipv6

    def run(self):
        # user provided in the __init__() port may be unavailable:
        try:
            self.socket.bind((self.host, self.port))
        except Exception as e:
            print("Warning: Could not acquire port:", self.port, "\n")
            print("I will try a higher port")
            print(e)
            # store to user provided port locally for later (in case 8080 fails)
            user_port = self.port
            self.port = 8080

            try:
                print("Launching HTTP server on ", self.host, ":", self.port)
                self.socket.bind((self.host, self.port))
            except Exception as e:
                print("ERROR: Failed to acquire sockets for ports ", user_port, " and 8080. ")
                print("Try running the Server in a privileged user mode.")
                print(e)
                self.shutdown()
                import sys
                sys.exit(1)

        print("Server acquired successfully the socket with port:", self.port)
        print("-----------------------------------------------------")

        # listen:
        self.socket.listen(5)  # maximum number of queued connections

        # accept:
        while True:
            connection, address = self.socket.accept()
            # connection - socket (socket)
            # address - client address (tuple)
            # address[0] = ip (str)
            # address[1] = port (int)

            data = connection.recv(1024)  # receive data from client
            received_data = bytes.decode(data)  # decode it to string
            parts = received_data.split(" ")  # split with " " on http data
            request_method = parts[0]
            req = parts[1]
            http_v = parts[2].split("\r\n")[0]

            # log:
            print(address[0] + ":" + str(address[1]),
                  "[" + time.strftime("%a-%d/%b/%Y %H:%M:%S") + "]",
                  '"' + request_method, req, http_v + '"', "-")

            threading.Thread(target=self.handler,
                             args=(connection, received_data, request_method)).start()  # run thread

    def handler(self, connection, received_data, request_method):
        if (request_method == 'GET') or (request_method == 'HEAD') or (request_method == 'POST'):

            file_requested = received_data.split()[1]  # getting 2nd element(request of client)
            response_content = b""  # for body of http response(it's binary)

            if file_requested == '/' or \
                    file_requested == '/index' or \
                    file_requested == '/main':  # in case no file is specified by the browser

                file_requested = 'index.html'  # load index.html by default

                # Load file content
                try:
                    file_requested = self.root + file_requested  # public/...
                    with open(file_requested, "rb") as file_handler:
                        if request_method == "GET" or request_method == "POST":
                            response_content = file_handler.read()
                            length = len(response_content)

                    response_headers = gen_headers(200, length,
                                                   get_content_type(file_requested))
                except Exception as e:  # in case file was not found, generate 404 page
                    # print("Warning, file not found. Serving response code 404\n", e, sep='')
                    if request_method == 'GET' or request_method == 'POST':
                        response_content = \
                            b"<html><body><p>Error 404: File not found</p><p>Python HTTP server</p></body></html>"
                    response_headers = gen_headers(404, len(response_content))

                server_response = response_headers.encode()  # return headers for GET, POST and HEAD
                if request_method == 'GET' or request_method == 'POST':
                    server_response += response_content  # return additional content for GET, POST only

                connection.send(server_response)
                connection.close()

            elif file_requested == "/msg":
                data_of_body = read_body_data(received_data)  # body_data: str
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
                file_requested = file_requested[1:]  # Removing '/'

                # Load file content:
                try:
                    file_requested = self.root + file_requested  # public/...
                    with open(file_requested, "rb") as file_handler:
                        if request_method == "GET" or request_method == "POST":
                            response_content = file_handler.read()
                            length = len(response_content)

                    response_headers = gen_headers(200, length,
                                                   get_content_type(file_requested))
                except Exception as e:  # in case file was not found, generate 404 page
                    # print("Warning, file not found. Serving response code 404\n", e, sep='')
                    if request_method == 'GET' or request_method == 'POST':
                        response_content = \
                            b"<html><body><p>Error 404: File not found</p><p>Python HTTP server</p></body></html>"
                    response_headers = gen_headers(404, len(response_content))

                server_response = response_headers.encode()  # return headers for GET, Post and HEAD
                if request_method == 'GET' or request_method == 'POST':
                    server_response += response_content  # return additional content for GET, POST only

                connection.send(server_response)
                connection.close()

    def shutdown(self):
        """ Shut down the server """

        try:
            print("Shutting down the server")
            self.socket.shutdown(socket.SHUT_RDWR)
        except Exception as e:
            print("Warning: could not shut down the socket. Maybe it was already closed?", e)

    def graceful_shutdown(self):
        """ This function shuts down the server. It's triggered
        by SIGINT signal """

        self.shutdown()  # shut down the server
        import sys
        sys.exit(1)


# *********************************************************************
def exit_process():
    while True:
        cmd = input()
        if cmd == "$exit":
            import os
            os._exit(1)  # exit from program
        elif cmd == "$time":  # getting time from server
            print(time.strftime("%A, %d/%B/%Y - %H:%M:%S"))
# *********************************************************************


_thread.start_new_thread(exit_process, ())  # for calling exit_process in other thread
# () is an empty tuple

print("Starting Web Server")
print("if you want to exit from program just write \"$exit\" in console!")
serv = Server("0.0.0.0", 80)  # construct server object
serv.run()  # acquire the socket
