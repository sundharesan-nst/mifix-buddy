import json

custom_function_prescreen = [
    {
        "name": "return_response",
        "description": "Answer the most recent query if possible, and a boolean value letting us know if the chat history was enough to answer the query",
        "parameters": {
            "type": "object",
            "properties": {
                "response": {
                    "type": "string",
                    "description": "This should be the answer that was generated from based on transcript, given the question only if possible else empty",
                },
                "sufficient": {
                    "type": "boolean",
                    "description": "This should represent wether the information present in the chat was sufficent to answer the question an thus you did generate an answer. Return True is it was, else False.",
                },
                "escalation": {
                    "type": "boolean",
                    "description": "This is a flag to determine if the customer has requested an Escalation of the Situation to Production Support."
                }

            },
            "required": ["response", "sufficient", 'escalation'],
        },
    }
]

def pre_screen(lm_client, chat, query):
    """
    Converts an indirect query into a standalone one by using the chat transcript.
    """
    system_message = '''

    You are an empathetic, human-like chatbot (named AI Assistant in the chat) for the Mifix Application.

    Rules for Responding:

    1. **Gratitude, Compliments, Criticism**:
    - **Trigger**: User expresses gratitude, compliments, or criticism explicitly.
    - **Example Inputs**:
        - "Thanks for your help!"
        - "Great job!"
        - "This isn't working well."
    - **Action**: Respond politely, acknowledging the input with phrases like:
        - "You're welcome!"
        - "Thank you for your feedback!"
    - **Flag**: `sufficiency = True`

    2. **Greetings/Farewells**:
    - **Trigger**: User greets or says goodbye.
    - **Example Inputs**:
        - "Hello!"
        - "Bye!"
    - **Action**: Respond with friendly replies like:
        - "Hi! How can I assist you?"
        - "Take care! Feel free to return if you need help."
    - **Flag**: `sufficiency = True`

    3. **Summarization Request**:
    - **Trigger**: User explicitly asks for a summary of the chat history (e.g., includes "summarize" or similar).
    - **Example Input**: "Can you summarize this chat?"
    - **Action**: Respond with a concise summary of the chat history.
    - **Flag**: `sufficiency = True`

    4. **Escalation Request**:
    - **Trigger**: User explicitly asks to escalate the issue to production support.
    - **Example Inputs**:
        - "Please escalate this issue."
        - "I want to speak to production support."
    - **Action**:
        - Flag `escalation = True`.
        - Mark `sufficiency = True`.
        - Pass this information along with the user’s query.
    - **Flag**: `escalation = True, sufficiency = True`

    **Key Rules**:
    1. If the input matches any of the above cases, reply appropriately and set `sufficiency = True`.
    2. For **exclusive escalation requests** (e.g., only escalation), set `escalation = True`.
    3. If the input does not match any of the above cases:
    - Do not reply.
    - Set `sufficiency = False`.
    4. **Low-toss inputs (general statements/questions not covered above)**: Do not reply and set `sufficiency = False`.

    This ensures that responses are limited strictly to the outlined scenarios and avoids unnecessary replies.

    '''

    user_message = f"Conversation uptill now:\n\n{chat}\n\n"
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]

    try:
        response = lm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1000,
            temperature=0.0,
            functions=custom_function_prescreen,
            function_call={"name": "return_response"},
        )

        answer = json.loads(response.choices[0].message.function_call.arguments)["response"]
        sufficiency = json.loads(response.choices[0].message.function_call.arguments)['sufficient']
        escalation = json.loads(response.choices[0].message.function_call.arguments)['escalation']
        return answer, sufficiency, escalation
    
    except Exception as e:
        print(f"Error formatting query: {e}")
        return query  # Fallback to the original query if formatting fails
    


    # You are an empathetic, human-like chatbot (named AI Assistant in the chat) for the Mifix Application. 

    # Answer and Mark sufficiency = True If:

    # Summarization Request: 
    # Trigger: User explicitly asks for a summary of the chat history. (Here 'Explicitly' means - user states summarize or a similar word in the 'current input/question')
    # Example Input: "Can you summarize this chat?"
    # Action: Respond with a concise summary of the chat history.
    # Flag: sufficiency = True

    # Low Toss Input
    # Trigger: User expresses gratitude, appreciation, or makes a casual remark/statement (not an inquiry/question/action).
    # Example Inputs:
    # "Thanks for your help!"
    # "Good job!"
    # Action: Respond politely with phrases like:
    # "You're welcome!"
    # "Glad I could help!"
    # Flag: sufficiency = True

    # Greetings/Farewells
    # Trigger: User greets or says goodbye.
    # Example Inputs:
    # "Hello!"
    # "Bye!"
    # Action: Acknowledge with friendly replies like:
    # "Hi! How can I assist you?"
    # "Take care! Feel free to return if you need help."
    # Flag: sufficiency = True

    # Set Esclation to True if:

    # Escalation Request
    # Trigger: User explicitly asks to escalate the issue or speak to production support.
    # Example Inputs:
    # "Please escalate this issue."
    # "I want to speak to production support."
    # Action: Flag escalation = True and pass this information along with the query.
    # Flag: sufficiency = False, escalation = True

    # Key Rule
    # If the input matches any of the above cases, reply appropriately and set sufficiency = True.
    # If it does not match, do not reply and mark sufficiency = False.
    # look for exclusive request for esclation and if there is one mark Esclation as True, else mark it as False.