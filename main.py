import requests
import json
import re

# можно было и без этого импорта, но для безопасности :)
from dotenv import load_dotenv
import os
load_dotenv()

TOKEN = os.getenv('TOKEN')

ADMIN_CHAT_ID = '5547244228'

def send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    params = {'chat_id': chat_id, 'text': text}
    response = requests.post(url, data=params)
    return response.json()

def forward_message_to_admin(update):
    message = update['message']
    chat_id = message['chat']['id']
    text = message['text']
    forwarded_message = f'From: {chat_id}\n{text}'
    send_message(ADMIN_CHAT_ID, forwarded_message)

def extract_user_id(text):
    match = re.search(r'From: (\d+)', text)
    if match:
        return match.group(1)
    else:
        return None

def handle_admin_reply(update):
    message = update['message']
    reply_to_message = message.get('reply_to_message')
    if reply_to_message:
        original_chat_id = extract_user_id(reply_to_message['text'])
        if original_chat_id:
            text = message['text']
            send_message(original_chat_id, text)

def main():
    offset = None
    while True:
        url = f'https://api.telegram.org/bot{TOKEN}/getUpdates'
        params = {'offset': offset, 'timeout': 30}
        response = requests.get(url, params=params)
        updates = response.json()['result']
        if updates:
            for update in updates:
                offset = update['update_id'] + 1
                if 'message' in update and 'text' in update['message']:
                    if update['message']['chat']['id'] != int(ADMIN_CHAT_ID):
                        forward_message_to_admin(update)
                    else:
                        handle_admin_reply(update)

if __name__ == '__main__':
    main()
