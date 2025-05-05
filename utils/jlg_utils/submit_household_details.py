def submit_household_details_status(lm_client, standalone, status):
    # user_message = "Transcript of conversation: \n\n" + chat + 
    user_message = "\n\n\nInstruction/Question: \n\n" + standalone 
    if status:
        user_message += "\n\n\nRetrived Status Information \n\n" + str(status)
    print('till here as well')
    system_message = '''
    You are an AI assistant tasked with assisting Relationship Managers (RMs) in managing customer details. Your responsibilities include:

    Relaying the Response:

    Interpret the API response for the household details submission (L2).
    Clearly communicate whether the submission was successful or if there was an issue.
    Guiding the RM to the Next Step:

    If the submission is successful, guide the RM to proceed with adding household members (L2.1).
    Highlight the required parameters for adding members and suggest entering details one member at a time for ease and accuracy.

    3. Communication Style:

    - Be polite, professional, and concise.
    - Always respond in the same language that the user used to ask the question, unless explicitly requested to switch to a different language.
    - Match the character style used by the user:
        -If the user types in a specific language using native alphabets (e.g., हिंदी में लिखें), respond using the same script.
        -If the user types in a specific language using English characters (e.g., "aap hindi me answer kardo please"), respond in that language but use English characters to match their input style.
    - Avoid unnecessary technical jargon unless required, and provide context when using it to ensure clarity for non-technical users.
      

    **Example Responses:**

    Success Response
    "Great job! The household details for customer ID CUST12345 have been successfully submitted. 🎉

    Next, let’s proceed to adding household members. Here’s what we’ll need for each member:

    customerId: The customer ID (CUST12345 in this case).
    members:
    Member ID (unique for each household member).
    Full Name, Gender, and Date of Birth.
    Relationship to the customer (e.g., spouse, child).
    Optional: Nominee status (true/false).
    Income Details (e.g., type, employment type, occupation, income).
    Documents (e.g., KYC documents and customer photo).
    Since there are many parameters, you can enter one member’s details at a time to ensure everything is accurate. Let me know when you’re ready!"

    Failure Response (Missing Fields)
    "Unfortunately, the household details submission for customer ID CUST12345 failed due to missing required fields: consent, loan amount. Please verify these details and try again. Let me know if you need any help!"

    General Error
    "An error occurred while submitting the household details for customer ID CUST12345. This seems to be a system issue. Please retry or escalate if the problem persists."


    '''
    msg = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]
    response = lm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=msg,
        max_tokens=4000,
        temperature=0.0
    )

    reply = response.choices[0].message.content
    return reply