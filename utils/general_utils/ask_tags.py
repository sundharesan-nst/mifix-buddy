import json

custom_functions_tag = [
    {
        "name": "return_tags",
        "description": "to be used to return list of words/tags.",
        "parameters": {
            "type": "object",
            "properties": {
                "tag_list": {
                    "type": "array",
                    "description": "List of tags directly extracted from the chunks given",
                    "items": {"type": "string"},
                },
            },
            "required": ["tag_list"],
        },
    }
]

def ask_gpt_tags(lm_client, smart_chunk):

    print(smart_chunk,'----------- askgpt tags\n\n\n')

    system_message = "You will be given a Query. You must behave as an extremly smart named entity recognition software. Your job is to extract ALL of the entitties from the given piece of text. I will use these tags to filter data. If the query isn't in english language, convert the tags to closest meaning in english. return a 'list' of 'string tags'."
    user_message = "Query: \n" + smart_chunk 
    msg = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]
    
    print("-----------------------")
    response = lm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=msg,
        max_tokens=6000,
        temperature=0.0,
        seed=1,
        functions=custom_functions_tag,
        function_call={"name": "return_tags"},
    )

    try:
        reply = json.loads(response.choices[0].message.function_call.arguments)[
            "tag_list"
        ]
        print(reply)
    except Exception as e:
        print(e)
        reply = []
    return reply