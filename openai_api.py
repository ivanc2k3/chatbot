from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

def chat_text(messages, model, temperature=1, max_tokens=2048, top_p=1, frequency_penalty=0, presence_penalty=0, stop=[]):
    # messages=[
    #     {"role": "system", "content": "You are a helpful assistant."},
    #     {"role": "user", "content": "Hello!"}
    # ]
    
    try:
        client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            # stop=stop
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"error: {str(e)}"