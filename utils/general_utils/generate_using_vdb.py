import json

custom_function_rag = [
    {
        "name": "return_response",
        "description": "Function to be used to return the response to the question, and a boolean value indicating if the information given was suffieicnet to generate the entire answer.",
        "parameters": {
            "type": "object",
            "properties": {
                "item_list": {
                    "type": "array",
                    "description": "List of chunk ids. ONLY the ones used to generate the response to the question being asked. return the id only if the info was used in the response. think carefully.",
                    "items": {"type": "integer"},
                },
                "response": {
                    "type": "string",
                    "description": "This should be the answer that was generated from the context, given the question",
                },
            },
            "required": ["response", "sufficient", "item_list"],
        },
    }
]

def ask_gpt_fast(lm_client, question, context, previous_context):
    # user_message = "Transcript of conversation: \n\n" + chat + 
    user_message = "\n\n\nCurrent Question: \n\n" + question 

    if previous_context:
        user_message += "\n\n\nPrevious Chats Context: \n\n" + str(previous_context)

    if context:
        user_message += "\n\n\nContext from VDB: \n\n" + str(context)
    print('till here as well')
    system_message = '''You are a professional customer-facing chatbot.
     
    Interaction Guidelines:
    Respond with empathy and patience.
    Ensure responses are coherent and maintain the flow of the conversation.

    Communication Style:

    - Be polite, professional, and concise.
    - Always respond in the same language that the user used to ask the question, unless explicitly requested to switch to a different language.
    - Match the character style used by the user:
        -If the user types in a specific language using native alphabets (e.g., हिंदी में लिखें), respond using the same script.
        -If the user types in a specific language using English characters (e.g., "aap hindi me answer kardo please"), respond in that language but use English characters to match their input style.
    - Avoid unnecessary technical jargon unless required, and provide context when using it to ensure clarity for non-technical users.

    You will be given context from several PDFs, 
    retrieved from a vector database, and the transcript of an ongoing chat with the customer. Use the relevance of the conversation in the transcript
    to understand the query better, then answer the query using the provided Context and Transcript only, no hallucinations.
    Return the response, which is the answer to the question asked.
    The reader of your response does not have any idea of the 'context/transcript' being passed. Do not reference the presence of the context in the final response, just provide the answer directly.
    
    In Case the context/previous chat isn't provided or isn't sufficient: 
    ask for additional information which might help understand the user better, or assist user prompt a more specific query so the context from the vector DB can be retrived. 
    Else if the question is not too vague AND doesn't seem like a very critical task (Something that might lead to exponentially demeaning results if not done properly) AND there is some soft guidance you can provide, provide that but add a note saying this is not this is not a grounded suggestion and esclate in case it's a critical task and then provide the suggestion/answer.
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
        functions=custom_function_rag,
        function_call={"name": "return_response"},
    )

    reply = json.loads(response.choices[0].message.function_call.arguments)[
        "response"
    ]
    item_list = json.loads(response.choices[0].message.function_call.arguments)[
        "item_list"
    ]
    
    return reply, item_list
