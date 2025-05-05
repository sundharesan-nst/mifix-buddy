import weaviate
import openai
from weaviate.classes.init import Auth
from flask_cors import CORS
import json
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
from passlib.hash import pbkdf2_sha256 as sha256
from flask import Flask, request, redirect, render_template, url_for, flash, session, jsonify
from passlib.hash import pbkdf2_sha256 as sha256
import boto3
from functools import wraps
from datetime import datetime
from boto3.dynamodb.conditions import Key
import requests
import os
from dotenv import load_dotenv, find_dotenv
import logging

#Importing General Utility Functions
from utils.general_utils.router import router_llm
from utils.general_utils.level0_router import router_llm_l0
from utils.general_utils.standalone import format_query
from utils.general_utils.ask_tags import ask_gpt_tags
from utils.general_utils.pre_screen import pre_screen
from utils.general_utils.generate_using_vdb import ask_gpt_fast
from utils.general_utils.parameter_extractor import extract_parameters
from utils.general_utils.process_image import desc_image
from utils.general_utils.s3_image_store import check_and_generate_unique_filename, upload_to_s3

#Importing Collection APIs based utility Functions 
from utils.collection_utils.collection_router import collection_router
from utils.collection_utils.attendance import attendance_status, attendance_marking
from utils.collection_utils.collection_target import collection_target_status
from utils.collection_utils.scheduled_groups import group_schedule_status
from utils.collection_utils.incomplete_transactions import incomplete_transactions_status
from utils.collection_utils.deposit_details import deposit_details_status
from utils.collection_utils.group_prospects import group_prospect_details
from utils.collection_utils.qr_generation import generate_digital_transaction_status
from utils.collection_utils.update_proof_of_trans import update_proof_of_transaction
from utils.collection_utils.reschedule_cust import reschedule_customer

#Imporing JLG APIs based utility Functions
from utils.jlg_utils.jlg_router import jlg_router
from utils.jlg_utils.generate_otp import generate_otp_status
from utils.jlg_utils.validate_otp import validate_otp_status
from utils.jlg_utils.upload_customer_documents import upload_customer_documents_status
from utils.jlg_utils.upload_household_documents import upload_household_documents_status
from utils.jlg_utils.upload_bank_documents import upload_bank_documents_status
from utils.jlg_utils.submit_l1_additional_details import submit_l1_additional_details_status
from utils.jlg_utils.l1_submitted_customer_list import get_l1_submitted_customers_list_status
from utils.jlg_utils.submit_household_details import submit_household_details_status
from utils.jlg_utils.submit_update_household_member import submit_update_household_member_details_status
from utils.jlg_utils.submit_amenities import submit_amenities_status
from utils.jlg_utils.submit_assets import submit_assets_status
from utils.jlg_utils.submit_expenses import submit_expenses_status
from utils.jlg_utils.eligibility_check import eligibility_check_status
from utils.jlg_utils.calculate_emi import calculate_emi_status
from utils.jlg_utils.l2_submitted_customers import get_l2_submitted_customers_list_status
from utils.jlg_utils.get_bank_details import get_bank_details_status
from utils.jlg_utils.submit_bank_details import submit_bank_details_status
from utils.jlg_utils.l3_submitted_customers_list import get_l3_submitted_customers_list_status
from utils.jlg_utils.retrigger_ekyc import retrigger_ekyc_status
from utils.jlg_utils.retry_credit_check import retry_credit_check_status
from utils.jlg_utils.create_group import create_group_status


from flask_sqlalchemy import SQLAlchemy


# Load and override existing environment variables
load_dotenv(find_dotenv(), override=True)

# Access specific environment variables
key = os.getenv('OPENAI_API_KEY')
weaviate_cluster_url = os.getenv('WEAVIATE_URL')
weaviate_api_key = os.getenv('WEAVIATE_API')
collection_name = os.getenv('COLLECTION_NAME')
aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
folder_id = os.getenv('FOLDER_ID')
login_credentials_table = os.getenv('LOGIN_CREDENTIALS_TABLE')
chat_table = os.getenv('CHAT_TABLE')
bucket_name = os.getenv('S3_BUCKET_NAME')
aws_region = os.getenv('AWS_REGION')
BASE_URL = os.getenv('APIs_BASE_URL')
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
print("read credentials")

