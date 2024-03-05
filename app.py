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
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

app = Flask(__name__)
config = configparser.ConfigParser()
config.read("config.ini")


parser = WebhookParser(config['line_bot']['Channel_Secret'])

line_bot_api = LineBotApi(config['line_bot']['Channel_Access_Token'])
handler = WebhookHandler(config['line_bot']['Channel_Secret'])
# client_id = config['imgur_api']['Client_ID']
# client_secret = config['imgur_api']['Client_Secret']
# album_id = config['imgur_api']['Album_ID']
# API_Get_Image = config['other_api']['API_Get_Image']
ETF_id = ['1','2']

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
 
        try:
            events = parser.parse(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
 
        for event in events:
            if isinstance(event, MessageEvent):  # 如果有訊息事件
                if event.message.text == 'hello': #查看服務
                    line_bot_api.reply_message(  
                    event.reply_token,
                    TextSendMessage(text='選擇基金:\n1 : 國內成分證券ETF \n2 : 國外成分證券ETF')
                )
                # elif event.message.text in ETF_id:
                #     etf_id = int(event.message.text)
                #     reply = fl.fiveline(etf_id)
                #     line_bot_api.reply_message(  
                #     event.reply_token,
                #     TextSendMessage(text=reply)
                # )
                # else:
                #     line_bot_api.reply_message(  # 回復傳入的訊息文字
                #     event.reply_token,
                #     TextSendMessage(text='error')
                # )
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

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
