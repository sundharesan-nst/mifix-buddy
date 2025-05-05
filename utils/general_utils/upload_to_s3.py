# upload_to_s3.py
# Purpose: Upload PDF documents from local folder to S3 bucket knowledge_documents folder

import os
import glob
import boto3
from dotenv import load_dotenv, find_dotenv

def load_environment():
    """Load environment variables from .env file"""
    load_dotenv(find_dotenv(), override=True)
    
    # AWS S3 Configuration
    aws_config = {
        'region': os.getenv('AWS_REGION'),
        'access_key': os.getenv('AWS_ACCESS_KEY_ID'),
        'secret_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'bucket_name': os.getenv('S3_BUCKET_NAME')
    }
    
    return aws_config

def get_s3_client(aws_config):
    """Initialize and return an S3 client"""
    return boto3.client(
        service_name='s3',
        region_name=aws_config['region'],
        aws_access_key_id=aws_config['access_key'],
        aws_secret_access_key=aws_config['secret_key']
    )

def get_existing_s3_files(s3_client, bucket_name, s3_folder):
    """Get list of files already in S3 folder"""
    existing_files = set()
    
    try:
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=f"{s3_folder}/"
        )
        
        if 'Contents' in response:
            for item in response['Contents']:
                existing_files.add(os.path.basename(item['Key']))
            print(f"Found {len(existing_files)} existing files in S3 folder '{s3_folder}'")
        else:
            print(f"No files found in S3 folder '{s3_folder}'")
    except Exception as e:
        print(f"Error fetching existing files: {e}")
    
    return existing_files

def upload_new_docs_to_s3(local_directory, s3_folder):
    """Upload only new PDF files from local directory to S3 bucket folder"""
    # Load environment variables
    aws_config = load_environment()
    bucket_name = aws_config['bucket_name']
    
    # Get S3 client
    s3_client = get_s3_client(aws_config)
    
    # Get list of files already in S3
    existing_files = get_existing_s3_files(s3_client, bucket_name, s3_folder)
    
    # Get list of local files
    file_paths = glob.glob(os.path.join(local_directory, "*.pdf"))
    print(f"Found {len(file_paths)} PDF files in local directory '{local_directory}'")
    
    # Filter to only new files
    new_files = []
    for file_path in file_paths:
        file_name = os.path.basename(file_path)
        if file_name not in existing_files:
            new_files.append(file_path)
    
    print(f"Found {len(new_files)} new files to upload")
    
    # Upload new files
    uploaded_files = []
    for file_path in new_files:
        file_name = os.path.basename(file_path)
        s3_key = f"{s3_folder}/{file_name}"
        
        try:
            print(f"Uploading {file_name} to s3://{bucket_name}/{s3_key}")
            s3_client.upload_file(file_path, bucket_name, s3_key)
            print(f"Successfully uploaded {file_name}")
            uploaded_files.append(file_path)
        except Exception as e:
            print(f"Error uploading {file_name}: {e}")
    
    print(f"Upload complete. {len(uploaded_files)} new files uploaded to S3 bucket")
    return uploaded_files

def read_documents_from_s3(s3_folder, specific_files=None):
    """
    Read documents from S3 bucket folder
    Returns list of tuples (document_text, filename)
    If specific_files is provided, only read those files
    """
    import io
    from PyPDF2 import PdfReader
    
    # Load environment variables
    aws_config = load_environment()
    bucket_name = aws_config['bucket_name']
    
    # Get S3 client
    s3_client = get_s3_client(aws_config)
    
    documents = []
    try:
        if specific_files is None:
            # List all objects in the specified folder
            response = s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=f"{s3_folder}/"
            )
            
            if 'Contents' not in response:
                print(f"No files found in s3://{bucket_name}/{s3_folder}/")
                return documents
            
            file_keys = [obj['Key'] for obj in response['Contents'] 
                        if obj['Key'].lower().endswith('.pdf')]
        else:
            # Use the provided file list
            file_keys = [f"{s3_folder}/{os.path.basename(f)}" for f in specific_files 
                        if os.path.basename(f).lower().endswith('.pdf')]
        
        print(f"Loading {len(file_keys)} PDF files from S3 bucket")
        
        for key in file_keys:
            try:
                # Download file from S3 into memory
                print(f"Processing {key}...")
                response = s3_client.get_object(Bucket=bucket_name, Key=key)
                file_content = response['Body'].read()
                
                # Process PDF
                pdf_file = io.BytesIO(file_content)
                reader = PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()  # Combine all pages into a single string
                
                file_name = os.path.basename(key)
                documents.append((text, file_name))
                print(f"Successfully processed {file_name}")
            except Exception as e:
                print(f"Warning: The file {key} could not be processed. Error: {e}")
    
    except Exception as e:
        print(f"Error accessing S3 bucket: {e}")
    
    return documents


local_directory = "../../docs"  # Your local directory with PDF files
s3_folder = "knowledge_documents"  # Target folder in S3 bucket

# Upload new documents to S3
uploaded_files = upload_new_docs_to_s3(local_directory, s3_folder)

# Read the uploaded documents from S3 (optional)
if uploaded_files:
    documents = read_documents_from_s3(s3_folder, uploaded_files)
    print(f"Successfully read {len(documents)} documents from S3")
else:
    print("No new documents were uploaded, skipping read operation")