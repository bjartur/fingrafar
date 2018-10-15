from http.server import *
from http import HTTPStatus
import shutil

from fingerprint_generator import Generator

directory = tempfile.gettempdir()
filename = 'fingerprint.bmp'
file_path = os.path.join(directory, filename)

class Server(BaseHTTPRequestHandler):

    def fingerprint_headers(self):
        self.wfile.write(b'HTTP/1.0 200 OK\r\n')
        self.wfile.write(b'Content-Type: image/x-windows-bmp\r\n')
        self.wfile.write(b'Cache-Control: no-cache\r\n')
        self.wfile.write(b'\r\n')

    def fingerprint(self):
        Generator().generate(file_path)
        with open(file_path, 'rb') as file:
            self.fingerprint_headers()
            shutil.copyfileobj(file, self.wfile)

    def index_headers(self):
        self.wfile.write(b"HTTP/1.0 200 OK\r\n")
        self.wfile.write(b"Content-Type: text/html; charset=US-ASCII\r\n")
        self.wfile.write(b"Cache-Control: no-cache\r\n")
        self.wfile.write(b"\r\n")

    def index(self):
        self.index_headers()
        with open('../frontend/index.html', 'rb') as file:
            shutil.copyfileobj(file, self.wfile)

    def do_HEAD(self):
        self.common(self.index_headers, self.fingerprint_headers)

    def do_GET(self):
        self.common(self.index, self.fingerprint)
    
    def common(self, index, fingerprint):
        try:
            if self.path == '/':
                index()
            elif self.path == '/fingerprint':
                fingerprint()
            else:
                self.send_response(HTTPStatus.NOT_FOUND)
                self.end_headers()
        except EnvironmentError:
            self.send_error(HTTPStatus.SERVICE_UNAVAILABLE)


if __name__ == "__main__":
    HTTPServer(('', 80), Server).serve_forever()
