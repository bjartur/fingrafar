from http.server import *
from http import HTTPStatus
import shutil

from fingerprint_generator import Generator


class Server(BaseHTTPRequestHandler):

    def fingerprint(self):
        with Generator().generate() as file:
            self.wfile.write(b'HTTP/1.0 200 OK\r\n')
            self.wfile.write(b'Content-Type: image/x-windows-bmp\r\n')
            self.wfile.write(b'Cache-Control: no-cache\r\n')
            self.wfile.write(b'\r\n')
            shutil.copyfileobj(file, self.wfile)

    def index(self):
        self.wfile.write(b"HTTP/1.0 200 OK\r\n")
        self.wfile.write(b"Content-Type: text/html; charset=US-ASCII\r\n")
        self.wfile.write(b"Cache-Control: no-cache\r\n")
        self.wfile.write(b"\r\n")
        with open('../frontend/index.html', 'rb') as file:
            shutil.copyfileobj(file, self.wfile)


    def do_GET(self):
        try:
            if self.path == '/':
                self.index()
            elif self.path == '/fingerprint':
                self.fingerprint()
            else:
                self.send_response(HTTPStatus.NOT_FOUND)
                self.end_headers()
        except EnvironmentError:
            self.send_error(HTTPStatus.SERVICE_UNAVAILABLE)


if __name__ == "__main__":
    HTTPServer(('', 80), Server).serve_forever()
