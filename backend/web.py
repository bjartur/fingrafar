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
from PIL import Image, ImageOps

from fingerprint_generator import Generator
import fingerprint_generator as sfinge

last_generation_started = 0.0
last_generation_finished = 0.0
slide_interval = 30
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
    return time.time() - last_generation_started > 4 * slide_interval

def generate_if_not_already_generating(self):
    global last_generation_started, slide_interval
    if last_generation_started < 1:
        generate()
    elif generation_didnt_finish():
        generate()

def is_file_dark():
    global image
    with Image.open(sfinge.file_path) as fingerprint:
        corners = itertools.product((0,fingerprint.width-1), (0,fingerprint.height-1))
        pixels = fingerprint.load()

        def is_dark(corner):
            return pixels[corner] < 250

        if all(is_dark(corner) for corner in corners):
            print("Dark background detected")
            return True
    return False

def generate(retries=0):
    global last_generation_started, last_generation_finished, image
    this_started = time.time()
    last_generation_started = this_started
    regenerate = None
    try:
        gen = Generator()
        gen.generate()

        regenerate = is_file_dark()

        if regenerate:
            if image == b'':
                if os.path.exists(sfinge.file_path):
                    os.remove(sfinge.file_path)
            else:
                with open(sfinge.file_path + ".old", 'w+b') as f:
                    f.write(image)
                with Image.open(sfinge.file_path + ".old") as fingerprint:
                    ImageOps.mirror(fingerprint).save(sfinge.file_path)

        if os.path.exists(sfinge.file_path):
            with open(sfinge.file_path, 'rb') as f:
                image = f.read()

    except (
        AttributeError,
        ElementNotFoundError,
        TypeError,
        MatchError,
        TimeoutError,
        COMError,
        FileNotFoundError
    ) as e:
        last_generation_started = 0.0
        if not isinstance(e, TimeoutError):
            gen.familicide()
        print()
        print(datetime.now())
        print(type(e))
        print(gen.location)
        print(e)
        if retries < 2:
            generate_if_needed(retries+1)
                
    if regenerate and retries < 2:
        generate(retries+1)
    last_generation_finished = time.time()
    with open('performance.txt', 'a') as log:
        log.write(str(last_generation_finished - last_generation_started) + '\n')


def load_current_fingerprint():
    global image, last_generation_started, last_generation_finished
    if is_file_dark():
        generate()
    with open(sfinge.file_path, 'rb') as f:
        image = f.read()
        last_generation_started = time.time() - 9999
        last_generation_finished = time.time() - 444

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
        self.wfile.write(b"Cache-Control: max-age: 80000 public\r\n")
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
                if self.path.endswith(';id'):
                    self.wfile.write(b'HTTP/1.0 200 OK\r\nContent-Type: application/json\r\nCache-Control: no-cache\r\n\r\n'\
                        + str(last_generation_finished).encode('ascii')
                    )
                    self.wfile.flush()
                    self.rfile.close()
                    generate_if_needed()
                    return
                if image == b'':
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
                self.wfile.write(b'Cache-Control: max-age=800000 public\r\n')
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
