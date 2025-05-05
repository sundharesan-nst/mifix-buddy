
def perform_esclation(lm_client, user_id, chat):

    system_message = '''


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
            max_tokens=4000,
            temperature=0.0
        )
        print(response)
        result = response.choices[0].message.content
        return result

    except Exception as e:
        print(f"Error formatting query: {e}")
        return ['', '']  # Fallback to the original query if formatting fails



def request_esclation(lm_client, user_id, chat):

    esclation_message, esclation_attempt_result = perform_esclation(lm_client, user_id, chat)

    system_message = '''

    '''

    user_message = ""

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]

    try:
        response = lm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=4000,
            temperature=0.0
        )
        print(response)
        result = response.choices[0].message.content
        return result

    except Exception as e:
        print(f"Error formatting query: {e}")
        #----------------------------------------------------------------------------------------------
        return '' # Fallback to the original query if formatting fails
