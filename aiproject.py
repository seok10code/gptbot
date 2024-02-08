from openai import OpenAI
import telegram
from telegram.ext import Updater
from telegram.ext import CommandHandler, Filters, MessageHandler
import asyncio
import os
import requests
from PIL import Image
import pyheif
from time import datetime
 
# def heicTojpg():
        # heif_file = pyheif.read(src)
        # image = Image.frombytes(
        # heif_file.mode,
        # heif_file.size,
        # heif_file.data,
        # "raw",
        # heif_file.mode,
        # heif_file.stride,
        # )
        # print(heif_file)
        # dst = 'C0'+str(i)+'_SY_'+ datetime.datetime.now().strftime('%Y%m%d_')+ str(cnt).zfill(3)
        # dst = os.path.join(j, dst)
        # image.save(dst + ".jpg","JPEG")


TELEGRAM_API_KEY="6466827111:AAEZWZQQLedWR-tDxAOqJXPbvXGcenph0Y8"
OEPNAI_API_KEY = "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"
CHAT_ID="6549772508"
# token
# with open("./token.txt") as f:
#     lines = f.readlines()
#     token = lines[0].strip()



def get_completion(client, query, prompt="You are a helpful assistant.", model="gpt-3.5-turbo"):
    messages = [{"role": "system", "content": prompt}, {"role": "user", "content": query}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message.content


def echo(update, context):
        client = OpenAI(api_key=OEPNAI_API_KEY)
        model = "gpt-3.5-turbo"
        user_id = update.effective_chat.id
        user_text = update.message.text
        query = user_text
        answer = get_completion(client, query)
        # messages = [
        #         {"role": "system", "content": "You are a helpful assistant."},
        #         {"role": "user", "content": query}
        # ]


        # response = client.chat.completions.create(model=model,
        # messages=messages)
        # answer = response.choices[0].message.content
        context.bot.send_message(chat_id=update.effective_chat.id, text=answer)


if __name__ == "__main__":
        
        updater = Updater(token=TELEGRAM_API_KEY, use_context=True)
        dispatcher = updater.dispatcher
        echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
        dispatcher.add_handler(echo_handler)

        # polling
        updater.start_polling()


