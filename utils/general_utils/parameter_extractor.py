import json
from datetime import datetime
import pytz

# Get the current date in Indian Standard Time (IST)
ist = pytz.timezone('Asia/Kolkata')
today_date = datetime.now(ist).strftime('%Y-%m-%d')

tools = [
    {
        "name": "payload_extractor",
        "description": "Preparing a payload file strictly in the structure specified, which would be used for a high stake API call in future",
        "parameters": {
            "type": "object",
            "strict": True,
            "properties":  {
                "sufficient": {
                    "type": "boolean",
                    "description": "This should reflect if the required json structure can be achieved based on the query",
                },
                "reply": {
                    "type": "string",
                    "description": "Leave this empty in case sufficient, in case not, you are a customer facing bot named AI assistant, and you polietly ask for further required information to move ahead.",
                },
                "payload": {
                    "type": "string",
                    "description": "The extracted payload strictly in the structure specified, which would in turn be used for high stakes API call",
                },
            },
            "required": ["sufficient", "reply", "payload"],
        },
    }
]

def extract_parameters(lm_client, standalone, structure, params, previous_context):
    
    print(today_date)
    
    if previous_context:
        user_message = "Context from previous chat: " + previous_context
    else:
        user_message = ''

    if params:
        user_message += " Parameter Knowledge base: " + str(params)
    
    user_message += " User Input: " + standalone + "\n Target Json File Structure: " + str(structure) 

    system_message = '''

    You are an advanced AI specializing in creating structured JSON payloads as strings for high-stakes API calls. Your primary goal is to analyze the user's input and generate an accurate JSON string in the specified structure. If insufficient data is provided, you must clearly and politely explain what is missing and why it is needed.

**Guidelines**:
1. **Output Format**:
    - If sufficient information is provided:
      - Generate the JSON payload as a string that matches the provided structure.
      - Only output the JSON string — no extra text, comments, or explanations.
    - If insufficient information is provided:
      - Output an empty string as the JSON payload.
      - Provide a clear, polite explanation of the missing details in `reply`.

2. **Output Fields**:
    - `sufficient`: A boolean indicating whether all required information is provided.
    - `reply`:
      - Empty if `sufficient` is `true`.
      - A polite, customer-focused explanation if `sufficient` is `false`.
    - `payload`: A JSON string representation of the required structure, or an empty string if `sufficient` is `false`.

3. **JSON Construction**:
    - Follow the exact structure provided in `Target JSON File Structure`.
    - Populate fields only if sufficient information is available. If any required field is missing, do not guess values.

4. **Communication Style**:
    - Be concise, clear, and professional.
    - Respond in the same language used in the query.

Note: - if the parameters demand files/images, then attach the path of that image/file/s mentioned in the User Input (No need for verification for relevance, just attach all). 
      - if there is a date to be entered in parameters and the date hasn't been explicitly provided, then use the date as "''' + today_date + '''" ( we use today's date as a fall back).

**Examples**:

**Example 1: Sufficient Input**
- **User Input**: "Update proof for customer C12345 and transaction date 2024-12-22.  Parameter Knowledge base: (image_path/s)" 
- **Target JSON File Structure**:
  ```json
  {
    "custId": "string",
    "proofOfTransactions": [image_path/s],
    "transactionDate": "string"
  }
Output:

{
  "sufficient": true,
  "reply": "",
  "payload": "{\"custId\": \"C12345\", \"proofOfTransactions\": [\"image_path/s\"], \"transactionDate\": \"2024-12-22\"}"
}

Example 2: Insufficient Input

User Input: "I need to update proof for customer C12345."
Target JSON File Structure:

{
  "custId": "string",
  "proofOfTransactions": ["string"],
  "transactionDate": "string"
}

Output:

{
  "sufficient": False,
  "reply": "It seems that proof of transactions and the transaction date are missing. Could you please provide these details to proceed?",
  "payload": ""
}
Example 3: Complex Structure

User Input: "Add customer C12345 with demographic details and marital status."
Target JSON File Structure:

{
  "payload": {
    "customerId": "string",
    "demographics": {
      "fullName": "string",
      "dob": "string",
      "gender": "string",
      "mobileNumber": "string",
      "maritalStatus": "string",
      "educationalQualification": "string",
      "natureOfResidence": "string"
    }
  }
}
Output:

{
  "sufficient": False,
  "reply": "The demographic details such as full name, date of birth, gender, mobile number, educational qualification, and nature of residence are missing. Please provide these to complete the payload.",
  "payload": ""
}
Example 4: Sufficient Input with Nested Structure
User Input: "Add a member for customer C12345 with full details and documents."

Target JSON File Structure:

{
  "payload": {
    "customerId": "string",
    "members": [
      {
        "id": "string",
        "fullName": "string",
        "gender": "string",
        "dob": "string",
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
Output:

{
  "sufficient": true,
  "reply": "",
  "payload": "{\"payload\": {\"customerId\": \"C12345\", \"members\": [{\"id\": \"M123\", \"fullName\": \"John Doe\", \"gender\": \"male\", \"dob\": \"1990-01-01\", \"relationship\": \"son\", \"isNominee\": true, \"incomeDetails\": [{\"id\": \"I456\", \"type\": \"salary\", \"employmentType\": \"permanent\", \"occupation\": \"engineer\", \"designation\": \"senior engineer\", \"income\": 75000}], \"documents\": {\"kycDocuments\": \"attched_image_path\", \"customerPhoto\": \"attched_image_path\"}}]}}"
}
Explanation:

Since the payload is explicitly included as part of the Target JSON File Structure, the generated JSON string must reflect this by enclosing all data within the payload key.
Ensure strict adherence to the structure, including any top-level payload or other wrapping keys, exactly as specified in the Target JSON File Structure.

Your Turn: Analyze the user input and the provided JSON structure. Generate a response that strictly adheres to the guidelines above.

'''
  
    msg = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]
    response = lm_client.chat.completions.create(
        model="gpt-4o",
        messages=msg,
        max_tokens=13000,
        temperature=0.0,
        functions=tools,
        function_call={"name": "payload_extractor"},
    )

    print(response)
    arguments = json.loads(response.choices[0].message.function_call.arguments)

    sufficient = arguments['sufficient']
    reply = arguments['reply']
    
    # Convert the JSON string in 'payload' to a Python dictionary
    try:
        if arguments['payload']:
            parameters = json.loads(arguments['payload'])
        else:
            parameters = {}
    except json.JSONDecodeError as e:
        print(f"Error decoding payload JSON: {e}")
        parameters = {}
    
    print('\n')
    print(parameters, type(parameters))
    print('\n')

    return parameters, sufficient, reply
    
