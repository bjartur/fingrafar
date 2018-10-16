from http.server import *
from http import HTTPStatus
import shutil
import time
import os

from fingerprint_generator import Generator
import fingerprint_generator as sfinge

last_generation_started = 0.0
slide_interval = 15

class Server(BaseHTTPRequestHandler):

    def generate_if_needed(self):
        global last_generation_started, slide_interval
        last_modified = os.path.getmtime(sfinge.file_path)
        if time.time() - last_generation_started >= slide_interval:
            if last_generation_started < last_modified:
                self.generate()

    # Before: file_path does not exist
    def generate_if_not_already_generating(self):
        global last_generation_started, slide_interval
        if last_generation_started < 1:
            self.generate()
        elif time.time() - last_generation_started > 2*slide_interval:
            self.generate()

    def generate(self):
        last_generation_started = time.time()
        Generator().generate()

    def fingerprint_headers(self):
        self.wfile.write(b'HTTP/1.0 200 OK\r\n')
        self.wfile.write(b'Content-Type: image/x-windows-bmp\r\n')
        self.wfile.write(b'Cache-Control: no-cache\r\n')
        self.wfile.write(b'\r\n')

    def fingerprint(self):
        with open(sfinge.file_path, 'rb') as file:
            self.fingerprint_headers()
            shutil.copyfileobj(file, self.wfile)
        self.generate_if_needed()

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
                if not os.path.exists(sfinge.file_path):
                    self.send_error(HTTPStatus.SERVICE_UNAVAILABLE)
                    self.end_headers()
                    self.generate_if_not_already_generating()
                else:
                    self.fingerprint()
            else:
                self.send_response(HTTPStatus.NOT_FOUND)
                self.end_headers()
        except EnvironmentError:
            self.send_error(HTTPStatus.SERVICE_UNAVAILABLE)


if __name__ == "__main__":
    ThreadingHTTPServer(('', 80), Server).serve_forever()
