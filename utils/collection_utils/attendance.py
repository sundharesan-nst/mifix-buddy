def attendance_status(lm_client, standalone, status):
    # user_message = "Transcript of conversation: \n\n" + chat + 
    user_message = "\n\n\nInquiry: \n\n" + standalone 
    if status:
        user_message += "\n\n\nRetrived Information \n\n" + str(status)
    print(status)
    print('till here as well')
    system_message = '''
    You are an AI Assistant designed to assist with attendance-related queries. Your role is to check the attendance status of the user and provide an appropriate response based on the retrieved information.

    ### Context:
    1. The user is inquiring about their attendance status.
    2. The system has fetched the attendance status from a database or API, which will be provided to you as input.

    ### Instructions:
    1. **Understand the Attendance Status**:
    - If the status is `PENDING`:
        - Inform the user that their attendance has not been marked yet.
        - Politely ask if they would like to mark their attendance now.
    - If the status is `COMPLETED`:
        - Share the clock-in time with the user.
  
    2. Communication Style:

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

def attendance_marking(lm_client, standalone, status):
    # user_message = "Transcript of conversation: \n\n" + chat + 
    user_message = "\n\n\nInstruction: \n\n" + standalone 
    if status:
        user_message += "\n\n\nRetrived Status Information \n\n" + str(status)
    print('till here as well')
    system_message = '''
    You are an AI Assistant designed to manage attendance requests for users. 
    Your task is to:
    1. Interpret the status of an attendance marking request.
    
    2. Relay the success or failure of the operation to the Relationship Manager (RM) in a concise and professional manner.

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