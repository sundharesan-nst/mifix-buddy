# process_documents.py
# Purpose: Read PDFs from S3, chunk them with smart chunking, and store chunks back in S3

import os
import json
import boto3
import io
from dotenv import load_dotenv, find_dotenv
import openai
from upload_to_s3 import read_documents_from_s3, get_s3_client, load_environment


load_dotenv(find_dotenv(), override=True)
key = os.getenv('OPENAI_API_KEY')
lm_client = openai.OpenAI(api_key=key)


smart_function = [
    {
        "name": "return_smart_chunks",
        "description": "Function to be used to convert the text into semantically relevant smart chunks.",
        "parameters": {
            "type": "object",
            "properties": {
                "smart_chunks": {
                    "type": "array",
                    "description": "This should be a python list of smart chunks.",
                    "items": {"type": "string"},
                }
            },
            "required": ["smart_chunks"],
        },
    }
]

#Return format for tags function calling
custom_functions_tag = [
    {
        "name": "return_tags",
        "description": "to be used to return list of words/tags.",
        "parameters": {
            "type": "object",
            "properties": {
                "tag_list": {
                    "type": "array",
                    "description": "List of tags directly extracted from the chunks given",
                    "items": {"type": "string"},
                },
            },
            "required": ["tag_list"],
        },
    }
]

# Smart Chunking Function 
def ask_gpt_smart_chunk(text):
    system_message = """You are a smart chunker. You will be given content from a word document. 
    You need to return the data, but divided into chunks - meaning, the chunk you return must encapsulate complete information. 
    You are allowed to return as many chunks as you like. But, you must cover the entire information. 
    The reasons is that I will be feeding this into a vector database for semantic retrival of vectors. 
    By feeding an entire page, the similarity scores are very low for specific queries that are only a fraction of the larger page. 
    But, if I were to auto chunk it by 100 or some words, then there are cases where information could be cut off, etc. 
    Therefore, you must return a list of strings. This is called smart chunking. Finally, remember, what you return, when read, must preserve context. 
    Just returning names, or sentences without any indication of the context or what they represent will be useless. 
    Each chunk must represent the heading Name, and Subheading it was pulled from, so that when we look at it we know exactly the central context from where it was derived from. 
    it should be so good that a reader must be able to put back the original text be piecing the chunks together. that is how good it should be. 
    Each chunk MUST contain the Heading, Scheme Name or subheading from where it was taken from. Otherwise, it will make absolutely no sense when looking at it seperately.

    ***
    **YOU MUST USE ALL DATA FROM GIVEN CONTENT. IF YOU ARE CONFUSED THEN COMPARE THE CONTENT IS GIVEN WITH THE CONTENT YOU ARE RETURNING. CHECK FOR ANY DATA LOSSE. IF YOU FEEL DATA IS MISSING THEN PROCESS BACK**.

    ***
    You'll be returning list of strings (chunks). 
    """

    user_message = "content from page from document below: \n" + text
    msg = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]

    print("-----------------------")
    response = lm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=msg,
        max_tokens=16000,
        temperature=0.0,
        functions=smart_function,
        function_call={"name": "return_smart_chunks"},
    )
    try:
        reply = json.loads(response.choices[0].message.function_call.arguments)[
            "smart_chunks"
        ]
        print(reply)
    except:
        print(reply)
        reply = []

    return reply

## creating Tags
def ask_gpt_tags(smart_chunk, synonums = "No synonyms"):

    print(smart_chunk,'----------- askgpt tags\n\n\n')

    system_message = """You will be given a smart chunk. You must behave as an extremly smart named entity recognition software. Your job is to extract ALL of the entities from the given piece of text. 
    Even if the smart chunk isn't in English, list of entities should be in english. I will use these tags to filter data. return a 'list' of 'string tags'."""
    
    user_message = "Smart Chunk: \n" + smart_chunk
    msg = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]

    print("-----------------------")
    response = lm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=msg,
        max_tokens=6000,
        temperature=0.0,
        seed=1,
        functions=custom_functions_tag,
        function_call={"name": "return_tags"},
    )

    try:
        reply = json.loads(response.choices[0].message.function_call.arguments)[
            "tag_list"
        ]
        print(reply)
    except Exception as e:
        print(e)
        reply = []
    return reply

