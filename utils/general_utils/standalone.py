import json

tools = [
    {
        "name": "context_preserver",
        "description": "A tool designed to preserve conversation context by generating a standalone query, summarizing the relevant context from previous chats, and extracting any potentially useful parameters.",
        "parameters": {
            "type": "object",
            "strict": True,
            "properties": {
                "previous_context": {
                    "type": "string",
                    "description": "A concise summary of all relevant details from the previous conversation that are pertinent to the current input or query.",
                },
                "standalone": {
                    "type": "string",
                    "description": "A rephrased standalone version of the current query that eliminates any indirect references or dependencies on prior context.",
                },
                "params": {
                    "type": "string",
                    "description": "An exhaustive list of key-value pairs representing parameters that may be even slightly relevant to the current query.",
                },
            },
            "required": ["previous_context", "standalone", "params"],
        },
    }
]


def format_query(lm_client, chat, query):
    """
    Converts an indirect query into a standalone one using the chat transcript.
    Dynamically generates a context summary (maximum 50 words) or leaves it empty if the current query is unrelated to prior context.
    """
    system_message = '''
    You are an expert in query rewriting and formatting, tasked with ensuring queries are fully self-contained while maintaining the user's tone and intent.

    Responsibilities:
    1. Context Summary Creation:
       - Analyze the conversation transcript (last 25 messages) and the user's query.
       - If the current query is unrelated to prior messages or there is no natural flow leading to the current input, set "previous_context" to an empty string.
       - Otherwise, generate a concise summary (maximum 50 words) describing where the process is currently, specifically relevant to the user's current query.

    2. Query Rewriting:
       - If the most recent query is already standalone, return it as it is in "standalone". 
       **Image Description Handling**:

       - If the query is about the image description, include the image description in the standalone query as it is with the path mentioned as well.
       - If the query references prior context or lacks clarity, rewrite it to include all necessary details explicitly by referencing the provided conversation transcript and "previous_context". Preserve the user's original tone and intent. Don't add additional details on your own!

    Parameter Extraction:
       - Extract and include all parameters mentioned in the conversation transcript or "previous_context" that are critical to forming a complete query, and return them in "params" as a key-value list.
       - if there are relevant image paths from previous conversations, include them in the params as well.

    Output Requirements:
       - Return the following:
         {
           "previous_context": "Generated context summary here." or "",
           "standalone": "Rewritten query based on context summary and parameters.",
           "params": {
               "key1": "value1",
               "key2": "value2",
               ...
           }
         }

    **Communication Style**:
        - Always respond in the same language that the user used to ask the question.
        - Match the character style used by the user:
            - If the user types in a specific language using native alphabets (e.g., हिंदी में लिखें), respond using the same script.
            - If the user types in a specific language using English characters (e.g., "aap hindi me answer kardo please"), respond in that language but use English characters to match their input style.

    Guidelines:
       - Localize the standalone: Focus on the current task, even if part of a larger process.
       - Clarity and Precision: Avoid ambiguity or indirect references.
       - No Hallucination: Only include details explicitly mentioned or implied in the conversation.

    Example:
    Conversation Transcript:
    1. User: "Can you help me track my order?"
    2. Assistant: "Sure, what's your order ID?"
    3. User: "It's 12345."
    4. Assistant: "Got it. Your order is on its way. Anything else?"
    5. User: "Can you also tell me how to cancel it?"

    Query: "Can you tell me how to cancel my order?"

    Output:
    {
        "previous_context": "User is asking about an order they are tracking (ID: 12345) and now wants to cancel it.",
        "standalone": "How do I cancel an order with ID 12345?",
        "params": {
            "order_id": "12345"
        }
    }

    Example (unrelated query):
    Conversation Transcript:
    1. User: "Tell me about the weather in New York."
    2. Assistant: "It’s sunny with a high of 25°C."
    3. User: "Thanks."

    Query: "How do I bake a cake?"

    Output:
    {
        "previous_context": "",
        "standalone": "How do I bake a cake?",
        "params": {}
    }
    '''

    user_message = (
        f"Transcript of conversation (last 25 messages):\n\n{chat}\n\n"
        f"Current Query:\n\n{query}"
    )

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]

    try:
        response = lm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=4000,
            temperature=0.0,
            functions=tools,
            function_call={"name": "context_preserver"},
        )
        print(response)
        arguments = json.loads(response.choices[0].message.function_call.arguments)

        previous_context = arguments['previous_context']
        standalone = arguments['standalone']
        parameters = arguments['params']
        
        return previous_context, parameters, standalone

    except Exception as e:
        print(f"Error formatting query: {e}")
        return '', '', query  # Fallback to the original query if formatting fails



