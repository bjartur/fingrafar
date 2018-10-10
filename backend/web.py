from http.server import *
from http import HTTPStatus
import shutil

from fingerprint_generator import Generator

class Server(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", 'image/x-windows-bmp')
        self.end_headers()
        file = Generator().generate()
        shutil.copyfileobj(file, self.wfile)
        file.close()

if __name__ == "__main__":
    HTTPServer(('', 80), Server).serve_forever()
