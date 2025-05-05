import base64
import json
from PIL import Image
import io

def desc_image(lm_client, image):
    """
    Generate a description for an image using OpenAI's GPT-4o mini vision model.

    Parameters:
    - lm_client: An instance of OpenAI's API client.
    - image: A file-like object containing the image to be described.

    Returns:
    - A string containing the description of the image.
    """
    try:
        # Determine the MIME type of the image
        image_format = Image.open(image).format.lower()  # e.g., 'jpeg', 'png'
        mime_type = f"image/{image_format}"

        # Reset file pointer to the beginning (needed after reading format)
        image.seek(0)

        # Encode the image to Base64
        image_base64 = base64.b64encode(image.read()).decode('utf-8')

        # Construct messages
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that describes images."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Perform OCR meaningfully, you can compile and dedupe info but don't add terminologies.",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime_type};base64,{image_base64}"
                        }
                    }
                ]
            }
        ]

        # Prepare the API request
        response = lm_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1000,
            temperature=0.0
        )

        # Extract the description from the response
        description = response.choices[0].message.content
        return description

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

