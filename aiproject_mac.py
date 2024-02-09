from openai import OpenAI
import telegram
from telegram.ext import Application
from telegram.ext import filters, MessageHandler, CallbackContext
import asyncio
import os
import requests



with open('key.txt', 'r') as file:
    # 파일의 각 줄을 순회
    for line in file:
        # 줄바꿈 문자 제거 및 공백 제거
        line = line.strip()
        # '=' 기호를 기준으로 키와 값을 분리
        if "=" in line:
            key, value = line.split('=', 1)
            # 환경 변수 설정
            os.environ[key] = value.strip('"')


TELEGRAM_API_KEY=os.environ.get('TELEGRAM_API_KEY')
OEPNAI_API_KEY = os.environ.get('OPENAI_API_KEY')
CHAT_ID=os.environ.get('CHAT_ID')


def get_completion(client, query, prompt="You are a helpful assistant.", model="gpt-3.5-turbo"):
    messages = [{"role": "system", "content": prompt}, {"role": "user", "content": query}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content


async def echo(update, context):
        print('pass here chatgpt')
        client = OpenAI(api_key=OEPNAI_API_KEY)
        model = "gpt-3.5-turbo"
        user_id = update.effective_chat.id
        user_text = update.message.text
        print(user_text)
        query = user_text
        answer = get_completion(client, query)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)


async def receive_file(update, context: CallbackContext):
    print('pass here for checking to receive files')
    document = update.message.document

    file = await context.bot.get_file(document.file_id)
    # 저장할 경로 지정
    download_path = os.path.join('downloads', document.file_name)
    print(file)
    # 파일 다운로드
    # file.download(download_path)

    await update.message.reply_text(f'File {document.file_name} has been downloaded successfully.')


if __name__ == "__main__":
        application = Application.builder().token(TELEGRAM_API_KEY).build()
        echo_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
        application.add_handler(echo_handler)
        file_handler = MessageHandler(filters.Document.ALL, receive_file)
        application.add_handler(file_handler)
        # polling
        application.run_polling()

