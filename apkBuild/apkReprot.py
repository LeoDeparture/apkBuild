#!/usr/local/bin/python3
#coding:utf-8
import os,requests,json

d = {
    'Dev':{
        "messageURL":"https://zhiwen-app-client.s3.cn-northwest-1.amazonaws.com.cn/dev/zhiwen-app-client_7-21-9-18-38.apk",
        "picURL":"https://zhiwen-app-client.s3.cn-northwest-1.amazonaws.com.cn/dev/zhiwen-app-client_7-21-9-18-38.jpg"
    },
    'Staging':
    {
        "messageURL":"https://zhiwen-app-client.s3.cn-northwest-1.amazonaws.com.cn/staging/zhiwen-app-client_7-21-6-32-56.apk",
        "picURL":"https://zhiwen-app-client.s3.cn-northwest-1.amazonaws.com.cn/staging/zhiwen-app-client_7-21-6-32-56.jpg"
    },
    'Release':
    {
        "messageURL":"https://zhiwen-app-client.s3.cn-northwest-1.amazonaws.com.cn/release/zhiwen-app-client_7-21-9-18-39.apk",
        "picURL":"https://zhiwen-app-client.s3.cn-northwest-1.amazonaws.com.cn/release/zhiwen-app-client_7-21-9-18-39.jpg"
    }
}

def dingMessage(context=None):
    botWebHook = 'https://oapi.dingtalk.com/robot/send?access_token=e4b53f173429b731446331e42c6139eb666d15319d78e4fe8bf4b6ce899e335a'
    header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
    }
    message = {
        "msgtype": "markdown",
        "markdown": {
            "title":"Zhiwen Client APK Build Report",
            "text": "# APK Build Report \n\n#### 发布环境：bbb\n\n#### 版本号：aaa\n\n## 点击蓝色链接跳转到二维码页面\n\n [二维码](%s)\n"\
                    % (d['Release']['picURL'])
        },
        "at": {
            "atMobiles": [
                ""
            ],
            "isAtAll": False
        }
    }
    message_json = json.dumps(message)
    apk_build_report = requests.post(url=botWebHook,headers=header,data=message_json)

dingMessage()
print(d['Release']['picURL'])