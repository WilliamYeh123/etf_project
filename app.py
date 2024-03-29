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
from etf.fl import fiveline, draw_stock
import os
from flask_apscheduler import APScheduler

app = Flask(__name__)
config = configparser.ConfigParser()
config.read("config.ini")

line_bot_api = LineBotApi('Ff4GOYKQcVoLtiLR9Lpv9KsND8DG2VF4njWotsE8vNs/CDl68orI6p4wov5hzgcA5Gef/waOK+zb4jK6+8iH76xXw8/gAx+o8ky6ZYVTZDbJJYlSRafD7w2L1jH5wWbC6eYRBQQKD9E2Ib8+GtjRPgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('269bf1d1f6457e1969c6a458ea51867a')
# client_id = config['imgur_api']['Client_ID']
# client_secret = config['imgur_api']['Client_Secret']
# album_id = config['imgur_api']['Album_ID']
# API_Get_Image = config['other_api']['API_Get_Image']

# @app.route("/")
# def daily_recommend():
#     line_bot_api.push_message('U6658ff60e29de21166347e537c9b2f65',messages = TextSendMessage(text=fiveline()))
# class Config(object):
#     JOBS = [
#         {
#             'id': 'job1',
#             'func': daily_recommend,
#             #'args': (1, 2),
#             'trigger': 'cron',
#             'hour': 14,
#             'minute':15
#         }
#     ]
#     SCHEDULER_API_ENABLED = True

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
    if event.message.text.lower() == "etf":
        content = fiveline('etf')
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0

    if event.message.text.lower() == "stock":
        content = fiveline('stock')
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=content))
        return 0
    if 'draw' in event.message.text:
        stock_id = event.message.text[5:]
        draw_stock(stock_id)
        #content = fiveline('stock')
        image_path = f'etf/images/{stock_id}_fl.png'
        if os.path.exists(image_path):
            image_message = ImageSendMessage(original_content_url='file://' + image_path,
                                              preview_image_url='file://' + image_path)
            line_bot_api.reply_message(event.reply_token, image_message)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Image not found"))
        return 0

if __name__ == '__main__':
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    app.run()
