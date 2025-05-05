import boto3
import os
from dotenv import load_dotenv, find_dotenv

# Load and override existing environment variables
load_dotenv(find_dotenv(), override=True)


AWS_S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME') 
AWS_REGION = os.getenv('AWS_REGION')
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')


def empty_bucket():
    print('Starting to empty the S3 bucket...')

    s3 = boto3.resource(
        service_name='s3',
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY
    )

    bucket = s3.Bucket(AWS_S3_BUCKET_NAME)

    # Delete all objects in the bucket
    bucket.objects.all().delete()

    print(f'All contents deleted from bucket: {AWS_S3_BUCKET_NAME}')

if __name__ == '__main__':
    empty_bucket()