app = Flask(__name__)
CORS(app)

#connect with db
    # db_url1 = f"postgresql+psycopg2://{DB_PARAMS1['user']}:{DB_PARAMS1['password']}@{DB_PARAMS1['host']}:{DB_PARAMS1['port']}/{DB_PARAMS1['dbname']}"

    # engine1 = create_engine(db_url1)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://darwinadmin:DarwinAdmin2023@65.0.116.9:5432/darwinqa'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Set a secret key for session handling
app.secret_key = os.getenv('APP_SECRET_KEY')

lm_client = openai.OpenAI(api_key=key)

# Define the required scopes
SCOPES = ['https://www.googleapis.com/auth/drive']

# Authenticate using service account
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

print('here1')

collection_route_map = {
    1: '/api/v1/attendance/status',
    2: '/api/v1/attendance/mark',
    3: '/dms/1.0/collection-target',
    4: '/dms/1.0/group-scheduled',
    5: '/dms/1.0/incomplete_transactions',
    6: '/cts/1.0/deposit_details',
    7: '/dms/1.0/group-prospect-detail',
    8: '/cts/1.0/generate-digital-transaction',
    9: '/cts/1.0/update_proof_of_transaction',
    10: '/dms/1.0/schedule/reschedule-customer'
}

jlg_route_map = {
    1: '/main/customer/generateOTP',
    2: '/main/customer/validateOTP',
    3: '/main/customer/upload',
    4: '/main/household/upload',
    5: '/main/bank/upload',
    6: '/main/customer/submitDetails',
    7: '/main/customer/singleList',
    8: '/main/customer/members',
    9: '/main/customer/household/submit',
    10: '/main/customer/amenities',
    11: '/main/customer/assets',
    12: '/main/customer/expenses',
    13: '/main/customer/eligibility',
    14: '/main/customer/calculate',
    15: '/main/customer/l2List',
    16: '/data/v1/master/ifsc',
    17: '/main/customer/account',
    18: '/main/customer/l3List',
    19: '/main/customer/retriggerEKYC',
    20: '/main/customer/credit-check',
    21: '/main/group/create',
}

collection_function_map = {
    1: attendance_status,
    2: attendance_marking,
    3: collection_target_status,
    4: group_schedule_status,
    5: incomplete_transactions_status,
    6: deposit_details_status,
    7: group_prospect_details,
    8: generate_digital_transaction_status,
    9: update_proof_of_transaction,
    10: reschedule_customer,
}

jlg_function_map = {
    1: generate_otp_status,
    2: validate_otp_status,
    3: upload_customer_documents_status,
    4: upload_household_documents_status,
    5: upload_bank_documents_status,
    6: submit_l1_additional_details_status,
    7: get_l1_submitted_customers_list_status,
    8: submit_update_household_member_details_status,
    9: submit_household_details_status,
    10: submit_amenities_status,
    11: submit_assets_status,
    12: submit_expenses_status,
    13: eligibility_check_status,
    14: calculate_emi_status,
    15: get_l2_submitted_customers_list_status,
    16: get_bank_details_status,
    17: submit_bank_details_status,
    18: get_l3_submitted_customers_list_status,
    19: retrigger_ekyc_status,
    20: retry_credit_check_status,
    21: create_group_status,
}

#Build the Drive service
service = build('drive', 'v3', credentials=creds)

def get_file_link(folder_id, file_name):
    query = f"'{folder_id}' in parents and name='{file_name}'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])
    
    if not items:
        print(f"File '{file_name}' not found.")
        return None
    else:
        file_id = items[0]['id']
        return f"https://drive.google.com/file/d/{file_id}/view"


folder_id = folder_id

print('here2')

weaviate_client = weaviate.connect_to_weaviate_cloud(
    cluster_url = weaviate_cluster_url,  
    auth_credentials=Auth.api_key(weaviate_api_key),  
    headers={'X-OpenAI-Api-key': key}  
)

print('here3')

def qdb(query, db_client, name, limit=1000):
    print('Inside QDB')
    context = None
    metadata = []
    print(ask_gpt_tags(lm_client, query))
    try:
        # Perform the query using V4 API
        res = db_client.collections.get(name).query.near_text(
            query=ask_gpt_tags(lm_client, query), 
            limit=limit,
            )
        
        context = ""
        metadata = []
        chunk_id = 0
        for obj in res.objects:
            context += "Chunk ID: " + str(chunk_id) + "\n"
            context += obj.properties["text"] + "\n\n"
            metadata.append(obj.properties["metadata"])
            chunk_id += 1
        print(context, metadata)

    except Exception as e:
        print("Exception in DB")
        print(e)
        time.sleep(3)
    return context, metadata

