# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import requests
import boto3

dynamodb = boto3.resource('dynamodb')
table_name = os.environ['table_name']
table = dynamodb.Table(table_name)
headers = {'Content-type': 'application/json'}


def lambda_handler(event, context):

    # Fetch the name and the URL of the service from the event
    service_id = event['ID']
    API_URL = event['URL']
    api_call_succeeded = False
  
    # Make a call to the API and get the status of the service
    try:
        requests.get(API_URL, headers=headers, timeout=4)
        api_call_succeeded = True
        service_status = "CLOSED"
    except requests.exceptions.Timeout:
        service_status = "OPEN"
    
    # Update the DynamoDB entry with the new status
    table.update_item(
        Key={"id": service_id},
        UpdateExpression="SET serviceStatus = :s",
        ExpressionAttributeValues={':s': service_status},
        ReturnValues="UPDATED_NEW"
    )

    return {
        'API call succeeded': api_call_succeeded,
        'serviceStatus': service_status,
    }
