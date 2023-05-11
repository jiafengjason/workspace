import requests
import sys

API_ENDPOINT = "https://api.openai.com/v1/chat/completions"

def call_chat_gpt(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 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",
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    response = requests.post(API_ENDPOINT, headers=headers, json=data)
    #print(response.json())
    return response.json()["choices"][0]["message"]["content"]

response = call_chat_gpt(sys.argv[1])
print(response)

