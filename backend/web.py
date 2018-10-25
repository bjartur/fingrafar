from http.server import *
from http import HTTPStatus
import itertools
import shutil
import time
from datetime import datetime
import os
from _ctypes import COMError

from pywinauto.findwindows import ElementNotFoundError
from pywinauto.findbestmatch import MatchError
from pywinauto.timings import TimeoutError
from PIL import Image

from fingerprint_generator import Generator
import fingerprint_generator as sfinge

last_generation_started = 0.0
last_generation_finished = 0.0
slide_interval = 55
image = b''


def generate_if_needed(retries=0):
    global last_generation_started, last_generation_finished, slide_interval
    if time.time() - last_generation_started >= slide_interval:
        if last_generation_started < last_generation_finished:
            generate(retries)
        elif generation_didnt_finish():
            generate(retries)

def generation_didnt_finish():
    global last_generation_started, slide_interval
    return time.time() - last_generation_started > 1.8 * slide_interval

def generate_if_not_already_generating(self):
    global last_generation_started, slide_interval
    if last_generation_started < 1:
        generate()
    elif generation_didnt_finish():
        generate()

def generate(retries=0):
    global last_generation_started, last_generation_finished
    this_started = time.time()
    last_generation_started = this_started
    try:
        gen = Generator()
        gen.generate()
    except (
        AttributeError,
        ElementNotFoundError,
        TypeError,
        MatchError,
        TimeoutError,
        COMError
    ) as e:
        last_generation_started = 0.0
        gen.familicide()
        print()
        print(datetime.now())
        print(type(e))
        print(gen.location)
        print(e)
        if retries < 2:
            generate_if_needed(retries+1)
    finally:
        regenerate = False
        with Image.open(sfinge.file_path) as fingerprint:
            corners = itertools.product((0,fingerprint.width-1), (0, fingerprint.height-1))
            pixels = fingerprint.load()

            def is_dark(corner):
                return pixels[corner] < 250

            if all(is_dark(corner) for corner in corners):
                print("Dark background detected, regenerating fingerprint...")
                regenerate = True
        if regenerate:
            generate()
    load_current_fingerprint()
    last_generation_finished = time.time()
    with open('performance.txt', 'a') as log:
        log.write(str(last_generation_finished - last_generation_started) + '\n')


def load_current_fingerprint():
    global image
    with open(sfinge.file_path, 'rb') as file:
        image = file.read()

class Server(BaseHTTPRequestHandler):


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
        self.fingerprint_headers()
        self.wfile.write(image)
        self.wfile.flush()
        self.rfile.close()
        generate_if_needed()

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
                    generate_if_not_already_generating()
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
    load_current_fingerprint()
    ThreadingHTTPServer(('127.0.0.1', 8080), Server).serve_forever()
    #ThreadingHTTPServer(('', 80), Server).serve_forever()
