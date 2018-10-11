from http.server import *
from http import HTTPStatus
import shutil

from fingerprint_generator import Generator


class Server(BaseHTTPRequestHandler):

    def fingerprint(self):
        with Generator().generate() as file:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", 'image/x-windows-bmp')
            self.send_header("Cache-Control", 'no-cache')
            self.end_headers()
            shutil.copyfileobj(file, self.wfile)

    def index(self):
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", 'text/html; charset=US-ASCII')
        self.send_header("Cache-Control", 'no-cache')
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
            self.send_response(HTTPStatus.SERVICE_UNAVAILABLE)


if __name__ == "__main__":
    HTTPServer(('', 80), Server).serve_forever()
