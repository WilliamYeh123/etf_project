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

line_bot_api = LineBotApi(config['line_bot']['Channel_Access_Token'])
handler = WebhookHandler(config['line_bot']['Channel_Secret'])
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

    # if event.message.text == "來張 imgur 正妹圖片":
    #     client = ImgurClient(client_id, client_secret)
    #     images = client.get_album_images(album_id)
    #     index = random.randint(0, len(images) - 1)
    #     url = images[index].link
    #     image_message = ImageSendMessage(
    #         original_content_url=url,
    #         preview_image_url=url
    #     )
    #     line_bot_api.reply_message(
    #         event.reply_token, image_message)
    #     return 0


if __name__ == '__main__':
    app.run()