def make_hyperLink(filename, link):
    return f"<a href={link} target='_blank'> {filename}</a>"

def vdb_pipeline(standalone, previous_context):
    context, metadata = qdb(standalone, weaviate_client, collection_name, 5)
    # if we use transcript + additional context, chat, raw question has to be brought in 
    # reply, citations = ask_gpt_fast(question, context, chat)
    #just using standalone with context retrived
    reply, citations = ask_gpt_fast(lm_client, standalone, context, previous_context)

    if citations:
        reply += '\n  Refrences:'

        for file_name in set([metadata[cite] for cite in citations]):
            link = (get_file_link(folder_id, file_name))
            reply += " \n"
            reply += f"{make_hyperLink(file_name,link)}"

    return (reply)

def collection_pipeline(standalone, user_id, latitude, longitude, previous_context, params):
    route, reason = collection_router(lm_client, standalone, previous_context)
    if route == 0:
        print(reason)
        return reason
    print('Reason for choosing ', collection_route_map[route], ' route: ', reason)


    collection_params = {
        1: {
            "needs_extraction": False,
            "parameters": {
                "user_id": user_id  # Directly available in the pipeline
            }
        },
        2: {
            "needs_extraction": False,
            "parameters": {
                "user_id": user_id,  # Directly available in the pipeline
                "eventData": {
                    "latitude": latitude,  # Provided directly in the pipeline
                    "longitude": longitude  # Provided directly in the pipeline
                }
            }
        },
        3: {
            "needs_extraction": False,
            "parameters": {
                "user_id": user_id  # Directly available in the pipeline
            }
        },
        4: {
            "needs_extraction": False,
            "parameters": {
                "user_id": user_id  # Directly available in the pipeline
            }
        },
        5: {
            "needs_extraction": False,
            "parameters": {
                "user_id": user_id  # Directly available in the pipeline
            }
        },
        6: {
            "needs_extraction": False,
            "parameters": {
                "user_id": user_id  # Directly available in the pipeline
            }
        },
        7: {
    "needs_extraction": True,
    "structure": {
        "group_id": "string"  # Example: The group ID must be a string
        }
    },
    8: {
        "needs_extraction": True,
        "structure": {
            "customer_id": "string",  # Example: The customer ID as a string
            "amount": "float"  # Example: Amount as a float or number
        }
    },
    9: {
        "needs_extraction": True,
        "structure": {
            "custId": "string",  # Example: Customer ID
            "proofOfTransactions": ["image path/s"],  # Example: A list of image paths
            "transactionDate": "date"  # Example: A date string in YYYY-MM-DD format
        }
    },
    10: {
        "needs_extraction": True,
        "structure": {
            "customer_id": "string",  # Example: The customer ID as a string
            "reason": "string",  # Example: Reason as a string
            "date": "date"  # Example: A date string in YYYY-MM-DD format
        }
    }

    }
    
    if not collection_params[route]['needs_extraction']:
        payload = collection_params[route]['parameters']
    else: 
        payload, sufficient, reply = extract_parameters(lm_client, standalone, collection_params[route]['structure'], params, previous_context)
        if not sufficient:
            return reply

    # Get the API endpoint
    endpoint = collection_route_map[route]
    # Construct the full URL
    url = f"{BASE_URL}{endpoint}"

    headers = {"Content-Type": "application/json"}

    try:
        # Determine the appropriate HTTP method based on the route
        if route in [1, 3, 4, 5, 6, 7]:  # These use GET
            response = requests.get(url, headers=headers, params=payload).json()
        elif route in [2, 10]:  # These use PUT
            response = requests.put(url, headers=headers, json=payload).json()
        elif route in [8, 9]:  # These use POST
            response = requests.post(url, headers=headers, json=payload).json()
        else:
            raise ValueError(f"Unsupported route: {route}")

        print(response)
        # Call the appropriate function from the function map with the response
        reply = collection_function_map[route](lm_client, standalone, response)

    except requests.exceptions.RequestException as e:
        # Handle any exceptions during the API call
        reply = f"An error occurred while making the API request: {e}"

    return reply

