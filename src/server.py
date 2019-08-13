import socket       # Networking support
import time         # Current time
import _thread      # multi-threading

myPort = 300            # your own port
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
        try:    # user provided in the __init__() port may be unavailable
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

        print("Server successfully acquired the socket with port:", self.port)
        self._wait_for_connections()

    def shutdown(self):
        """ Shut down the server """
        try:
            print("Shutting down the server")
            s.socket.shutdown(socket.SHUT_RDWR)

        except Exception as e:
            print("Warning: could not shut down the socket. Maybe it was already closed?", e)

    def _gen_headers(self,  code):
        """ Generates HTTP response Headers. Omits the first line! """

        # determine response code
        h = ''
        if code == 200:
            h = 'HTTP/1.1 200 OK\n'
        elif code == 404:
            h = 'HTTP/1.1 404 Not Found\n'

        # write further headers
        current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
        h += 'Date: ' + current_date + '\n'
        h += 'Server: Simple-Python-HTTP-Server\n'
        h += 'Connection: close\n\n'
        # signal that the connection will be closed after completing the request
        # \n\n, it's very important between for header and body(because of the http rules)

        return h

    def _wait_for_connections(self):
        """ Main loop awaiting connections """
        while True:
            print("Awaiting New connection")
            print("-----------------------")
            self.socket.listen(5)   # maximum number of queued connections

            (connection, address) = self.socket.accept()
            # connection - socket
            # address - client address

            print("Got connection from:", address)

            data = connection.recv(1024)    # receive data from client
            string = bytes.decode(data)     # decode it to string

            # determine request method  (HEAD and GET are supported)
            request_method = string.split(' ')[0]
            print("Method: ", request_method)
            print("Request body: ", string)

            # if string[0:3] == 'GET':
            if (request_method == 'GET') | (request_method == 'HEAD'):
                # file_requested = string[4:]

                # split on space "GET /file.html" -into-> ('GET','file.html',...)
                file_requested = string.split(' ')[1]   # get 2nd element
                response_content = b""   # for body of http response(it's binary)

                if file_requested == '/':  # in case no file is specified by the browser
                    file_requested = 'index.html'   # load index.html by default

                    # file_requested = self.www_dir + file_requested
                    print("Serving web page [", file_requested, "]")

                    # Load file content
                    try:
                        file_requested = self.dir + file_requested      # public/...
                        file_handler = open(file_requested, 'rb')
                        if request_method == 'GET':  # only read the file when GET
                            response_content = file_handler.read()  # read file content
                        file_handler.close()

                        response_headers = self._gen_headers(200)

                    except Exception as e:  # in case file was not found, generate 404 page
                        print("Warning, file not found. Serving response code 404\n", e, sep='')
                        response_headers = self._gen_headers(404)

                        if request_method == 'GET':
                            response_content = \
                                b"<html><body><p>Error 404: File not found</p><p>Python HTTP server</p></body></html>"

                    server_response = response_headers.encode()     # return headers for GET and HEAD
                    if request_method == 'GET':
                        server_response += response_content  # return additional content for GET only

                    connection.send(server_response)
                    print("Closing connection with client")
                    connection.close()

                else:
                    file_requested = file_requested[1:]     # Remove '/' from first statement
                    print("Serving web page [", file_requested, "]")

                    # Load file content:
                    try:
                        file_requested = self.dir + file_requested      # public/...
                        file_handler = open(file_requested, 'rb')
                        if request_method == 'GET':  # only read the file when GET
                            response_content = file_handler.read()  # read file content
                        file_handler.close()

                        response_headers = self._gen_headers(200)
                    except Exception as e:  # in case file was not found, generate 404 page
                        print("Warning, file not found. Serving response code 404\n", e, sep='')
                        response_headers = self._gen_headers(404)

                        if request_method == 'GET':
                            response_content = \
                                b"<html><body><p>Error 404: File not found</p><p>Python HTTP server</p></body></html>"

                    server_response = response_headers.encode()  # return headers for GET and HEAD
                    if request_method == 'GET':
                        server_response += response_content  # return additional content for GET only

                    connection.send(server_response)
                    print("Closing connection with client")
                    connection.close()

    def graceful_shutdown(self, dummy):
        """ This function shuts down the server. It's triggered
        by SIGINT signal """
        s.shutdown()    # shut down the server
        import sys
        sys.exit(1)


# *********************************************************************
def exit_process():
    while True:
        cmd = input()       # listen to exit form process
        if cmd == "$exit":
            import os
            os._exit(1)     # exit from program
# *********************************************************************


_thread.start_new_thread(exit_process, ())  # for calling exit_process in other thread

print("Starting Web Server")
s = Server()            # construct server object
s.activate_server()     # acquire the socket

# exit from program with typing $exit in console
