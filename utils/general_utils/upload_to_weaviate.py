# weaviate_upload.py
# Purpose: Load smart chunks from S3 and upload to Weaviate collection

import os
import json
import boto3
import weaviate
from weaviate.auth import Auth
import weaviate.classes as wvc
from dotenv import load_dotenv, find_dotenv
from upload_to_s3 import load_environment, get_s3_client

def load_weaviate_config():
    """Load Weaviate configuration from environment variables"""
    load_dotenv(find_dotenv(), override=True)
    
    weaviate_config = {
        'url': os.getenv('WEAVIATE_URL'),
        'api_key': os.getenv('WEAVIATE_API'),
        'openai_key': os.getenv('OPENAI_API_KEY'),
        'collection_name': os.getenv('COLLECTION_NAME')
    }
    
    return weaviate_config

def get_weaviate_client(weaviate_config):
    """Initialize and return a Weaviate client"""
    try:
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=weaviate_config['url'],
            auth_credentials=Auth.api_key(weaviate_config['api_key']),
            headers={'X-OpenAI-Api-key': weaviate_config['openai_key']},
            skip_init_checks=True
        )
        return client
    except Exception as e:
        print(f"Error connecting to Weaviate: {e}")
        return None

def ensure_collection_exists(client, collection_name):
    """Ensure the collection exists in Weaviate, create it if not"""
    try:
        if not client.collections.exists(collection_name):
            client.collections.create(
                name=collection_name,
                vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai(
                    model="ada",
                    model_version="002",
                    vectorize_collection_name=False
                ),
                properties=[
                    wvc.config.Property(
                        name="tag",
                        data_type=wvc.config.DataType.TEXT_ARRAY,
                        vectorize_property_name=True
                    ),
                    wvc.config.Property(
                        name="text",
                        data_type=wvc.config.DataType.TEXT,
                        vectorize_property_name=False
                    ),
                    wvc.config.Property(
                        name="metadata",
                        data_type=wvc.config.DataType.TEXT,
                        vectorize_property_name=False
                    ),
                ]
            )
            print(f"Created collection '{collection_name}'")
        else:
            print(f"Collection '{collection_name}' already exists")
        
        return True
    except Exception as e:
        print(f"Error creating collection: {e}")
        return False

def load_chunks_from_s3(s3_folder):
    """Load chunk files from S3 bucket folder"""
    # Load environment variables
    aws_config = load_environment()
    bucket_name = aws_config['bucket_name']
    
    # Get S3 client
    s3_client = get_s3_client(aws_config)
    
    # List objects in the specified folder
    data_objs = []
    try:
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=f"{s3_folder}/"
        )
        
        if 'Contents' not in response:
            print(f"No files found in s3://{bucket_name}/{s3_folder}/")
            return data_objs
        
        file_keys = [obj['Key'] for obj in response['Contents'] 
                   if obj['Key'].lower().endswith('.json')]
        
        print(f"Found {len(file_keys)} chunk files in S3 bucket")
        
        for key in file_keys:
            try:
                # Download file from S3
                response = s3_client.get_object(Bucket=bucket_name, Key=key)
                file_content = response['Body'].read().decode('utf-8')
                
                # Parse JSON
                data_obj = json.loads(file_content)
                data_objs.append(data_obj)
                print(f"Loaded {os.path.basename(key)}")
            except Exception as e:
                print(f"Error loading {key}: {e}")
    
    except Exception as e:
        print(f"Error accessing S3 bucket: {e}")
    
    return data_objs

def upload_to_weaviate(data_objs, collection_name):
    """Upload data objects to Weaviate collection"""
    # Load Weaviate configuration
    weaviate_config = load_weaviate_config()
    
    # Get Weaviate client
    client = get_weaviate_client(weaviate_config)
    if not client:
        print("Failed to connect to Weaviate. Exiting.")
        return False
    
    try:
        # Ensure collection exists
        if not ensure_collection_exists(client, collection_name):
            print("Failed to create or verify collection. Exiting.")
            client.close()
            return False
        
        # Access the collection
        collection = client.collections.get(collection_name)
        
        # Insert objects in batches
        if data_objs:
            try:
                collection.data.insert_many(data_objs)
                print(f"Successfully inserted {len(data_objs)} objects into Weaviate collection '{collection_name}'")
                return True
            except Exception as e:
                print(f"Error inserting data into Weaviate: {e}")
                return False
        else:
            print("No data objects to insert")
            return False
    
    finally:
        if client:
            client.close()

def process_chunks_to_weaviate(s3_folder):
    """
    Main function to load chunks from S3 and upload to Weaviate
    """
    # Load Weaviate configuration
    weaviate_config = load_weaviate_config()
    collection_name = weaviate_config['collection_name']
    
    # Load chunks from S3
    data_objs = load_chunks_from_s3(s3_folder)
    print(f"Loaded {len(data_objs)} data objects from S3")
    
    if not data_objs:
        print("No data objects to process. Exiting.")
        return False
    
    # Upload to Weaviate
    success = upload_to_weaviate(data_objs, collection_name)
    
    return success


s3_chunks_folder = "smart_chunks"  # S3 folder containing chunk files

# Process chunks from S3 to Weaviate
success = process_chunks_to_weaviate(s3_chunks_folder)

if success:
    print("Successfully processed chunks to Weaviate")
else:
    print("Failed to process chunks to Weaviate")