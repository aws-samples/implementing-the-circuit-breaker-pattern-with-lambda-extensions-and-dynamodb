# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import json


def lambda_handler(event, context):
    inject_failure = os.environ.get('INJECT_FAILURE')
    http_method = event['httpMethod']
    path = event['path']
   
    if inject_failure:
        response = {
            'statusCode': 500,
            'body': json.dumps({'error': 'Injected failure.'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
        
    else:
        # Define your API routes and responses
        if path == '/api/resource':
            response = {
                'statusCode': 200,
                'body': json.dumps({'message': 'request successful.', 'method': http_method}),
                'headers': {
                    'Content-Type': 'application/json'
                }
            }

        elif http_method == 'GET' and path == '/api/resource/health':
            response = {
                'statusCode': 200,
                'body': json.dumps({'Status': 'UP'}),
                'headers': {
                    'Content-Type': 'application/json'
                }
            }
        else:
            response = {
                'statusCode': 404,
                'body': json.dumps({'error': 'Route not found.'}),
                'headers': {
                    'Content-Type': 'application/json'
                }
            }
    
    return response
