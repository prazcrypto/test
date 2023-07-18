import boto3
import gzip
import socket
import json
import requests

session = boto3.Session(
    aws_access_key_id='AKIAWAQ6PTOK372YOZ7D',
    aws_secret_access_key='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'
)

def is_json_valid(json_string):
    try:
        json.loads(json_string)
        return True
    except ValueError:
        return False

def send_log_to_cyberal_server(log_content, cyberal_server_ip, cyberal_server_port):
    try:
        # Send the log content to the Cyberal server using HTTP POST
        response = requests.post(f"http://{cyberal_server_ip}:{cyberal_server_port}", data=log_content)
        if response.status_code == 200:
            print("Log sent successfully to the Cyberal server.")
        else:
            print(f"Failed to send log to the Cyberal server. Status code: {response.status_code}")
    except Exception as e:
        print(f"Failed to send log to Cyberal server: {e}")

def send_log_to_logger(log_content, logger_endpoint):
    try:
        # Send the log content to the logger using HTTP POST
        response = requests.post(logger_endpoint, data=log_content)
        if response.status_code == 200:
            print("Log sent successfully to the logger.")
        else:
            print(f"Failed to send log to the logger. Status code: {response.status_code}")
    except Exception as e:
        print(f"Failed to send log to the logger: {e}")

def retrieve_cloudtrail_logs(bucket_name, cyberal_server_ip, cyberal_server_port, logger_endpoint):
    s3_client = session.client('s3')

    # List all objects in the S3 bucket
    objects = s3_client.list_objects_v2(Bucket=bucket_name)['Contents']

    # Iterate through each object and download its content
    for obj in objects:
        key = obj['Key']

        # Download the object's content
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        log_content = response['Body'].read()

        # Decompress the content if it is gzip compressed
        if response['ContentEncoding'] == 'gzip':
            log_content = gzip.decompress(log_content)

        # Convert the log content to JSON format
        try:
            log_content_json = log_content.decode('utf-8')
            logs = log_content_json.split('\n')
            for log in logs:
                if log and is_json_valid(log):
                    # Forward the log content to the Cyberal server
                    send_log_to_cyberal_server(log, cyberal_server_ip, cyberal_server_port)

                    # Forward the log content to the logger
                    send_log_to_logger(log, logger_endpoint)
        except Exception as e:
            print(f"Error processing log content: {e}")

    print("All logs processed.")

# Usage
bucket_name = 'aws-cloudtrail-logs-413454539669-38ecd5f0'
cyberal_server_ip = ''
# port number here
cyberal_server_port = 443 
logger_endpoint = 'https://loggerip:port/ingest1'

retrieve_cloudtrail_logs(bucket_name, cyberal_server_ip, cyberal_server_port, logger_endpoint)
