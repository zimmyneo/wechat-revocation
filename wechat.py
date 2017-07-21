#coding:utf-8
#author renqiang

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import time
import itchat
import os
import shutil

from itchat.content import *

#备份收到的消息
msg_backup_dict = {}
#备份文件存储位置
revocation_file_dir = './backup/'

#消息备份
@itchat.msg_register([TEXT,PICTURE, VIDEO, ATTACHMENT, MAP, SHARING, RECORDING, FRIENDS, CARD])
def text_receive(msg):
    #消息id
    msg_id = msg['MsgId']
    #消息创建时间
    msg_create_time = msg['CreateTime']
    #消息发送者
    msg_from = itchat.search_friends(userName=msg['FromUserName'])['NickName']
    msg_content, msg_sharing_url,msg_type = get_content_by_type(msg)
    msg_backup_dict.update({msg_id:{'msg_create_time':msg_create_time,  'msg_from': msg_from, 'msg_content':msg_content, 'msg_sharing_url':msg_sharing_url,'msg_type': msg_type}})
    clear_timeout_msg()


#更加消息类型获取消息内容
def get_content_by_type(msg):
    #消息类型
    msg_type = msg['Type']
    msg_content = ''
    msg_sharing_url = ''
    if msg_type == 'Text' :
        msg_content = msg['Text']
    elif msg_type == 'Sharing':
        msg_content = msg['Text']
        msg_sharing_url = msg['Url']
    elif msg_type == 'Picture':
        msg_content = msg['FileName'] 
        msg['Text'](msg_content)
    return msg_content, msg_sharing_url,msg_type


#通知获取，判断是否是撤回通并将撤回消息发送到消息助手
@itchat.msg_register([NOTE])
def get_revocation_msg(msg):
    if not os.path.exists(revocation_file_dir):
        os.makedirs(revocation_file_dir)

    revocation_msg_time = format_time(time.localtime())
    content = str(msg['Content'])
    if re.search(r"\<replacemsg\>\<\!\[CDATA\[.*撤回了一条消息\]\]\>\<\/replacemsg\>", content).group(0) != None: 
        revocation_msg_id = re.search('\<msgid\>(.*?)\<\/msgid\>',msg['Content']).group(1)
        revocation_msg = msg_backup_dict.get(revocation_msg_id,{})
        msg_from = str(revocation_msg['msg_from'])
        msg_content = str(revocation_msg['msg_content'])
        #拼接发送给消息助手的消息
        msg_result = '你的小伙伴：' \
                + msg_from \
                + ' 在 ' + str(revocation_msg_time) \
                + ' 撤回了一条消息 【'+ msg_content +'】'
        msg_type = revocation_msg['msg_type']
        if msg_type == 'Sharing':
            msg_result += r'分享链接:' \
                    + revocation_msg['msg_sharing_url']
        elif msg_type == 'Picture':
            msg_result += r'文件保存在脚本目录下backup目录中'
            #将文件移动到指定目录中
            shutil.move(msg_content,revocation_file_dir)

        #将撤回的消息发送给消息助手
        itchat.send(msg_result, toUserName='filehelper')
        msg_backup_dict.pop(revocation_msg_id)
        clear_timeout_msg()

#微信消息两份钟后不能撤回，清理超时消息
def clear_timeout_msg():
    for msgid in list(msg_backup_dict):
        if time.time() - msg_backup_dict.get(msgid,None)['msg_create_time'] > 125:
            msg = msg_backup_dict.pop(msgid)
            if msg['msg_type'] == 'Sharing' or msg['msg_type'] == 'Picture':
                os.remove(msg['msg_content'])
                        
#时间格式化为字符串类型
def format_time(mytime):
    result_time = mytime.tm_year.__str__() \
            + "/" + mytime.tm_mon.__str__() \
            + "/" + mytime.tm_mday.__str__() \
            + " " + mytime.tm_hour.__str__() \
            + ":" + mytime.tm_min.__str__() \
            + ":" + mytime.tm_sec.__str__()
    return result_time

if __name__ == '__main__':
    #生成图片二维码
    #itchat.auto_login()
    #生成命令行控制台二维码
    #itchat.auto_login(enableCmdQR=True)
    itchat.auto_login(enableCmdQR=2)
    itchat.run()
