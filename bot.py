import sys, os, subprocess, time, json, logging, telegram, threading, datetime, requests, redis
from time import sleep
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

json_str = os.popen("cat ~/.secrets/key.json").read()
json_dict=json.loads(json_str)
mytoken=json_dict['telegram_bot']['token']
rootid =json_dict['telegram_bot']['rootid']
userid =json_dict['telegram_bot']['userid']
sudopw =json_dict['telegram_bot']['sudopw']

xiaobo_url="/tmp/mojo_webqq_qrcode_default.png"
myredis = redis.Redis(host='localhost', port=6379, db=5)

updater = Updater(token=mytoken)
dispatcher = updater.dispatcher

ERR_NO_PERMISSION="请先使用/su取得系统权限！"

def user_auth(telegram_id):
    global rootid, userid
    if str(telegram_id) == str(rootid) or str(telegram_id) in userid:
        return True
    else:
        return False

def chk_xiaobo_sts_by_ps():
    global myredis
    if int(subprocess.check_output(['ps ax | grep [x]iaobo | sed \'s/^\s*//\' | cut -d " " -f 1 | wc -l'],shell=True)) > 0:
        return True
    else:
        myredis.set('XB_STS', False)
        return False

def chk_xiaobo_sts_by_redis():
    global myredis
    if myredis.get('XB_STS').decode('utf-8') == 'True':
        return True
    else:
        return False

def chk_xiaobo_sts():
    if chk_xiaobo_sts_by_ps() == True and chk_xiaobo_sts_by_redis() == True:
        return True
    else:
        return False

def xb(bot, update):
    global myredis
    chk_xiaobo_sts_by_ps()
    logging.info(str(update.message.chat_id) + " send /xb")
    if user_auth(update.message.chat_id):
        os.system('rm '+xiaobo_url)
        os.system('kill -9 `ps ax | grep [x]iaobo | sed \'s/^\s*//\' | cut -d " " -f 1` && sleep 5')
        os.system('tmux new-window -n xiaobo "cd ~/workspaces/xiaoboQQBot/src && python xiaobo.py"')
        bot.send_message(chat_id=update.message.chat_id, text="小波已重启！正在准备二维码...")
        sleep(5)
        try:
            xiaobo_qr = open(xiaobo_url, 'rb')
            bot.send_photo(chat_id=update.message.chat_id, photo=xiaobo_qr)
            xiaobo_qr.close()
        except:
            if chk_xiaobo_sts() == True:
                bot.send_message(chat_id=update.message.chat_id, text='小波('+ myredis.get('XB_LAST_LOGIN_ID').decode('utf-8')+')已自动登录。\n在线开始时间：'+myredis.get('XB_LAST_LOGIN_TIME').decode('utf-8'))
            else:
                logging.warning(str(update.message.chat_id) + " xiaobo_url does not exist")
                bot.send_message(chat_id=update.message.chat_id, text="没有二维码文件，请用/qr手动获取")

def qr(bot, update):
    logging.info(str(update.message.chat_id) + " send /qr")
    if user_auth(update.message.chat_id):
        try:
            xiaobo_qr = open(xiaobo_url, 'rb')
            bot.send_photo(chat_id=update.message.chat_id, photo=xiaobo_qr)
            xiaobo_qr.close()
        except:
            logging.warning(str(update.message.chat_id) + " xiaobo_url does not exist")
            bot.send_message(chat_id=update.message.chat_id, text="没有二维码文件，请先/xb，如果仍然无法开启则使用cc")
        else:
            bot.send_message(chat_id=update.message.chat_id, text="小波扫描二维码")
    else:
        bot.send_message(chat_id=update.message.chat_id, text=ERR_NO_PERMISSION)

def sts(bot, update):
    global myredis
    logging.info(str(update.message.chat_id) + " send /sts")
    if user_auth(update.message.chat_id):
        if chk_xiaobo_sts() == True:
            bot.send_message(chat_id=update.message.chat_id, text='小波('+ myredis.get('XB_LAST_LOGIN_ID').decode('utf-8')+')当前在线。\n在线开始时间：'+myredis.get('XB_LAST_LOGIN_TIME').decode('utf-8'))
        elif chk_xiaobo_sts_by_ps() == False:
            bot.send_message(chat_id=update.message.chat_id, text='小波当前不在线 [ERRCODE: NO_PSAUX_STS]')
        elif chk_xiaobo_sts_by_redis() == False:
            bot.send_message(chat_id=update.message.chat_id, text='小波当前不在线 [ERRCODE: NO_REDIS_STS]')
    else:
        bot.send_message(chat_id=update.message.chat_id, text=ERR_NO_PERMISSION)

