import os
import socket
import mimetypes


# TCP server base class
class TCPServer:
    # Superclass for HTTP Server class.
    def __init__(self, host='127.0.0.1', port=2311):
        self.host = host
        self.port = port

    def start(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(5)
        print("Serving at: ", s.getsockname())

        while True:
            conn, address = s.accept()
            print("Connected to: ", address)
            # reading just the first 1024 bytes sent by the client.
            data = conn.recv(1024)
            response = self.handle_request(data)
            conn.sendall(response)
            conn.close()

    def handle_request(self, data):
        # To be Overridden
        return data


# Http server class
class HTTPServer(TCPServer):
    headers = {
        'Server': 'theServer',
        'Content-Type': 'text/html',
    }

    status_codes = {
        200: 'OK',
        404: 'Not Found',
        501: 'Not Implemented',
    }

    def handle_request(self, data):
        request = HTTPRequest(data)  # request parsed by the object
        try:
            # Call the corresponding handler method for the request method
            handler = getattr(self, 'handle_%s' % request.method)
        except AttributeError:
            handler = self.HTTP_501_handler
        response = handler(request)
        return response

    def response_line(self, status_code):
        # Returns response line (as bytes)
        reason = self.status_codes[status_code]
        response_line = 'HTTP/1.1 %s %s\r\n' % (status_code, reason)
        return response_line.encode()  # str to bytes

    def response_headers(self, extra_headers=None):
        # Returns headers (as bytes).
        headers_copy = self.headers.copy()  # local copy of headers
        if extra_headers:
            headers_copy.update(extra_headers)
        headers = ''
        for h in headers_copy:
            headers += '%s: %s\r\n' % (h, headers_copy[h])
        return headers.encode()

    def handle_OPTIONS(self, request):
        response_line = self.response_line(200)
        extra_headers = {'Allow': 'OPTIONS, GET'}
        response_headers = self.response_headers(extra_headers)
        blank_line = b'\r\n'
        return b''.join([response_line, response_headers, blank_line])

    def handle_GET(self, request):
        path = request.uri.strip('/')
        if not path:
            # If path is empty we serve the index as default
            path = 'index.html'
        if os.path.exists(path) and not os.path.isdir(path):  # don't serve directories
            response_line = self.response_line(200)
            # check file's MIME type, else set as 'text/html'
            content_type = mimetypes.guess_type(path)[0] or 'text/html'
            extra_headers = {'Content-Type': content_type}
            response_headers = self.response_headers(extra_headers)
            with open(path, 'rb') as f:
                response_body = f.read()
        else:
            response_line = self.response_line(404)
            response_headers = self.response_headers()
            with open('404.html', 'rb') as f:
                response_body = f.read()
        blank_line = b'\r\n'
        response = b''.join(
            [response_line, response_headers, blank_line, response_body])
        return response

    def HTTP_501_handler(self, request):
        response_line = self.response_line(status_code=501)
        response_headers = self.response_headers()
        blank_line = b'\r\n'
        response_body = b'<h1> 501! OMG they killed the server! </h1>'
        return b"".join([response_line, response_headers, blank_line, response_body])


class HTTPRequest:
    # Parser for HTTP requests.
    def __init__(self, data):
        self.method = None
        self.uri = None
        self.http_version = '1.1'  # default to HTTP/1.1
        # call self.parse method to parse the request data
        self.parse(data)

    def parse(self, data):
        lines = data.split(b'\r\n')
        request_line = lines[0]
        words = request_line.split(b' ')
        self.method = words[0].decode()
        if len(words) > 1:
            # if block because sometimes browsers don't send URI with the request for index
            self.uri = words[1].decode()
        if len(words) > 2:
            # again if browsers send the HTTP version
            self.http_version = words[2]


if __name__ == '__main__':
    server = HTTPServer()
    server.start()