def jlg_pipeline(standalone, user_id, previous_context, params):
    route, reason = jlg_router(lm_client, standalone, previous_context)
    if route == 0:
        print(reason)
        return reason
    print('Reason for choosing ', jlg_route_map[route], ' route: ', reason)

    jlg_params = {
    1: {
        "needs_extraction": True,
        "structure": {
            "phoneNumber": "string"  # Example: Phone number in string format (10-digit numeric)
        }
    },
    2: {
        "needs_extraction": True,
        "structure": {
            "payload": {
                "mobile": "string",  # Example: Phone number as a string
                "otp": "string"  # Example: OTP in string format
            }
        }
    },
    3: {
        "needs_extraction": True,
        "structure": {
            "customerId": "string",  # Example: Customer ID as a string
            "type": "string",  # Example: Document type as a string
            "files": ["file/image path"]  # Example: A list of uploaded files
        }
    },
    4: {
        "needs_extraction": True,
        "structure": {
            "customerId": "string",  # Example: Customer ID as a string
            "memberId": "string",  # Example: Member ID as a string
            "type": "string",  # Example: Document type as a string
            "files": ["file/image path"]  # Example: A list of uploaded files
        }
    },
    5: {
        "needs_extraction": True,
        "structure": {
            "customerId": "string",  # Example: Customer ID as a string
            "type": "string",  # Example: Document type as a string
            "files": ["file/image path"]  # Example: A list of uploaded files
        }
    },
    6: {
    "needs_extraction": True,
    "structure": {
        "payload": {
            "customerId": "string",  # Example: Customer ID in string format
            "demographics": {
                "fullName": "string",  # Example: Full name as a string
                "dob": "date",  # Example: Date of birth in 'YYYY-MM-DD' format
                "gender": "string",  # Example: Gender as a string (e.g., "Male", "Female", "Other")
                "mobileNumber": "string",  # Example: Mobile number as a string (10-digit numeric)
                "maritalStatus": "string",  # Example: Marital status as a string (e.g., "Single", "Married")
                "educationalQualification": "string",  # Example: Education qualification as a string
                "natureOfResidence": "string"  # Example: Residence type as a string (e.g., "Owned", "Rented")
                }
            }
        }
    },
    7: {
        "needs_extraction": False,
        "structure": {
            'userId' : user_id      
        }
    },
    8: {
    "needs_extraction": True,
    "structure": {
        "payload": {
            "customerId": "string",
            "members": [
                {
                    "id": "string",
                    "fullName": "string",
                    "gender": "string",
                    "dob": "date",
                    "relationship": "string",
                    "isNominee": "boolean",
                    "incomeDetails": [
                        {
                            "id": "string",
                            "type": "string",
                            "employmentType": "string",
                            "occupation": "string",
                            "designation": "string",
                            "income": "float"
                        }
                    ],
                    "documents": {
                        "kycDocuments": "string",
                        "customerPhoto": "string"
                        }
                    }
                ]   
            }
        }
    },
    9: {
        "needs_extraction": True,
        "structure": {
            "payload": {
                "customerId": "string",
                "consent": "boolean",
                "optedLoan": {
                    "amount": "float",
                    "tenure": "integer",
                    "purpose": "string",
                    "netWorth": "float"
                }
            }
        }
    },
    10: {
        "needs_extraction": True,
        "structure": {
            "payload": {
                "customerId": "string",
                "amenities": [
                    {
                        "code": "string",
                        "value": "string"
                    }
                ]
            }
        }
    },
    11: {
        "needs_extraction": True,
        "structure": {
            "payload": {
                "customerId": "string",
                "assets": [
                    {
                        "category": "string",
                        "code": "string",
                        "value": "float"
                    }
                ]
            }
        }
    },
    12: {
        "needs_extraction": True,
        "structure": {
            "payload": {
                "customerId": "string",
                "expenses": [
                    {
                        "type": "string",
                        "code": "string",
                        "value": "float"
                    }
                ]
            }
        }
    },
    13: {
        "needs_extraction": True,
        "structure": {
            "customerId": "string"
        }
    },
    14: {
        "needs_extraction": True,
        "structure": {
            "payload": {
                "customerId": "string",
                "amount": "float",
                "tenure": "integer"
            }
        }
    },
    15: {
        "needs_extraction": False,
        "structure": {
            'userId' : user_id      
        }
    },
    16: {
        "needs_extraction": True,
        "structure": {
            "ifsc": "string"
        }
    },
    17: {
        "needs_extraction": True,
        "structure": {
            "payload": {
                "customerId": "string",
                "disbursementPreference": "string",
                "consent": "boolean",
                "bankDetails": {
                    "accountHolderName": "string",
                    "accountNumber": "string",
                    "reAccNumber": "string",
                    "ifsc": "string",
                    "branchName": "string",
                    "branchAddress": "string",
                    "proofOfAccount": "string"
                }
            }
        }
    },
    18: {
        "needs_extraction": False,
        "structure": {
            'userId' : user_id      
        }
    },
    19: {
    "needs_extraction": True,
    "structure": {
        "payload": {
            "customerId": "string",
            "ekycRequests": [
                    {
                        "id": "string",
                        "aadharNumber": "string",
                        "transactionId": "string"
                    }
                ]
            }
        }
    },
    20: {
        "needs_extraction": True,
        "structure": {
            "customerId": "string"
        }
    },
    21: {
        "needs_extraction": True,
        "structure": {
            "payload": {
                "customers": [
                    "string"
                ],
                "groupHead": "string",
                "villageName": "string"
            }
        }
    }
}

    if not jlg_params[route]['needs_extraction']:
        payload = jlg_params[route]['structure']
    else: 
        payload, sufficient, reply = extract_parameters(lm_client, standalone, jlg_params[route]['structure'], params, previous_context)
        if not sufficient:
            return reply

    # Get the API endpoint
    endpoint = jlg_route_map[route]
    # Construct the full URL
    url = f"{BASE_URL}{endpoint}"

    headers = {"Content-Type": "application/json"}

    try:
        # Determine the appropriate HTTP method based on the route
        if route in [7, 15, 18]:  # These use GET
            response = requests.get(url, headers=headers, params=payload).json()
        elif route in [8]:  # These use PUT
            response = requests.put(url, headers=headers, json=payload).json()
        elif route in [6, 13, 14, 16, 20, 1, 2, 3, 4, 5, 9, 10, 11, 12, 17, 19, 21]:  # These use POST
            response = requests.post(url, headers=headers, json=payload).json()
        else:
            raise ValueError(f"Unsupported route: {route}")

        print(response)
        # Call the appropriate function from the function map with the response
        reply = jlg_function_map[route](lm_client, standalone, response)

    except requests.exceptions.RequestException as e:
        # Handle any exceptions during the API call
        reply = f"An error occurred while making the API request: {e}"
        
    return reply