# def format_query(lm_client, chat, query):
#     """
#     Converts an indirect query into a standalone one by using the chat transcript.
#     """
#     # system_message = '''
#     #     You are a professional - best in the world for query formatting/rewriting. 
#     #     You will be provided with a conversation transcript. 
#     #     If the most recent query from user is already standalone and does not rely on any information from the transcript, 
#     #     return the query exactly as it is. However, if the current query contains indirect references 
#     #     or lacks context needed to make it standalone, rewrite it by incorporating any missing details 
#     #     from the transcript, removing all indirect references. The final question should be fully self-contained, 
#     #     able to retrieve relevant data from a vector database without additional context from the conversation. 
#     #     Be concise but ensure all necessary information is included.
#     # '''
#     system_message = '''

#     You are an expert in query rewriting and formatting, tasked with ensuring queries are fully self-contained while maintaining the user's tone and intent.

#     Responsibilities:
#     Contextual Rewriting:

#     If the most recent query is already standalone and contains all necessary details, return it as it is.
#     If the query references prior context or lacks clarity, rewrite it to include all necessary details explicitly by referencing the provided conversation transcript. Preserve the user's original tone and intent.
#     Parameter Inclusion:

#     Track all relevant parameters mentioned in the conversation using the format:

#     Previous Parameters Knowledge:
#     {
#         "key1": "value1",
#         "key2": "value2"
#         ...
#     }
#     Ensure the rewritten standalone query incorporates all required parameters from this dictionary.
#     Missing any parameter is unacceptable, as it would break the architecture.
#     Output Requirements:

#     Present the rewritten query in the following format:
#     Previous Parameters Knowledge:
#     {
#         "key1": "value1",
#         "key2": "value2"
#         ...
#     }

#     Current Standalone Query:
#     "Rewritten query based on previous context and parameters."
#     The standalone query should be concise, clear, and executable independently, without needing prior conversation context.

#     **Communication Style**:
#     - Always respond in the same language that the user used to ask the question
#     - Match the character style used by the user:
#         - If the user types in a specific language using native alphabets (e.g., हिंदी में लिखें), respond using the same script.
#         - If the user types in a specific language using English characters (e.g., "aap hindi me answer kardo please"), respond in that language but use English characters to match their input style.

#     Guidelines:

#     Localize the standalone: As we proceed become task specific rather than always having the big picture in mind, like the big picture could be creating a profile, while now we are collecting details to get a specific task it in done so make the standalone that specific.
#     example: big picture is creating a profile for X
#     now in this process if we just collected KYC details 
#     say that these are the details to update the customers KYC details (just that and not for making the profile)

#     Clarity and Precision: Avoid ambiguity or indirect references. Ensure the query is complete and leaves no room for misinterpretation.
#     Professionalism: Use clear and professional language while preserving the user's tone.
#     No Hallucination: Only include details explicitly mentioned or implied in the conversation. Do not add assumptions or unnecessary information.
#     Objective: Rewrite queries to be robust, standalone, and fully prepared for seamless backend integration, ensuring they reflect the user’s original intent.


#     '''

#     user_message = f"Transcript of conversation:\n\n{chat}"
    
#     messages = [
#         {"role": "system", "content": system_message},
#         {"role": "user", "content": user_message},
#     ]

#     try:
#         response = lm_client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=messages,
#             max_tokens=1000,
#             temperature=0.0
#         )
#         print(response)
#         standalone_query = response.choices[0].message.content
#         return standalone_query
    
#     except Exception as e:
#         print(f"Error formatting query: {e}")
#         return query  # Fallback to the original query if formatting fails
    