def split_documents(documents):
    """
    Process documents with smart chunking and tagging
    Returns tags, texts, and metadata lists
    """
    tags = []
    texts = []
    metadata = []

    for doc_text, file_name in documents:
        print(f'Processing document: {file_name}')
        chunks = ask_gpt_smart_chunk(doc_text)
        print(f'Completed Smart Chunking for {file_name}, created {len(chunks)} chunks')
        
        for i, chunk in enumerate(chunks):
            texts.append(chunk)
            print(f'Generating tags for chunk {i+1}/{len(chunks)}')
            chunk_tags = ask_gpt_tags(chunk)
            tags.append(chunk_tags)
            print(f'Generated tags: {chunk_tags}')
            metadata.append(file_name)
            print(f"Added metadata: {file_name}")
    
    return tags, texts, metadata

def get_next_chunk_index(s3_client, bucket_name, smart_chunks_folder):
    """
    Get the next available index for chunk files by checking existing files in S3
    """
    try:
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=f"{smart_chunks_folder}/"
        )
        
        max_index = 0
        if 'Contents' in response:
            for item in response['Contents']:
                file_name = os.path.basename(item['Key'])
                if file_name.startswith('data_obj_') and file_name.endswith('.json'):
                    try:
                        index = int(file_name.replace('data_obj_', '').replace('.json', ''))
                        max_index = max(max_index, index)
                    except ValueError:
                        pass
        
        return max_index + 1
    except Exception as e:
        print(f"Error determining next chunk index: {e}")
        return 1

def save_chunks_to_s3(tags, texts, metadata, s3_folder):
    """
    Save processed chunks to S3 bucket
    """
    # Load environment variables
    aws_config = load_environment()
    bucket_name = aws_config['bucket_name']
    
    # Get S3 client
    s3_client = get_s3_client(aws_config)
    
    # Get next available index for chunk files
    start_index = get_next_chunk_index(s3_client, bucket_name, s3_folder)
    
    # Create data objects
    data_objs = [{"tag": tg, "text": tx, "metadata": mt} for tg, tx, mt in zip(tags, texts, metadata)]
    
    # Upload each data object as a JSON file to S3
    for i, data_obj in enumerate(data_objs):
        file_index = start_index + i
        file_name = f"data_obj_{file_index}.json"
        s3_key = f"{s3_folder}/{file_name}"
        
        try:
            # Convert to JSON string
            json_data = json.dumps(data_obj, indent=4)
            
            # Upload to S3
            s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=json_data,
                ContentType='application/json'
            )
            print(f"Successfully uploaded {file_name} to S3")
        except Exception as e:
            print(f"Error uploading chunk {file_name}: {e}")
    
    print(f"Saved {len(data_objs)} chunk files to S3, starting at index {start_index}")
    return data_objs

def process_and_chunk_documents(s3_input_folder, s3_output_folder, specific_files=None):
    """
    Main function to process documents from S3, chunk them, and save back to S3
    """
    # Read documents from S3
    documents = read_documents_from_s3(s3_input_folder, specific_files)
    print(f"Processing {len(documents)} documents")
    
    if not documents:
        print("No documents to process. Exiting.")
        return []
    
    # Process documents with smart chunking
    tags, texts, metadata = split_documents(documents)
    
    # Save chunks to S3
    data_objs = save_chunks_to_s3(tags, texts, metadata, s3_output_folder)
    
    return data_objs


s3_input_folder = "knowledge_documents"  # Input folder in S3 bucket
s3_output_folder = "smart_chunks"  # Output folder in S3 bucket

# Process and chunk all documents in the input folder
process_and_chunk_documents(s3_input_folder, s3_output_folder)

# Or to process specific files:
# specific_files = ["doc1.pdf", "doc2.pdf"]
# process_and_chunk_documents(s3_input_folder, s3_output_folder, specific_files)