# Initialize an S3 client resource
print('Initializing S3 client resource...')
s3_client = boto3.client(
    's3',
    region_name=aws_region,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)
print('S3 client resource initialized')

# Initialize a DynamoDB resource
print('Initializing DynamoDB resource...')
dynamodb = boto3.resource(
    'dynamodb',
    region_name=aws_region,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key
)
print('DynamoDB resource initialized')

print('Initializing DynamoDB tables...')
table = dynamodb.Table(login_credentials_table)  # Login Credentials table
print('Main table initialized')
chat_table = dynamodb.Table(chat_table) # chats stored table
print('Chat table initialized')

# Decorator to restrict access to authenticated users
print('Defining login_required decorator...')
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
print('Decorator defined')

@app.route('/', methods=['GET'])
def index():
    print('Rendering signup page')
    return render_template('signup.html')  # Ensure you have a signup.html template in your templates directory

@app.route('/signup', methods=['POST'])
def signup():
    print('Entered /signup route')
    user_id = request.form.get('user_id')
    password = request.form.get('password')
    print(f'User ID received: {user_id}')
    hashed_password = sha256.hash(password)  # Hashing the password before storing it

    try:
        print('Checking if user ID already exists...')
        response = table.get_item(Key={'user_id': user_id})
        if 'Item' in response:
            print('User ID already registered')
            flash("User ID already registered. Please log in.")
            return redirect(url_for('index'))

        print('Adding new user to DynamoDB...')
        response = table.put_item(
            Item={
                'user_id': user_id,
                'password': hashed_password
            }
        )
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print('Signup successful')
            flash("Signup successful! Please log in.")
            return redirect(url_for('login'))
        else:
            print('Failed to add user to DynamoDB')
            return "Failed to add user to DynamoDB", 500
    except Exception as e:
        print(f"Error adding user to DynamoDB: {e}")
        return f"Error adding user to DynamoDB: {str(e)}", 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    print('Entered /login route')
    if request.method == 'POST':
        print('Processing POST request in /login')
        user_id = request.form.get('user_id')
        password = request.form.get('password')
        print(f'User ID received for login: {user_id}')

        try:
            print('Fetching user from DynamoDB...')
            response = table.get_item(Key={'user_id': user_id})
            user = response.get('Item')
            
            if user:
                print('User found in database')
            else:
                print('User not found in database')

            if user and sha256.verify(password, user['password']):
                print('Password verification successful')
                session['user_id'] = user_id
                flash("Login successful!")
                return redirect(url_for('search'))
            else:
                print('Invalid user ID or password')
                flash("Invalid user ID or password!")
                return redirect(url_for('login'))
        except Exception as e:
            print(f"Error fetching user data: {e}")
            return f"Error fetching user data: {str(e)}", 500

    print('Rendering login page')
    return render_template('login.html')

