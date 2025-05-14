# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import json
import os
import http.client
import requests

headers = {'Content-type': 'application/json'}
# Fetch environment variables for the name and the URL of the service
service_name = os.environ['service_name']
API_URL = os.environ['API_URL']


def lambda_handler(event, context):
    
    # Create a HTTP connection to the extension with the correct host and port
    conn = http.client.HTTPConnection('sandbox', 4243)
    conn.request('GET', "/")
    
    response = conn.getresponse().read().decode()
    status_list = json.loads(response).get("data")
    conn.close()
    # Looping through the status list to find the index of the service status
    indexForService = None
    for index, status_dict in enumerate(status_list):
        if status_dict.get("id") == service_name:
            indexForService = index

    # If available, get the service status        
    if indexForService is not None:
        service_status = status_list[indexForService].get("serviceStatus")
    else:
        raise KeyError("Specified service ID not found in DynamoDB")
    
    # Logic depending on service status
    if service_status == 'CLOSED':
        response = requests.get(API_URL, headers=headers)
        http_status_code = response.status_code
        message = response.json().get("message")
    else:
        http_status_code = 500
        message = "Service is not closed"
        
    return {
        'status code': http_status_code,
        'Response from API': message
    }
