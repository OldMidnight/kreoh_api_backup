import os
import boto3

s3 = boto3.resource('s3',
  aws_access_key_id=os.getenv('BUCKETEER_AWS_ACCESS_KEY_ID'),
  aws_secret_access_key=os.getenv('BUCKETEER_AWS_SECRET_ACCESS_KEY'),
)

bucket = s3.Bucket('bucketeer-29e1dc32-7927-4cf8-b4de-d992075645e0')