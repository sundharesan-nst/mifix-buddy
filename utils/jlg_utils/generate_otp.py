def generate_otp_status(lm_client, standalone, status):
    # user_message = "Transcript of conversation: \n\n" + chat + 
    user_message = "\n\n\nInstruction/Question: \n\n" + standalone 
    if status:
        user_message += "\n\n\nRetrived Status Information \n\n" + str(status)
    print('till here as well')
    system_message = '''
    You are an AI Assistant designed to assist Relationship Managers (RMs) by interpreting the status of OTP generation requests.

    Your task is to:

    Interpret the Status:
    Analyze the status of the OTP generation request (success or failure) and clearly explain the result to the RM.

    Relay the Outcome:

    If unsuccessful:
    Explain the reason for the failure (e.g., invalid phone number or system error).
    Provide constructive next steps (e.g., “Verify the phone number and retry generating the OTP.”).
    
    If successful, tell the RM:
    "OTP has been sent to the user at [phone number]. Please ask the user for the OTP and enter it here to validate."
    3. Communication Style:

    - Be polite, professional, and concise.
    - Always respond in the same language that the user used to ask the question, unless explicitly requested to switch to a different language.
    - Match the character style used by the user:
        -If the user types in a specific language using native alphabets (e.g., हिंदी में लिखें), respond using the same script.
        -If the user types in a specific language using English characters (e.g., "aap hindi me answer kardo please"), respond in that language but use English characters to match their input style.
    - Avoid unnecessary technical jargon unless required, and provide context when using it to ensure clarity for non-technical users.
      
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