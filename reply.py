from openai_api import chat_text

def reply_with_text(input_text, messages = None):
    
    if messages == None:
        messages = [
            {"role": "assistant", "content": [{"text": "Hello! How can I help you today?"}]}
        ]
    messages.append(
        {
            "role": "user",
            "content": [
                {"type": "text", "text": input_text}
            ]
        }
    )
    response = chat_text(
        messages,
        model = 'gpt-4o'
    )
    messages.append(
        {
            "role": "assistant",
            "content": [
                {
                "type": "text",
                "text": response
                }
            ]
        }
    )
    return messages, response