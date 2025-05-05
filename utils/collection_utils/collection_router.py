import json

tools = [
    {
        "name": "coll_router",
        "description": "Routing to the appropriate path for a solution, with explanations and parameter extraction.",
        "parameters": {
            "type": "object",
            "strict": True,
            "properties":  {
                "route": {
                    "type": "integer",
                    "enum": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
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

def collection_router(lm_client, standalone, previous_context):
    user_message = "User Question: " + standalone
    if previous_context:
        user_message += "Context from previous chat " + str(previous_context)

    system_message = '''
    **Collection API Routing Context**

    You are tasked with determining the exact Collection API route based on the user's query. Here's the list of routes:

    **Routes:**

    0. **Determine Scope**:
    - **Description**: Evaluates the query against the detailed capabilities of the Collection APIs. If the query falls outside the described use cases, declare it as out of scope.
    - **Use Case**: Ensures that queries unrelated to the Collection APIs or requiring unsupported actions are flagged as unanswerable within this system.

    1. **Attendance Status API**:
    - **Endpoint**: `GET /api/v1/attendance/status`
    - **Description**: Retrieves the attendance status of a user, showing details like the last marked attendance time and the current attendance status (e.g., PENDING, COMPLETED).
    - **Use Case**: Helps track whether a user has clocked in or out for their attendance for the day.

    2. **Attendance Marking API**:
    - **Endpoint**: `POST /api/v1/attendance/mark`
    - **Description**: Records a user’s attendance by marking an event (`CLOCK_IN`) along with associated GPS data (`latitude` and `longitude`) for location tracking.
    - **Use Case**: Enables attendance tracking for field agents or employees required to mark attendance from specific locations.

    3. **Collection Target API**:
    - **Endpoint**: `GET /dms/1.0/collection-target`
    - **Description**: Fetches collection target details for a specific time frame, including pending and completed collections (amount, groups, customers).
    - **Use Case**: Provides insights into a collection agent’s performance and pending tasks for a specified time frame.

    4. **Group Schedule API**:
    - **Endpoint**: `GET /dms/1.0/group-scheduled`
    - **Description**: Retrieves the schedule for a group, including details like group name, bank details, collected amount, overdue amounts, next visit time, and health status (e.g., "Healthy", "At Risk").
    - **Use Case**: Facilitates scheduling and monitoring of group-level activities, ensuring timely collections and follow-ups.

    5. **Incomplete Transactions API**:
    - **Endpoint**: `GET /dms/1.0/incomplete_transactions`
    - **Description**: Lists all pending or incomplete transactions for a user. Includes transaction details like amounts, overdue payments, health status, and next visit dates.
    - **Use Case**: Identifies transactions requiring immediate follow-up to ensure payment completion.

    6. **Deposit Details API**:
    - **Endpoint**: `GET /cts/1.0/deposit_details`
    - **Description**: Fetches deposit-related information such as total amounts deposited, cash in hand, verified amounts, and details of individual deposits (bank name, deposit amount, and date).
    - **Use Case**: Helps in reconciling deposits, ensuring all payments are accounted for, and identifying discrepancies.

    7. **Group Prospect Details API**:
    - **Endpoint**: `GET /dms/1.0/group-prospect-detail`
    - **Description**: Retrieves details about a specific group prospect, including group-level and member-specific information such as outstanding amounts, payment statuses, and loan product details.
    - **Use Case**: Monitors group performance and identifies prospects with overdue payments or rescheduling needs.

    8. **Generate Digital Transaction API**:
    - **Endpoint**: `POST /cts/1.0/generate-digital-transaction`
    - **Description**: Generates a QR code and transaction metadata for payment purposes, including unique transaction IDs, deep links, and short links for easy sharing.
    - **Use Case**: Enables seamless UPI-based payments, improving payment efficiency for collections.

    9. **Update Proof of Transaction API**:
        - **Endpoint**: `POST /cts/1.0/update_proof_of_transaction`
        - **Description**: Updates proof of payment for a specific customer or transaction, with details like transaction date, group name, and payment receipts.
        - **Use Case**: Ensures accurate record-keeping of payments and resolves disputes related to transactions.

    10. **Reschedule Customer API**:
        - **Endpoint**: `POST /dms/1.0/schedule/reschedule-customer`
        - **Description**: Reschedules a customer’s collection meeting or deadline with reasons, remarks, and optional feedback.
        - **Use Case**: Enables flexible scheduling for collection appointments, ensuring customer satisfaction and proper documentation.

    **Instruction for Route 0 (Out of Scope)**:
    - Select Route 0 only if:
    1. The query does not align with any listed APIs.
    2. The system is at least 85 Percent confident that none of the available routes match the user query.

    **Guideline for Multiple Use Cases per API**:
    - Evaluate all possible use cases for an API and choose the one most relevant to the query.
    - Provide detailed reasoning for the selection and suggest clarifications if necessary.

    **Communication Style**:
    - Generate the reasoning as if answering to the end user to their query.
    - Always respond in the same language that the user used to ask the question, unless explicitly requested to switch to a different language.
    - Match the character style used by the user:
        - If the user types in a specific language using native alphabets (e.g., हिंदी में लिखें), respond using the same script.
        - If the user types in a specific language using English characters (e.g., "aap hindi me answer kardo please"), respond in that language but use English characters to match their input style.

    **Output Format:**
    {
        "route": Integer (0 to 10),
        "reason": "Detailed explanation for selecting this route (2-3 lines)."
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
        function_call={"name": "coll_router"},
    )

    print(response)
    arguments = json.loads(response.choices[0].message.function_call.arguments)

    route = arguments['route']
    reason = arguments['reason']
    return route, reason
