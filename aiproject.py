from openai import OpenAI
import os
import requests


OEPNAI_API_KEY = "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"
client = OpenAI(api_key=OEPNAI_API_KEY)


# 모델 - GPT 3.5 Turbo 선택
model = "gpt-3.5-turbo"

# 질문 작성하기
query = "안녕"

# 메시지 설정하기
messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": query}
]

# ChatGPT API 호출하기
response = client.chat.completions.create(model=model,
messages=messages)
answer = response.choices[0].message.content
print(answer)



# def get_completion(prompt, model="gpt-3.5-turbo"):
#     messages = [{"role": "user", "content": prompt}]
#     response = openai.ChatCompletion.create(
#         model=model,
#         messages=messages,
#         temperature=0,
#     )
#     return response.choices[0].message["content"]