from openai import OpenAI
import telegram
from telegram.ext import Application
from telegram.ext import filters, MessageHandler, CallbackContext

import asyncio
import os
import requests
import json

from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient




with open('key.txt', 'r') as file:
    # 파일의 각 줄을 순회
    for line in file:
        # 줄바꿈 문자 제거 및 공백 제거
        line = line.strip()
        # '=' 기호를 기준으로 키와 값을 분리
        if "=" in line:
            key, value = line.split('=', 1)
            # 환경 변수 설정

            os.environ[f'{key}'] = value.strip('"')

TELEGRAM_API_KEY=os.environ.get('TELEGRAM_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
CHAT_ID=os.environ.get('CHAT_ID')
FORM_RECOGNIZER_KEY=os.environ.get('FORM_RECOGNIZER_KEY')
FORM_RECOGNIZER_ENDPOINT=os.environ.get('FORM_RECOGNIZER_ENDPOINT')
STORAGE_CONSTR =os.environ.get('STORAGE_CONSTR')
SOURCE_NAME =os.environ.get('SOURCE_NAME')
FILE_NAME = ""


def upload_to_blob(file_url: str, blob_service_client: BlobServiceClient, container_name: str, blob_name: str):
    # 컨테이너 클라이언트 생성
    container_client = blob_service_client.get_container_client(container=container_name)
    
    # GET 요청으로 파일 다운로드 및 Blob Storage에 업로드
    with requests.get(file_url, stream=True) as r:
        r.raise_for_status()  # 요청이 성공했는지 확인
        
        # Blob Storage에 파일 업로드
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(data=r.raw, overwrite=True)
        print(f'File uploaded to blob: {blob_name}')





def get_blob_url():

    FILE_NAME =os.environ.get('FILE_NAME')
    # FILE_NAME = "test01.pdf"
    SAS=os.environ.get('SAS')
    container = ContainerClient.from_connection_string(
         conn_str=STORAGE_CONSTR,
         container_name = SOURCE_NAME,
        #  credential=sas
    )

    blob_list = container.list_blobs()
    blob_url = container.url

    for blob in blob_list:
        if blob.name == FILE_NAME:  
            formUrl = blob_url+"/"+blob.name
    return formUrl



def analyze_read():
    formUrl = get_blob_url()

    document_analysis_client = DocumentAnalysisClient(
        endpoint=FORM_RECOGNIZER_ENDPOINT, credential=AzureKeyCredential(FORM_RECOGNIZER_KEY)
    )
    print(formUrl)
    print('='*60)
    poller = document_analysis_client.begin_analyze_document_from_url("prebuilt-read", formUrl)
    result = poller.result()

    # print("Document contains contestn:" , result.content)
    with open("/mnt/c/Users/김석원/Desktop/python_script/pdf_file_test.txt", "w") as text_file:
         text_file.write(result.content+'\n\n\n\n\n')
    # for page in result.content:
        # with open("/mnt/c/Users/김석원/Desktop/python_script/pdf_file.txt", "w") as text_file:
            # text_file.write(f"{page_num}:" + f"{page}" + "\n")
        # print("="*70)
        # print(page)



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
        client = OpenAI(api_key=OPENAI_API_KEY)
        model = "gpt-3.5-turbo"
        user_id = update.effective_chat.id
        user_text = update.message.text
        print(user_text)
        query = user_text
        answer = get_completion(client, query)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=answer)


async def receive_file(update, context: CallbackContext):

    document = update.message.document

    file = await context.bot.get_file(document.file_id)
    # 저장할 경로 지정
    download_path = os.path.join('downloads', document.file_name)
    file_url = file.file_path
    file_name = document.file_name
    os.environ['FILE_NAME'] = file_name
    os.environ['FILE_URL']=file_url
    # 파일 다운로드
    # Azure Blob Storage 설정
    blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONSTR)

    # Blob Storage에 파일 업로드 실행
    upload_to_blob(os.environ.get('FILE_URL'), blob_service_client, SOURCE_NAME, os.environ.get('FILE_NAME'))

    await update.message.reply_text(f'File {document.file_name} has been downloaded successfully.')


if __name__ == "__main__":
        application = Application.builder().token(TELEGRAM_API_KEY).build()
        echo_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, echo)
        application.add_handler(echo_handler)
        file_handler = MessageHandler(filters.Document.ALL, receive_file)
        application.add_handler(file_handler)
        # polling
        application.run_polling()
        # analyze_read()


