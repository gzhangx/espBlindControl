# SPDX-FileCopyrightText: Copyright (c) 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT
# copied from https://github.com/justbuchanan/pico_web_control/tree/main
"""
`adafruit_httpserver`
================================================================================

Simple HTTP Server for CircuitPython


* Author(s): Dan Halbert

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases
"""
ECONNRESET = 104
EBADF= 9
EAGAIN= 'I DONT KNOW THIS NUM'

#try:
    #from typing import Any, Callable, Optional
#except ImportError:
    #print("import type error")
#    pass

#from errno import EAGAIN, ECONNRESET
import os

import socket
__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_HTTPServer.git"


class HTTPStatus:  # pylint: disable=too-few-public-methods
    """HTTP status codes."""

    def __init__(self, value, phrase):
        """Define a status code.

        :param int value: Numeric value: 200, 404, etc.
        :param str phrase: Short phrase: "OK", "Not Found', etc.
        """
        self.value = value
        self.phrase = phrase

    def __repr__(self):
        return f'HTTPStatus({self.value}, "{self.phrase}")'

    def __str__(self):
        return f"{self.value} {self.phrase}"

HTTPStatus.NOT_FOUND = HTTPStatus(404, "Not Found")
"""404 Not Found"""
HTTPStatus.OK = HTTPStatus(200, "OK")  # pylint: disable=invalid-name
"""200 OK"""
HTTPStatus.INTERNAL_SERVER_ERROR = HTTPStatus(500, "Internal Server Error")
"""500 Internal Server Error"""

class _HTTPRequest:
    def __init__(
        self, path: str = "", method: str = "", raw_request = None
    ) -> None:
        self.raw_request = raw_request
        if raw_request is None:
            self.path = path
            self.method = method
        else:
            # Parse request data from raw request
            request_text = ''
            first_line = raw_request.readline().decode('utf-8')
            request_text = request_text+first_line
            contentLen = 0
            while True:
               line = raw_request.readline()               
               if not line or line == b'\r\n':
                   break
               strLine = line.decode('utf-8')               
               if strLine.lower().startswith('content-length:'):
                   contentLen = int(strLine[len('Content-Length:'):])
                   
               #print("got line="+strLine)
               request_text+=strLine
               
            bodydata = ''   
            stillNeedToRead = contentLen   
            if contentLen > 0:
                while True:
                    line = raw_request.recv(stillNeedToRead)
                    if not line or len(line) == 0:
                        break
                    bodydata += line.decode('utf-8')
                    stillNeedToRead -= len(line)
                    if stillNeedToRead <= 0:
                        break
                
            self.request_data = bodydata
            #print("request_text"+request_text)
            self.method = '';
            self.path = '';
            try:
                (self.method, self.path, _httpversion) = first_line.split()
                print("method "+self.method+" path="+self.path)
            except ValueError as exc:
                print("not parsable req", exc,first_line)
                #raise ValueError("Unparseable raw_request: ", raw_request) from exc

            

    def __hash__(self) -> int:
        return hash(self.method) ^ hash(self.path)

    def __eq__(self, other: "_HTTPRequest") -> bool:
        return self.method == other.method and self.path == other.path

    def __repr__(self) -> str:
        return f"_HTTPRequest(path={repr(self.path)}, method={repr(self.method)})"

class MIMEType:
    """Common MIME types.
    From https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
    """

    TEXT_PLAIN = "text/plain"

    APP_JSON = "application/json"
    _MIME_TYPES = {
        "bin": "application/octet-stream",
        "css": "text/css",
        "csv": "text/csv",
        "gif": "image/gif",
        "html": "text/html",
        "htm": "text/html",
        "ico": "image/vnd.microsoft.icon",        
        "jpeg .jpg": "image/jpeg",
        "js": "text/javascript",
        "json": APP_JSON,        
        "otf": "font/otf",
        "png": "image/png",
        "pdf": "application/pdf",        
        "ttf": "font/ttf",
        "txt": TEXT_PLAIN,        
    }

    @staticmethod
    def mime_type(filename):
        """Return the mime type for the given filename. If not known, return "text/plain"."""
        return MIMEType._MIME_TYPES.get(filename.split(".")[-1], MIMEType.TEXT_PLAIN)


        
