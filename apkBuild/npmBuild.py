#!/usr/local/bin/python3
#coding:utf-8

import os
import sys
import boto3,json
import requests
import time,datetime
from MyQR import myqr

build_env = sys.argv[1]
ver_tag = '%s-%s' % (sys.argv[1],sys.argv[2])
# 声明环境变量
os.system('export ANDROID_HOME=/usr/src/android-sdk-linux')
os.system('export PATH=${PATH}:${ANDROID_HOME}/tools')
os.system('export PATH=${PATH}:${ANDROID_HOME}/platform-tools')
# 工作目录相关变量
# /root/workspace/pinecone-fish
r_path = os.getcwd()
# /root/workspace/pinecone-fish/android/app/build/outputs/apk/release/app-release.apk
apk_path = r_path + '/android/app/build/outputs/apk/release/app-release.apk'
# /home/ec2-user/node_modules
nm_dir = '/home/ec2-user/node_modules'

def preBuild():
    os.chdir(r_path)
    print('>> 复制.env配置文件到工作目录')
    os.system('\cp /home/ec2-user/.env* %s/' % r_path)
    print('>> 复制编译秘钥到工作目录')
    os.system('\cp /home/ec2-user/zhiwen-release-key.keystore %s/android/app/' % r_path)
    print('>> 已切换到pinecone-fish项目的代码根目录')
    print('>> 启用定制化node_modules静态资源')
    os.system('\cp -r %s %s/node_modules' % (nm_dir,r_path))
    if os.path.isfile(apk_path):
        print('>> 当前项目目录已存在APK工程文件\n>> 文件路径在%s' % apk_path)
        print('>> 文件信息如下：')
        os.system('stat %s' % apk_path)

def postBuild():
    print('>> 清空node_modules静态资源，整理磁盘空间')
    os.system('if [ -d ./node_modules ]; then rm -rf ./node_modules ;fi')

def upload_file(file_name, bucket, object_name=None):
    if object_name is None:
        object_name = file_name
    s3_client = boto3.client('s3')
    try:
        if file_name.find('.jpg') > 0:
            response = s3_client.upload_file(file_name, bucket, object_name,ExtraArgs={'ContentType': "image/jpeg", 'ACL': "public-read"})
        else:
            response = s3_client.upload_file(file_name, bucket, object_name,ExtraArgs={'ACL': "public-read"})
    except ClientError as e:
        logging.error(e)
        return False
    return True

def qr_code(appUrl,qrImageName,qr_path):
    output_path = qr_path
    version, level, qr_name = myqr.run(
        appUrl,
        version=1,  # 二维码大小
        level='L',  # 纠错等级，L生成二维码较小
        picture=None,  # 中央配图
        colorized=False,  # 染色
        contrast=1.0,  # 对比度
        brightness=1.0,  # 亮度
        save_name=qrImageName,  # 二维码输出文件名
        save_dir=output_path  # 输出目录
    )

def dingMessage(build_env,time_tag,picUrl):
    botWebHook = 'https://oapi.dingtalk.com/robot/send?access_token=e4b53f173429b731446331e42c6139eb666d15319d78e4fe8bf4b6ce899e335a'
    header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8"
    }
    message = {
        "msgtype": "markdown",
        "markdown": {
            "title":"Zhiwen Client APK Build Report",
            "text": "# APK Build Report \n\n#### 发布环境：%s\n\n#### 版本号：%s\n\n## 点击蓝色链接跳转到二维码页面\n\n [二维码](%s)\n"\
                    % (build_env,time_tag,picUrl)
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

def main():
    preBuild()
    # time.sleep(2)
    now = datetime.datetime.utcnow()
    time_tag = '%s-%s-%s-%s-%s' % (now.month, now.day, now.hour, now.minute, now.second)
    obj_name = '%s/zhiwen-app-client_%s.apk' % (build_env, time_tag)
    apk_bak_name = 'zhiwen-app-client_%s.apk' % (time_tag)

    print('>> 开始执行APK编译流程\n>> 编译%s版本的APK程序包' % build_env)
    # time.sleep(2)
    os.system('npm run build-%s-android' % build_env)

    print('>> 开始同步 apk-%s 到S3' % build_env)
    upload_file(apk_path,'zhiwen-app-client',obj_name)
    print('>> %s已上传到S3存储桶' % obj_name)

    print('>> 生成对应环境APK程序包的二维码并同步到S3')
    # appUrl = https://zhiwen-app-client.s3.cn-northwest-1.amazonaws.com.cn/release/zhiwen-app-client_7-20-17-30-28.apk
    prefix = 'https://zhiwen-app-client.s3.cn-northwest-1.amazonaws.com.cn/'
    appUrl = prefix + obj_name
    picUrl = appUrl.replace('.apk','.jpg')

    qrImageName = obj_name.replace('.apk','.jpg').replace('%s/'% build_env,'')
    qr_path = r_path +'/'
    qr_code(appUrl,qrImageName,qr_path)
    upload_file('%s%s' % (qr_path,qrImageName), 'zhiwen-app-client', '%s/%s' % (build_env,qrImageName))

    print('>> 发送钉钉机器人消息通知开发者')
    dingMessage(build_env, time_tag, picUrl)

    postBuild()

if __name__ == '__main__':
    main()