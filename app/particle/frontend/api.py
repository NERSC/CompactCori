#!/usr/bin/python
"""A parallelized MD simulation in Python written for version 1 of the Compact Cori
project at NERSC.
This runs in O(n^2) time since all particles are compared to one another when
locating in-range neighbors.
Threads in mpi4py are 0-indexed
"""
import argparse
import random
import math
#import numpy as np
import json
import time
import threading
from urllib.parse import urlparse
from http.server import BaseHTTPRequestHandler

def debug(string):
    """Print a message in yellow to STDOUT"""
    CSI="\x1B["
    print(CSI + "31;93m" + "[DEBUG]    " + string + CSI + "31;0m")

def error(err, string):
    """Print a message in red to STDOUT and raise an exception"""
    CSI="\x1B["
    print(CSI + "31;31m" + "[ERROR]    " + string + CSI + "31;0m")
    raise err(CSI + "31;31m" + string + CSI + "31;0m")

class Server(BaseHTTPRequestHandler):
    global endpoint
    def do_GET(self):
        """Handle GET requests to the API endpoint"""
        parsed_path = urlparse(self.path)
        if "/api/v1/get_particles" in parsed_path:
            message = endpoint
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(message.encode("utf-8"))
        else:
            debug("GET request sent to " + str(parsed_path))

    def do_POST(self):
        """Handle POST requests to the API endpoint"""
        parsed_path = urlparse(self.path)
        if "/api/v1/post_parameters" in parsed_path:
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(length).decode("utf-8")
            print("post_data: " + post_data)
            pass
        else:
            debug("POST request sent to " + str(parsed_path))

def main():
    from http.server import HTTPServer
    server = HTTPServer(("127.0.0.1", 8080), Server)
    print("Starting server, ^c to exit")

    threading.Thread(target=server.serve_forever).start()

    global endpoint
    endpoint = "{}"

    print("Server started")

    particles = []
    particles.append( {"particle_id" : 0, "position" : [0.5,0.5,0.5], "velocity" : [0.1,0.1,0.1] } )
    particles.append( {"particle_id" : 1, "position" : [0.0,0.5,0.5], "velocity" : [0.1,0.1,0.1] } )

    icount = 0
    while True:
        icount += 1
        temp_endpoint = "{\"particles\":"
        for particle in particles:
           particle['position'][0] += particle['velocity'][0]
           particle['position'][0] %= 1
           particle['position'][1] += particle['velocity'][1]
           particle['position'][1] %= 1
           particle['position'][2] += particle['velocity'][2]
           particle['position'][2] %= 1
        temp_endpoint += json.dumps(particles)
        temp_endpoint += "}"
        endpoint = temp_endpoint
        debug("Loop count "+str(icount))
        debug("Loop count "+endpoint)

if __name__ == "__main__":
    main()
