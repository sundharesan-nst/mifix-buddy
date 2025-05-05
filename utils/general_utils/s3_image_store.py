import boto3
from botocore.exceptions import ClientError

def check_and_generate_unique_filename(s3_client, bucket, original_filename):
    """
    Check if a file with the given name exists in S3 and generate a unique name if necessary.
    """
    base_name, ext = original_filename.rsplit('.', 1)  # Split into name and extension
    new_name = original_filename
    counter = 1

    while True:
        try:
            # Check if the object exists
            s3_client.head_object(Bucket=bucket, Key=new_name)
            # If exists, modify the name
            new_name = f"{base_name}_{counter}.{ext}"
            counter += 1
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                break  # Object does not exist, use the current name
            else:
                raise  # Other errors should be raised
    return new_name

def upload_to_s3(s3_client, bucket, object_key, file_data):
    """
    Synchronously upload the image to S3.
    """
    try:
        s3_client.put_object(Bucket=bucket, Key=object_key, Body=file_data)
        print(f"Uploaded {object_key} to {bucket}")
    except Exception as e:
        print(f"Error uploading {object_key}: {e}")