@app.route('/search', methods=['POST', 'GET'])
@login_required
def search():
    print('Entered /search route')
    user_id = session.get('user_id')
    print(f'User ID from session: {user_id}')
    
    if request.method == 'POST':
        print('Processing POST request in /search')
        try:
            # Use request.form for text inputs
            print('---------------------------------------------')
            print(request.form)
            imgCount = request.form.get('countImg')
            print('Images_Count: ', imgCount)
            print('---------------------------------------------')
            latitude = request.form.get('latitude')
            longitude = request.form.get('longitude')
            question = request.form.get('question')
            print(f'Question received: {question}')
            print(f'Location is: [{latitude, longitude}]')
            
            images = []
            file_names = []

            if imgCount:
                print('Entered imgCount block')
                print(f"imgCount: {imgCount}")  # Debug imgCount

                images = []
                file_names = []

                for i in range(1, int(imgCount) + 1):
                    img_key = f'img_{i}'  # Dynamically generate the key name (img_1, img_2, ...)

                    image = request.files.get(img_key)  # Retrieve the file

                    # Debug print for current iteration
                    print(f"Looking for key: {img_key}")
                    print(f"Image: {image}")

                    if image:
                        images.append(image)
                        file_names.append(image.filename)  # Use the embedded filename from the file object
                        print(f"Image {img_key}: {image.filename}")  # Print the filename

                print("Received Images:", images)
                print("Received File Names:", file_names)

            image_descriptions = ''
            if images:
                for i, image in enumerate(images):
                    print(f'Image received: {file_names[i]}')

                    # Generate unique filename
                    unique_filename = check_and_generate_unique_filename(s3_client, bucket_name, file_names[i])
                    print(f"Unique filename generated: {unique_filename}")

                    # Upload to S3
                    upload_to_s3(s3_client, bucket_name, unique_filename, image.read())

                    description = desc_image(lm_client, image)
                    image_descriptions += f"Attached Image {unique_filename} (Path: https://{bucket_name}.s3.{aws_region}.amazonaws.com/{unique_filename}) Description: {description}\n"
                print(image_descriptions)

            question = image_descriptions + 'Question: ' + question
            print(question)

            if not question:
                print('No question provided')
                return jsonify({'answer': "No question provided."}), 400

            print('Querying chat_table for chat history...')
            response = chat_table.query(
                KeyConditionExpression=Key('user_id').eq(user_id),
                ScanIndexForward=True
            )
            chat_items = response.get('Items', [])

            # Limit to the last 25 interactions
            chat_items = chat_items[-25:] if len(chat_items) > 25 else chat_items

            print(f'Number of chat history items retrieved: {len(chat_items)}')

            chat = '\n'.join(f"User: {item['question']}\nAI Assistant: {item['answer']}" for item in chat_items)
            chat += 'User: ' + question + '\n'

            print('Calling pre_screen function...')
            reply, sufficient, esclation = pre_screen(lm_client, chat, question)
            print(f'pre_screen result: sufficient={sufficient}')

            if esclation:
                sufficient = True
                print("esclation has been requested")
                try:
                    print('Requesting esclation...')
                    #request_esclation(lm_client, user_id, chat)
                    return jsonify({'answer': "Esclation has been requested."})
                except Exception as e:
                    print(f"Error in /search route: {e}")
                    return jsonify({'answer': "can't find answer due to system error"})

            if not sufficient:
                print('Generating standalone query with format_query function...')
                previous_context, parameters, standalone = format_query(lm_client, chat, question)
                print('previous_context: ', previous_context)
                print('Standalone: ', standalone)
                print('Parameters: ', parameters)
                print('Routing')
                route, reason = router_llm_l0(lm_client, standalone, previous_context)
                print('l0-route:', route)
                print('l0-routing reason:', reason)
                if route == 1:
                    print('VDB it is')
                    reply = vdb_pipeline(standalone, previous_context)
                elif route == 2:
                    print('Collection API Question')
                    reply = collection_pipeline(standalone, user_id, latitude, longitude, previous_context, parameters)
                elif route == 3:
                    print('JLG APIs Question')
                    reply = jlg_pipeline(standalone, user_id, previous_context, parameters)
                else:
                    reply = 'Sorry but your query is out of the scope of my capabilities, want me to connect you to Support?'

            if not reply:
                print('No answer generated')
                chat += "System: No answer generated.\n"
                return jsonify({'answer': "No answer available for this question."})

            print('Appending generated reply to chat log')
            reply = 'AI Assistant: \n\n' + reply + '\n\n'

            timestamp = datetime.utcnow().isoformat()
            print(f'Saving chat entry with timestamp: {timestamp}')

            chat_table.put_item(
                Item={
                    'user_id': user_id,
                    'timestamp': timestamp,
                    'question': question,
                    'answer': reply
                }
            )
            print('Chat entry saved successfully')
            return jsonify({'answer': reply})

        except Exception as e:
            print(f"Error in /search route: {e}")
            return jsonify({'answer': "can't find answer due to system error"})
    else:
        print('Processing GET request for chat history')
        try:
            response = chat_table.query(
                KeyConditionExpression=Key('user_id').eq(user_id),
                ScanIndexForward=True
            )
            chat_history = response.get('Items', [])
            print(f'Number of chat history items for GET request: {len(chat_history)}')
        except Exception as e:
            print(f"Error fetching chat history: {e}")
            chat_history = []

        return render_template('chat.html', user_id=user_id, chat_history=chat_history)

