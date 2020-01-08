# @author -> https://www.github.com/aryanbadiee

import socket       # Networking support
import time         # Current time
import _thread      # multi-threading

myPort = 80             # your own port
myHost = ""             # your own host
myRoot = "public/"      # your own root (folder for client-side code)


class Server:
    """ Class describing a simple HTTP server objects."""
    
    def __init__(self):
        """ Constructor """
        self.host = myHost           # <-- works on all available network interfaces
        self.port = myPort
        self.dir = myRoot            # Directory where web-page files are stored

        """ Attempts to acquire the socket and launch the server """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def activate_server(self):
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
        self._wait_for_connections()

    def _gen_headers(self, code, _type: str=None):
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
            h += 'Connection: close\n\n'
            # signal that the connection will be closed after completing the request
            # \n\n, it's very important between for header and body(because of the http rules)
        else:
            # write further headers
            current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
            h += 'Date: ' + current_date + '\n'
            h += 'Content-Type: ' + _type + '\n'
            h += 'Server: Simple-Python-HTTP-Server\n'
            h += 'Connection: close\n\n'
            # signal that the connection will be closed after completing the request
            # \n\n, it's very important between for header and body(because of the http rules)

        return h

    def shutdown(self):
        """ Shut down the server """
        try:
            print("Shutting down the server")
            self.socket.shutdown(socket.SHUT_RDWR)

        except Exception as e:
            print("Warning: could not shut down the socket. Maybe it was already closed?", e)

    def _wait_for_connections(self):
        """ Main loop awaiting connections """
        self.socket.listen(5)  # maximum number of queued connections
        while True:
            print("Awaiting New Connection")
            print("-----------------------")

            connection, address = self.socket.accept()
            # connection - socket
            # address - client address

            print("Got connection from:", address)

            data = connection.recv(1024)    # receive data from client
            string = bytes.decode(data)     # decode it to string

            # determine request method  (HEAD and GET are supported)
            request_method = string.split()[0]          # method of request
            print("Method: ", request_method)
            print("Request body: ", string)

            # body_data = self.read_body_data(string)   # body_data: str

            # if string[0:3] == 'GET':
            if (request_method == 'GET') or (request_method == 'HEAD') or (request_method == 'POST'):
                # file_requested = string[4:]

                # split on space "GET /file.html" -into-> ('GET','file.html',...)
                file_requested = string.split(' ')[1]   # get 2nd element
                response_content = b""   # for body of http response(it's binary)

                if file_requested == '/' or \
                   file_requested == '/index' or \
                   file_requested == '/main':      # in case no file is specified by the browser

                    file_requested = 'index.html'   # load index.html by default

                    # file_requested = self.www_dir + file_requested
                    print("Serving web page [", file_requested, "]")

                    # Load file content
                    try:
                        file_requested = self.dir + file_requested      # public/...
                        with open(file_requested, "rb") as file_handler:
                            if request_method == "GET" or request_method == "POST":
                                response_content = file_handler.read()

                        response_headers = self._gen_headers(200,
                                                             self.get_content_type(file_requested))

                    except Exception as e:  # in case file was not found, generate 404 page
                        print("Warning, file not found. Serving response code 404\n", e, sep='')
                        response_headers = self._gen_headers(404)

                        if request_method == 'GET' or request_method == 'POST':
                            response_content = \
                                b"<html><body><p>Error 404: File not found</p><p>Python HTTP server</p></body></html>"

                    server_response = response_headers.encode()     # return headers for GET, POST and HEAD
                    if request_method == 'GET' or request_method == 'POST':
                        server_response += response_content  # return additional content for GET, POST only

                    connection.send(server_response)
                    print("Closing connection with client")
                    connection.close()

                else:
                    file_requested = file_requested[1:]     # Remove '/' from first statement
                    print("Serving web page [", file_requested, "]")

                    # Load file content:
                    try:
                        file_requested = self.dir + file_requested      # public/...
                        with open(file_requested, "rb") as file_handler:
                            if request_method == "GET" or request_method == "POST":
                                response_content = file_handler.read()

                        response_headers = self._gen_headers(200,
                                                             self.get_content_type(file_requested))
                    except Exception as e:  # in case file was not found, generate 404 page
                        print("Warning, file not found. Serving response code 404\n", e, sep='')
                        response_headers = self._gen_headers(404)

                        if request_method == 'GET' or request_method == 'POST':
                            response_content = \
                                b"<html><body><p>Error 404: File not found</p><p>Python HTTP server</p></body></html>"

                    server_response = response_headers.encode()  # return headers for GET, Post and HEAD
                    if request_method == 'GET' or request_method == 'POST':
                        server_response += response_content  # return additional content for GET, POST only

                    connection.send(server_response)
                    print("Closing connection with client")
                    connection.close()

    def get_content_type(self, file_requested: str) -> str:
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

    def graceful_shutdown(self, dummy):
        """ This function shuts down the server. It's triggered
        by SIGINT signal """
        s.shutdown()    # shut down the server
        import sys
        sys.exit(1)

    # for getting data from body of HTTP:
    def read_body_data(self, string: str) -> str:
        lines = string.splitlines()

        result = ""             # for return
        _next = False

        for line in lines:
            if line == "":      # means empty line between header and body in HTTP
                _next = True
            elif _next:
                result += line

        return result


# *********************************************************************
def exit_process():
    while True:
        cmd = input()
        if cmd == "$exit":
            import os
            os._exit(1)         # exit from program
        elif cmd == "$time":    # getting time from server
            print(time.strftime("%A, %d/%B/%Y - %H:%M:%S"))
# *********************************************************************


_thread.start_new_thread(exit_process, ())  # for calling exit_process in other thread
# () is an empty tuple

print("Starting Web Server")
print("if you want to exit from program just write \"$exit\" in console!")
s = Server()            # construct server object
s.activate_server()     # acquire the socket
