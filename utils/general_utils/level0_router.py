import json

tools = [
    {
        "name": "l0_router",
        "description": "Routing to the appropriate path for a solution, with explanations and parameter extraction.",
        "parameters": {
            "type": "object",
            "strict": True,
            "properties":  {
                "route": {
                    "type": "integer",
                    "enum": [1, 2, 3],
                    "description": "The selected route for the query. Choose 1 for VectorDB, 2 for Collection-based APIs, and 3 for JLG Group APIs.",
                },
                "reason": {
                    "type": "string",
                    "description": "A concise explanation for the selected route.",
                },
            },
            "required": ["route", "reason"],
        },
    }
]

def router_llm_l0(lm_client, standalone, previous_context):
    if previous_context:
        user_message = "User Question: " + standalone + "\nContext from previous chat " + str(previous_context)
    else:
        user_message = "User Question: " + standalone
    system_message = '''
    Flow Context for Routing Queries
Process Overview:

Routing Objective:
The goal of this router is to determine the appropriate route for addressing the user's query and, if required, direct to real-time actions. Based on the query's intent, the router will classify it into one of the following categories:

**Routes:**
Route 1) **VectorDB Query:**
   - When the user seeks raw knowledge or answers based on textbook-like resources or reference documents stored in the VectorDB.
   - Typical use cases include queries like:
     - "What is the eligibility criteria for JLG loans?"
     - "Explain the penny drop validation process."
     - "How does household income affect loan eligibility?"
   - No specific customer/group ID/any parameters is required for this route.
   - The primary focus is providing factual, research-based responses without invoking real-time API actions.
   - This is also a viable path in case RM is stuck somewhere or is facing error and needs resolutions 

Route 2) **Collection-based API Query:**

For real-time actions related to attendance, payment, reporting, or rescheduling in the collection process.

Capabilities:
Attendance Status API: Fetches the current attendance status.
Attendance Marking API: Marks attendance with location details.
Collection Target API: Retrieves assigned collection targets.
Group Schedule API: Fetches scheduled group activities.
Incomplete Transactions API: Retrieves a list of incomplete transactions.
Generate Digital Transaction API: Generates QR codes and transaction details.
Update Proof of Transaction API: Updates proof of payment for customers.
Deposit Details API: Fetches deposit-related details.
Group Prospect Details API: Retrieves details for a specified group.
Reschedule Customer API: Reschedules a customer with remarks.

Direct the Question to this route incase you feel the question can be answered using any of the above APIs or a combination of them

Route 3) **JLG Group API Query:**
For real-time actions related to onboarding, household details, bank account verification, and group creation in the JLG process.

Capabilities:
Generate Mobile OTP: Creates an OTP for customer authentication.
Validate Mobile OTP: Verifies the OTP entered by the customer.
Upload Customer Documents (L1): Uploads documents like applicant photos and address proof.
Upload Household Member Documents (L2): Manages KYC and asset document uploads for household members.
Upload Bank Documents (L3): Uploads bank account proof documents.
Submit L1 Additional Details: Submits customer demographics and required L1 details.
Fetch L1 Customer List: Retrieves a list of L1 customers based on filters.
Submit/Update Household Member Details: Adds or updates household member details.
Submit Household Details: Submits household-level information and loan preferences.
Submit Amenities: Records preferences for household amenities.
Submit Assets: Logs assets owned by the customer.
Submit Expenses: Captures customer expenses by type and amount.
Eligibility Check: Checks a customer’s loan eligibility.
Calculate EMI: Calculates EMI for a customer based on loan amount and tenure.
Fetch L2 Customer List: Retrieves a list of L2 customers based on filters.
Get Bank Details by IFSC: Fetches bank details using an IFSC code.
Submit Bank Account Details: Submits bank details for disbursement.
Fetch L3 Customer List: Retrieves a list of L3 customers based on filters.
Retrigger EKYC: Retriggers the EKYC process for a customer.
Retry Credit Check: Initiates a retry for the credit check process.
Create Group: Creates a JLG group with specified customers.

Note: If the query shows intent on creating a customer's profile, or moving ahead with the profile, this is the path. 

**Router LLM Task:**
You are tasked with detecting the intent behind the user's query and selecting the appropriate route. Based on the input query:
- **Detect Intent:** Determine if the user seeks knowledge (VectorDB), collection-based real-time actions, or JLG group-specific real-time workflows.
- **Respond with Reasoning:** Provide a clear explanation for the chosen route.
- **Highlight Real-Time Action:** For routes 2 and 3, indicate the type of action to be executed, such as marking attendance, submitting details, or initiating group formation.

**Output Format:**
{
    'route': Integer (1, 2, or 3),
    'reason': "Explanation for the selected route."
}

**Examples:**
Query:
"What are the eligibility criteria for a loan?"
Output:
{
    "route": 1,
    "reason": "The query seeks knowledge-based information about loan eligibility, best answered using VectorDB resources."
}

Query:
"Fetch my incomplete transactions."
Output:
{
    "route": 2,
    "reason": "This query involves retrieving a list of incomplete transactions, which is a real-time collection-based action."
}

Query:
"Retry EKYC for customer CUST789."
Output:
{
    "route": 3,
    "reason": "The query involves retrying EKYC for a specific customer, which is part of the JLG group API flow."
}

    '''

    msg = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]
    response = lm_client.chat.completions.create(
        model="gpt-4o",
        messages=msg,
        max_tokens=4000,
        temperature=0.0,
        functions=tools,
        function_call={"name": "l0_router"},
    )

    print(response)
    arguments = json.loads(response.choices[0].message.function_call.arguments)

    route = arguments['route']
    reason = arguments['reason']
    return route, reason