@app.route('/logout')
def logout():
    print('Logging out user...')
    session.pop('user_id', None)
    flash("You have been logged out.")
    print('User logged out successfully')
    return redirect(url_for('login'))

@app.route('/clear_chat_history', methods=['POST'])
@login_required
def clear_chat_history():
    print('Entered /clear_chat_history route')
    user_id = session.get('user_id')
    print(f'Processing chat history for user ID: {user_id}')

    try:
        response = chat_table.query(
            KeyConditionExpression=Key('user_id').eq(user_id)
        )
        chat_history = response['Items']
        print(f'Number of chat history items to save and delete: {len(chat_history)}')

        if chat_history:
            # Sort chat history by timestamp in ascending order
            sorted_chat_history = sorted(chat_history, key=lambda x: x['timestamp'])

            # Save sorted chat history to S3
            s3_key = f"chat_history/{user_id}/{int(time.time())}.json"
            s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=json.dumps(sorted_chat_history, indent=4),
                ContentType='application/json'
            )
            print(f'Sorted chat history saved to S3: {s3_key}')

        with chat_table.batch_writer() as batch:
            for item in response['Items']:
                batch.delete_item(
                    Key={
                        'user_id': item['user_id'],
                        'timestamp': item['timestamp']
                    }
                )
        print('Chat history cleared successfully')
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error clearing chat history: {e}")
        return jsonify({"success": False, "error": str(e)})
    


if __name__ == "__main__":
    # print('Starting Flask application...')
    # app.run(host='localhost', port=6060,debug=True)

    # Get port from environment variable or use default
    port = int(os.getenv('PORT', 6060))
    # Get host from environment variable or use default
    host = os.getenv('HOST', '0.0.0.0')
    
    # logger.info(f"Starting Flask application on {host}:{port}")
    print(f"Starting Flask application on {host}:{port}")
    app.run(host=host, port=port, debug=False)