class HTTPResponse:
    """Details of an HTTP response. Use in `HTTPServer.route` decorator functions."""

    _HEADERS_FORMAT = (
        "HTTP/1.1 {}\r\n"
        "Content-Type: {}\r\n"
        "Content-Length: {}\r\n"
        "Connection: close\r\n"
        "Access-Control-Allow-Origin: *\r\n"
        "\r\n"
    )

    def __init__(
        self,
        *,
        status: tuple = HTTPStatus.OK,
        content_type: str = MIMEType.TEXT_PLAIN,
        body: str = "",
        filename = None,
        root: str = "",
    ) -> None:
        """Create an HTTP response.

        :param tuple status: The HTTP status code to return, as a tuple of (int, "message").
          Common statuses are available in `HTTPStatus`.
        :param str content_type: The MIME type of the data being returned.
          Common MIME types are available in `MIMEType`.
        :param Union[str|bytes] body:
          The data to return in the response body, if ``filename`` is not ``None``.
        :param str filename: If not ``None``,
          return the contents of the specified file, and ignore ``body``.
        :param str root: root directory for filename, without a trailing slash
        """
        self.status = status
        self.content_type = content_type
        self.body = body.encode() if isinstance(body, str) else body
        self.filename = filename

        self.root = root

    def send(self, conn) -> None:
        # TODO: Use Union[SocketPool.Socket | socket.socket] for the type annotation in some way.
        """Send the constructed response over the given socket."""
        if self.filename:
            try:
                file_length = os.stat(self.root + self.filename)[6]
                self._send_file_response(conn, self.filename, self.root, file_length)
            except OSError:
                self._send_response(
                    conn,
                    HTTPStatus.NOT_FOUND,
                    MIMEType.TEXT_PLAIN,
                    f"{HTTPStatus.NOT_FOUND} {self.filename}\r\n",
                )
        else:
            self._send_response(conn, self.status, self.content_type, self.body)

    def _send_response(self, conn, status, content_type, body):
        self._send_bytes(
            conn, self._HEADERS_FORMAT.format(status, content_type, len(body))
        )
        self._send_bytes(conn, body)

    def _send_file_response(self, conn, filename, root, file_length):
        self._send_bytes(
            conn,
            self._HEADERS_FORMAT.format(
                self.status, MIMEType.mime_type(filename), file_length
            ),
        )
        
        with open(root + filename, "rb") as file:
            while bytes_read := file.read(2048):
                if bytes_read == None:
                    print("null bytes read")
                    break;
                if len(bytes_read) <=0:
                    print("bytes read <=0")
                    break;
                if self._send_bytes(conn, bytes_read) != True:
                    break
        

    def _send_bytes(self, conn, buf):  # pylint: disable=no-self-use
        bytes_sent = 0
        bytes_to_send = len(buf)
        view = memoryview(buf)
        while bytes_sent < bytes_to_send:
            try:
                bytes_sent += conn.send(view[bytes_sent:])
            except OSError as exc:
                print("got error " + str(exc.errno)+" " + str(exc))
                if exc.errno == ECONNRESET:
                    return False
                if exc.errno == EBADF:
                    return False
                if exc.errno == EAGAIN:
                    return False
                return False
        return True


        
class HTTPServer:
    """A basic socket-based HTTP server."""

    def __init__(self) -> None:
        # TODO: Use a Protocol for the type annotation.
        # The Protocol could be refactored from adafruit_requests.
        """Create a server, and get it ready to run.

        :param socket: An object that is a source of sockets. This could be a `socketpool`
          in CircuitPython or the `socket` module in CPython.
        """
        self._buffer = bytearray(1024)
        self.routes = {}
        self._sock = None
        self.root_path = "/"

    def route(self, path: str, method: str = "GET"):
        """Decorator used to add a route.

        :param str path: filename path
        :param str method: HTTP method: "GET", "POST", etc.

        Example::

            @server.route(path, method)
            def route_func(request):
                raw_text = request.raw_request.decode("utf8")
                print("Received a request of length", len(raw_text), "bytes")
                return HTTPResponse(body="hello world")

        """

        def route_decorator(func):
            self.routes[_HTTPRequest(path, method)] = func
            return func

        return route_decorator

    def serve_forever(self, host: str='', port: int = 80, root: str = "") -> None:
        """Wait for HTTP requests at the given host and port. Does not return.

        :param str host: host name or IP address
        :param int port: port
        :param str root: root directory to serve files from
        """
        self.start(host, port, root)

        while True:
            try:
                self.poll()
            except OSError:
                continue

    def start(self, host: str, port: int = 80, root: str = "") -> None:
        """
        Start the HTTP server at the given host and port. Requires calling
        poll() in a while loop to handle incoming requests.

        :param str host: host name or IP address
        :param int port: port
        :param str root: root directory to serve files from
        """
        self.root_path = root

        self._sock = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((host, port))
        self._sock.listen(10)
        # blocking socket. non-blocking doesn't seem to work on the pico W.
        # see https://github.com/adafruit/circuitpython/issues/7086
        self._sock.setblocking(True)

    def poll(self):
        """
        Call this method inside your main event loop to get the server to
        check for new incoming client requests. When a request comes in,
        the application callable will be invoked.
        """
        try:
            conn, _ = self._sock.accept()
            try:
                cl_file = conn.makefile('rwb', 0)

                request = _HTTPRequest(raw_request=cl_file)

                # If a route exists for this request, call it. Otherwise try to serve a file.
                route = self.routes.get(request, None)
                if route:
                    print("dbgrm found route")
                    response = route(request)
                elif request.method == "GET":
                    print("not found route with get")
                    response = HTTPResponse(filename=request.path, root=self.root_path)
                else:
                    print("not found route with else")
                    response = HTTPResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR)

                response.send(conn)
            finally:
                conn.close()
        except OSError as ex:
            print("got exception errno="+str(ex.errno))
            # handle EAGAIN and ECONNRESET
            if ex.errno == EAGAIN:
                # there is no data available right now, try again later.
                return
            if ex.errno == ECONNRESET:
                # connection reset by peer, try again later.
                return
            raise

    @property
    def request_buffer_size(self) -> int:
        """
        The maximum size of the incoming request buffer. If the default size isn't
        adequate to handle your incoming data you can set this after creating the
        server instance.

        Default size is 1024 bytes.

        Example::

            server = HTTPServer(pool)
            server.request_buffer_size = 2048

            server.serve_forever(str(wifi.radio.ipv4_address))
        """
        return len(self._buffer)

    @request_buffer_size.setter
    def request_buffer_size(self, value: int) -> None:
        self._buffer = bytearray(value)

