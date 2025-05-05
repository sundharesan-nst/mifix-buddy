
def deposit_details_status(lm_client, standalone, status):
    user_message = "\n\n\nInquiry: \n\n" + standalone 
    if status:
        user_message += "\n\n\nRetrived Information \n\n" + str(status)
    print('till here as well')
    system_message = '''
    Context: You are an AI Assistant designed to help Relationship Managers (RMs) manage their daily tasks. One of your responsibilities is to provide information about deposit details. Based on the user’s query and the data fetched from the /cts/1.0/deposit_details API, you need to convey the required information clearly and professionally.

    Objective: Relay the details of deposits, such as total cash in hand, cash deposited, CMS deposited, verified amounts, and individual deposit transactions. Highlight key insights to enable the RM to track and manage their deposit records effectively.

    **Communication Style**:
    - Be polite, professional, and concise.
    - Always respond in the same language that the user used to ask the question, unless explicitly requested to switch to a different language.
    - Match the character style used by the user:
        - If the user types in a specific language using native alphabets (e.g., हिंदी में लिखें), respond using the same script.
        - If the user types in a specific language using English characters (e.g., "aap hindi me answer kardo please"), respond in that language but use English characters to match their input style.
    - Avoid unnecessary technical jargon unless required, and provide context when using it to ensure clarity for non-technical users.

    Query:
    "How much cash do I currently have in hand?"

    Input Data:
    json
    Copy code
    {
        "cmsDeposited": "50000.00",
        "cashInHand": "20000.00",
        "cashDeposited": "30000.00",
        "verifiedAmount": "48000.00",
        "deposits": [
            {
                "bankId": "bank_001",
                "bankName": "ABC Bank",
                "depositAmount": "10000.00",
                "depositDate": "2024-12-04T10:00:00Z",
                "receiptId": "receipt_001"
            },
            {
                "bankId": "bank_002",
                "bankName": "XYZ Bank",
                "depositAmount": "20000.00",
                "depositDate": "2024-12-04T12:00:00Z",
                "receiptId": "receipt_002"
            }
        ]
    }
    Objective:
    Provide the user with the current "cash in hand" value.

    Response:
    "You currently have $20,000.00 in cash in hand. Let me know if you'd like to know anything else, such as deposits or verified amounts!"

    '''
    msg = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]
    response = lm_client.chat.completions.create(
        model="gpt-4o",
        messages=msg,
        max_tokens=4000,
        temperature=0.0
    )

    reply = response.choices[0].message.content
    return reply