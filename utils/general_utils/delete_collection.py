import weaviate
from weaviate.classes.init import Auth
import weaviate.classes as wvc
import openai
import os
from io import StringIO
from dotenv import load_dotenv, find_dotenv

# Load and override existing environment variables
load_dotenv(find_dotenv(), override=True)

# Access specific environment variables
key = os.getenv('OPENAI_API_KEY')
weaviate_cluster_url = os.getenv('WEAVIATE_URL')
weaviate_api_key = os.getenv('WEAVIATE_API')
collection_name = os.getenv('COLLECTION_NAME')

lm_client = openai.OpenAI(api_key=key)
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=weaviate_cluster_url,  
    auth_credentials=Auth.api_key(weaviate_api_key),  # Replace with your Weaviate Cloud key
    headers={'X-OpenAI-Api-key': key},  # Replace with your OpenAI API key
    skip_init_checks=True
)

client.collections.delete(collection_name)

client.close()