import os
import boto3
from io import BytesIO
import botocore

s3 = boto3.resource('s3',
    aws_access_key_id=os.getenv('BUCKETEER_AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('BUCKETEER_AWS_SECRET_ACCESS_KEY'),
)

class FileStore:
    def __init__(self, bucket):
        self.bucket = bucket

    def upload(self, inputStream, fileName):
        try:
            self.bucket.upload_fileobj(inputStream, fileName)
        except botocore.exceptions.ClientError as e:
            raise Exception('Could not upload file', e)

    def download(self, fileName):
        outputStream = BytesIO()
        self.bucket.download_fileobj(fileName, outputStream)
        return outputStream


    def delete_file(self, key):
        try:
            s3.Object(self.bucket.name, key).delete()
        except botocore.exceptions.ClientError as e:
            raise Exception('Could not delete object', e)