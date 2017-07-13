#coding:utf-8
#autor renqiang

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import time
import itchat

from itchat.content import *

#备份收到的消息
msg_backup_dict = {}

#消息备份
@itchat.msg_register([TEXT,PICTURE, VIDEO, ATTACHMENT, MAP, SHARING, RECORDING, FRIENDS, CARD])
def text_receive(msg):
    current_time = time.localtime()
    #消息id
    msg_id = msg['MsgId']
    msg_create_time = msg['CreateTime']
    msg_type = msg['Type']
    msg_from = itchat.search_friends(userName=msg['FromUserName'])['NickName']
    msg_content = ''
    if msg_type == 'Text':
        msg_content = msg['Content']

    msg_backup_dict.update({msg_id:{'msg_create_time':msg_create_time,  'msg_from': msg_from, 'msg_content':msg_content, 'msg_type': msg_type}})


#通知获取，判断是否是撤回通知
@itchat.msg_register([NOTE])
def get_revocation_msg(msg):
    revocation_msg_time = format_time(time.localtime())
    content = str(msg['Content'])
    if re.search(r"\<replacemsg\>\<\!\[CDATA\[.*撤回了一条消息\]\]\>\<\/replacemsg\>", content).group(0) != None: 
        revocation_msg_id = re.search('\<msgid\>(.*?)\<\/msgid\>',msg['Content']).group(1)
        revocation_msg = msg_backup_dict.get(revocation_msg_id,{})
        msg_from = str(revocation_msg['msg_from'])
        msg_content = str(revocation_msg['msg_content'])
        msg_result = '你的小伙伴：' \
                + msg_from \
                + '在 ' + str(revocation_msg_time) \
                + '撤回了一条消息 【'+ msg_content +'】'
        itchat.send(msg_result, toUserName='filehelper')

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
    #命令行控制台生成二维码
    #itchat.auto_login(enableCmdQR=True)
    itchat.auto_login(enableCmdQR=2)
    itchat.run()
