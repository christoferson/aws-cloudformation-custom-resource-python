#!/usr/bin/env python
import json
import boto3
import urllib3

http = urllib3.PoolManager()
s3 = boto3.resource('s3')

def handler(event, context):
    try:
        request_type = event['RequestType']
        bucket = event['ResourceProperties']['BucketName']

        if request_type == 'Delete':
            bucket = s3.Bucket(bucket)
            for obj in bucket.objects.filter():
                s3.Object(bucket.name, obj.key).delete()
        else:
            print(f'Ignoring request. Request Type={request_type}')
        send_cfn_response(event, context, "SUCCESS")
    except Exception as e:
        print(e)
        send_cfn_response(event, context, "FAILED")


def send_cfn_response(event, context, responseStatus):
    response_body = {'Status': responseStatus,
                    'Reason': 'Log stream name: ' + context.log_stream_name,
                    'PhysicalResourceId': context.log_stream_name,
                    'StackId': event['StackId'],
                    'RequestId': event['RequestId'],
                    'LogicalResourceId': event['LogicalResourceId'],
                    'Data': json.loads("{}")}

    response_url = event['ResponseURL']

    print(f'Sending PUT to {response_url}')

    http.request('PUT', event['ResponseURL'], headers={'Content-Type': 'application/json'}, body=json.dumps(response_body))
