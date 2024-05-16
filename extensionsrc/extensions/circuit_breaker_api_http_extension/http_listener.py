# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Event, Thread
from cachetools import cached, TTLCache
import boto3

# Initializing DDB client
dynamodb = boto3.resource('dynamodb')
table_name = os.environ['table_name']
ttl_value = os.environ['ttl']
table = dynamodb.Table(table_name)

""" Demonstrates code to set up an HTTP listener and receive events
"""

RECEIVER_NAME = "sandbox"
LOCAL_DEBUGGING_IP = "127.0.0.1"
RECEIVER_PORT = 4243


def get_listener_address():
    return RECEIVER_NAME if ("true" != os.getenv("AWS_SAM_LOCAL")) else LOCAL_DEBUGGING_IP


def http_server_init(queue):
    def handler(*args):
        CircuitBreakerHandler(queue, *args)

    listener_address = get_listener_address()
    print(f"Initializing HTTP Server on {listener_address}:{RECEIVER_PORT}")
    server = HTTPServer((listener_address, RECEIVER_PORT), handler)

    # Ensure that the server thread is scheduled so that the server binds to the port
    # and starts to listen before subscribing to the circuit breaker states and ask for the next event.
    started_event = Event()
    server_thread = Thread(target=serve, daemon=True, args=(started_event, server, listener_address,))
    server_thread.start()
    rc = started_event.wait(timeout=9)
    if rc is not True:
        raise Exception("server_thread has timedout before starting")


# Server implementation
class CircuitBreakerHandler(BaseHTTPRequestHandler):
    def __init__(self, queue, *args):
        self.queue = queue
        BaseHTTPRequestHandler.__init__(self, *args)
            
    def do_GET(self):
        circuit_state = ddb_response()
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"data": circuit_state}).encode('utf-8'))


# Server thread
def serve(started_event, server, listener_name):
    # Notify that this thread is up and running
    started_event.set()
    try:
        print(f"Serving HTTP Server on {listener_name}:{RECEIVER_PORT}")
        server.serve_forever()
    except RuntimeError:
        print(f"Error in HTTP server {sys.exc_info()[0]}")
    finally:
        if server:
            server.shutdown()


@cached(cache=TTLCache(maxsize=1, ttl=int(ttl_value)))
def ddb_response():
    response = table.scan()
    return response['Items']
