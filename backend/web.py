from http.server import *
from http import HTTPStatus
import shutil
import time
import os
from _ctypes import COMError

from pywinauto.findwindows import ElementNotFoundError
from pywinauto.findbestmatch import MatchError
from pywinauto.timings import TimeoutError

from fingerprint_generator import Generator
import fingerprint_generator as sfinge

last_generation_started = 0.0
slide_interval = 55

def generate():
    global last_generation_started
    try:
        last_generation_started = time.time()
        Generator().generate()
    except (
        ElementNotFoundError,
        TypeError,
        MatchError,
        TimeoutError,
        COMError
    ):
        last_generation_started = 0.0

class Server(BaseHTTPRequestHandler):

    def generation_didnt_finish(arg):
        global last_generation_started, slide_interval
        return time.time() - last_generation_started > 1.3 * slide_interval

    def generate_if_needed(self):
        global last_generation_started, slide_interval
        last_modified = os.path.getmtime(sfinge.file_path)
        if time.time() - last_generation_started >= slide_interval:
            if last_generation_started < last_modified:
                generate()
            elif self.generation_didnt_finish():
                generate()

    # Before: file_path does not exist
    def generate_if_not_already_generating(self):
        global last_generation_started, slide_interval
        if last_generation_started < 1:
            generate()
        elif self.generation_didnt_finish():
            generate()

    def fingerprint_headers(self):
        self.wfile.write(b'HTTP/1.0 200 OK\r\n')

        self.wfile.write(b'Content-Type: image/x-windows-bmp\r\n')

        self.wfile.write(b'Cache-Control: no-cache\r\n')
        self.wfile.write(b"Cache: no-cache\r\n")
        self.wfile.write(b"Pragma-Control: no-cache\r\n")
        self.wfile.write(b"Cache-directive: no-cache\r\n")
        self.wfile.write(b"Pragma-directive: no-cache\r\n")
        self.wfile.write(b"Cache-Control: no-cache\r\n")
        self.wfile.write(b"Pragma: no-cache\r\n")
        self.wfile.write(b"Expires: 0\r\n")
        self.wfile.write(b"Pragma-directive: no-cache\r\n")
        self.wfile.write(b"Cache-directive: no-cache\r\n")

        self.wfile.write(b'\r\n')

    def fingerprint(self):
        with open(sfinge.file_path, 'rb') as file:
            self.fingerprint_headers()
            shutil.copyfileobj(file, self.wfile)
        self.wfile.flush()
        self.rfile.close()
        self.generate_if_needed()

    def index_headers(self):
        self.wfile.write(b"HTTP/1.0 200 OK\r\n")
        self.wfile.write(b"Content-Type: text/html; charset=US-ASCII\r\n")
        self.wfile.write(b"Last-Modified: Fri, 19 Oct 2018 12:40:00 GMT\r\n")
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
            elif self.path.startswith('/fingerprint'):
                if not os.path.exists(sfinge.file_path):
                    self.send_error(HTTPStatus.SERVICE_UNAVAILABLE)
                    self.end_headers()
                    self.generate_if_not_already_generating()
                else:
                    self.fingerprint()
            else:
                self.wfile.write(b'HTTP/1.1 404 NOT FOUND\r\n')
                self.wfile.write(b"Last-Modified: Fri, 19 Oct 2018 12:40:00 GMT\r\n")
                self.wfile.write(b'Content-Length: 11\r\n')
                self.wfile.write(b'Content-Type: text/plain;charset=US-ASCII\r\n')
                self.wfile.write(b'Cache-Control: no-cache\r\n')
                self.wfile.write(b'Connection: Close\r\n')
                self.wfile.write(b'\r\n')
                self.wfile.write(b'Not found\r\n')
        except EnvironmentError:
            self.send_error(HTTPStatus.SERVICE_UNAVAILABLE)


if __name__ == "__main__":
    if not os.path.exists(sfinge.file_path):
        generate()
    ThreadingHTTPServer(('127.0.0.1', 8080), Server).serve_forever()
    #ThreadingHTTPServer(('', 80), Server).serve_forever()
