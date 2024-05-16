#!/bin/sh
''''exec python -u -- "$0" ${1+"$@"} # '''
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
import os
import sys
from pathlib import Path
from queue import Queue 
# Add lib folder to path to import boto3 library.
# Normally with Lambda Layers, python libraries are put into the /python folder which is in the path.
# As this extension is bringing its own Python runtime, and running a separate process, the path is not available.
# Hence, having the files in a different folder and adding it to the path, makes it available. 
lib_folder = Path(__file__).parent / "lib"
sys.path.insert(0, str(lib_folder))

from circuit_breaker_api_http_extension.http_listener import http_server_init, RECEIVER_PORT
from circuit_breaker_api_http_extension.circuit_breaker_api_client import CircuitBreakerAPIClient
from circuit_breaker_api_http_extension.extensions_api_client import ExtensionsAPIClient

"""Here is the sample extension code that stitches all of this together.
    - The extension will run two threads. The "main" thread, will register to ExtensionAPI and process its invoke and
    shutdown events (see next call). The second "listener" thread will listen for HTTP Post events that deliver log batches.
    - The "listener" thread will place every data batch it receives in a synchronized queue; during each execution slice,
    the "main" thread will make sure to process any event in the queue before returning control by invoking next again.
    - Note that because of the asynchronous nature of the system, it is possible that data for one invoke is
    processed during the next invoke slice. Likewise, it is possible that data for the last invoke is processed during
    the SHUTDOWN event.

"""


class CircuitBreakerAPIHTTPExtension():
    def __init__(self, agent_name, registration_body, subscription_body):
        print(f"Initializing CircuitBreakerAPIExternalExtension {agent_name}")
        self.agent_name = agent_name
        self.queue = Queue()
        self.logs_api_client = CircuitBreakerAPIClient()
        self.extensions_api_client = ExtensionsAPIClient()

        # Register early so Runtime could start in parallel
        self.agent_id = self.extensions_api_client.register(self.agent_name, registration_body)
        print(f"Registered {self.agent_name} with ID {self.agent_id}")

        # Start listening before Circuit Breaker API registration
        http_server_init(self.queue)
        self.logs_api_client.subscribe(self.agent_id, subscription_body)

    def run_forever(self):
        print(f"Serving CircuitBreakerAPIHTTPExternalExtension {self.agent_name}")
        while True:
            resp = self.extensions_api_client.next(self.agent_id)
            # Process the received batches if any.
            while not self.queue.empty():
                batch = self.queue.get_nowait()
                print(f"BATCH RECEIVED: {batch}")


# Register for the INVOKE events from the EXTENSIONS API
_REGISTRATION_BODY = {
    "events": ["INVOKE", "SHUTDOWN"],
}

TIMEOUT_MS = 1000  # Maximum time (in milliseconds) that a batch would be buffered.
MAX_BYTES = 262144  # Maximum size in bytes that the logs would be buffered in memory.
MAX_ITEMS = 10000  # Maximum number of events that would be buffered in memory.

_SUBSCRIPTION_BODY = {
    "destination": {
        "protocol": "HTTP",
        "URI": f"http://sandbox:{RECEIVER_PORT}",
    },
    "types": ["platform", "function"],
    "buffering": {
        "timeoutMs": TIMEOUT_MS,
        "maxBytes": MAX_BYTES,
        "maxItems": MAX_ITEMS
    }
}


def main():
    print(f"Starting Extensions {_REGISTRATION_BODY} {_SUBSCRIPTION_BODY}")
    # Note: Agent name has to be file name to register as an external extension
    ext = CircuitBreakerAPIHTTPExtension(os.path.basename(__file__), _REGISTRATION_BODY, _SUBSCRIPTION_BODY)
    ext.run_forever()


if __name__ == "__main__":
    main()
