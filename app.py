import requests
import re
import random
import configparser
from bs4 import BeautifulSoup
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)
config = configparser.ConfigParser()
config.read("config.ini")

line_bot_api = LineBotApi('Ff4GOYKQcVoLtiLR9Lpv9KsND8DG2VF4njWotsE8vNs/CDl68orI6p4wov5hzgcA5Gef/waOK+zb4jK6+8iH76xXw8/gAx+o8ky6ZYVTZDbJJYlSRafD7w2L1jH5wWbC6eYRBQQKD9E2Ib8+GtjRPgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('269bf1d1f6457e1969c6a458ea51867a')
# client_id = config['imgur_api']['Client_ID']
# client_secret = config['imgur_api']['Client_Secret']
# album_id = config['imgur_api']['Album_ID']
# API_Get_Image = config['other_api']['API_Get_Image']


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    # print("body:",body)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'ok'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("event.reply_token:", event.reply_token)
    print("event.message.text:", event.message.text)
    if event.message.text.lower() == "hello":
        content = 'hi~'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0

if __name__ == '__main__':
    app.run()