def cc(bot, update):
    logging.info(str(update.message.chat_id) + " send /cc")
    if user_auth(update.message.chat_id):
        os.system('rm ~/workspaces/xiaoboQQBot/src/cookie/*')
        os.system('rm ~/workspaces/xiaoboQQBot/src/smart_qq_bot/__pycache__/*')
        os.system('rm ~/workspaces/xiaoboQQBot/src/smart_qq_plugins/__pycache__/*')
        bot.send_message(chat_id=update.message.chat_id, text="小波的缓存已清除！")
    else:
        bot.send_message(chat_id=update.message.chat_id, text=ERR_NO_PERMISSION)

def su(bot, update, args):
    logging.info(str(update.message.chat_id) + " send /su " + ' '.join(args))
    global rootid
    if len(args) > 0 and args[0] == sudopw:
        bot.send_message(chat_id=rootid, text="用户"+str(update.message.chat_id)+"已经获取系统通知权限！")
        rootid = update.message.chat_id
        bot.send_message(chat_id=update.message.chat_id, text="已经获取系统通知权限！")
    else:
        bot.send_message(chat_id=rootid, text="用户"+str(update.message.chat_id)+"尝试获取系统通知权限失败！" + ' '.join(args))
        bot.send_message(chat_id=update.message.chat_id, text="密码错误，无法系统通知权限！")

def n(bot, update, args):
    logging.info(str(update.message.chat_id) + " send /n " + ' '.join(args))
    if str(update.message.chat_id) == str(rootid):
        if len(args) > 0 and len(args[0]) > 0:
            for uid in userid:
                bot.send_message(chat_id=uid, text=str(args[0]))
            bot.send_message(chat_id=rootid, text="已经向所有管理员群发系统消息：\n"+str(args[0]))
        else:
            bot.send_message(chat_id=update.message.chat_id, text='群发消息格式不正确！')
    else:
        bot.send_message(chat_id=update.message.chat_id, text=ERR_NO_PERMISSION)

def show_help(bot, update):
    logging.info(str(update.message.chat_id) + " " + update.message.text)
    bot.send_message(chat_id=update.message.chat_id, text="命令一览：\n/xb - 重启小波\n/qr - 发送小波的二维码\n/sts - 查看当前小波运行状态\n/su - 管理员指令\nn - 管理员群发\ncc - [慎用]清除小波的缓存")

#qq online monitoring bot
class myThread1(threading.Thread):
    def __init__(self):
        super(myThread1, self).__init__()

    def run(self):
        global myredis
        alert = False
        logout = 0
        login  = 0
        fq = 0
        while True:
            pic_exist = os.path.exists(xiaobo_url)
            if pic_exist == True and alert == False:
                logout = datetime.datetime.now()
                online_status='小波已掉线！\n掉线时间: '+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                logging.info(online_status)
                for uid in userid:
                    bot.send_message(chat_id=uid, text=online_status)
                bot.send_message(chat_id=rootid, text=online_status)
                alert = True
            elif pic_exist == False and alert == True:
                login = datetime.datetime.now()
                logout_duration = (login - logout).seconds
                logout_sec = str(logout_duration % 60)
                logout_min = str(int(logout_duration / 60) % 60)
                logout_hour   = str(int(logout_duration / 3600))
                online_status='小波已恢复上线\n上线时间: '+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n本次掉线: '+logout_hour+'小时'+logout_min+'分'+logout_sec+'秒'
                logging.info(online_status)
                for uid in userid:
                    bot.send_message(chat_id=uid, text=online_status)
                bot.send_message(chat_id=rootid, text=online_status)
                alert = False

            #read xb fq from redis
            new_fq = myredis.get('XB_REPLY_FREQUENCY').decode('utf-8')
            if fq != 0 and fq != new_fq:
                bot.send_message(chat_id=rootid, text='小波随机吐槽频率改为 '+ new_fq +' %')
            fq = new_fq
            sleep(5)

if __name__ == '__main__':
    xb_handler = CommandHandler('xb', xb)
    qr_handler = CommandHandler('qr', qr)
    sts_handler = CommandHandler('sts', sts)
    cc_handler = CommandHandler('cc', cc)
    su_handler = CommandHandler('su', su, pass_args=True)
    n_handler = CommandHandler('n', n, pass_args=True)
    help_handler = MessageHandler(Filters.text, show_help)

    dispatcher.add_handler(xb_handler)
    dispatcher.add_handler(qr_handler)
    dispatcher.add_handler(sts_handler)
    dispatcher.add_handler(cc_handler)
    dispatcher.add_handler(su_handler)
    dispatcher.add_handler(n_handler)
    dispatcher.add_handler(help_handler)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
    bot = telegram.Bot(token=mytoken)
    try:
        th1 = myThread1()
        th1.start()
    except:
        logging.warning("无法启动小波管理台！")
        bot.send_message(chat_id=rootid, text="无法启动小波管理台！")
    else:
        logging.info("小波管理台已启动，输入任何消息查看使用帮助。")
        bot.send_message(chat_id=rootid, text="小波管理台已启动，输入任何消息查看使用帮助。")
    finally:
        updater.start_polling()