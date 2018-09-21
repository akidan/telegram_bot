import sys, os, time, json, logging, telegram, threading, datetime, requests
from time import sleep
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

json_str = os.popen("cat ~/.secrets/key.json").read()
json_dict=json.loads(json_str)
mytoken=json_dict['telegram_bot']['token']
rootid =json_dict['telegram_bot']['rootid']
userid =json_dict['telegram_bot']['userid']
sudopw =json_dict['telegram_bot']['sudopw']

xiaobo_url="/tmp/mojo_webqq_qrcode_default.png"

updater = Updater(token=mytoken)
dispatcher = updater.dispatcher

ERR_NO_PERMISSION="请先使用/su取得系统权限！"

def user_auth(telegram_id):
    global rootid, userid
    if str(telegram_id) == str(rootid) or str(telegram_id) is in str(userid):
        return True
    else:
        return False

def xb(bot, update):
    logging.info(str(update.message.chat_id) + " send /xb")
    if  user_auth(update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text=ERR_NO_PERMISSION)
    else:
        os.system('rm '+xiaobo_url)
        os.system('kill -9 `ps ax | grep [x]iaobo | sed \'s/^\s*//\' | cut -d " " -f 1` && sleep 5')
        os.system('tmux new-window -n xiaobo "cd ~/workspaces/xiaoboQQBot/src && python xiaobo.py"')
        bot.send_message(chat_id=update.message.chat_id, text="小波已重启！")
        os.system('sleep 5')

def qr(bot, update):
    logging.info(str(update.message.chat_id) + " send /qr")
    if  user_auth(update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text=ERR_NO_PERMISSION)
    else:
        try:
            xiaobo_qr = open(xiaobo_url, 'rb')
            bot.send_photo(chat_id=update.message.chat_id, photo=xiaobo_qr)
            xiaobo_qr.close()
        except:
            logging.warning(str(update.message.chat_id) + " xiaobo_url does not exist")
            bot.send_message(chat_id=update.message.chat_id, text="没有二维码文件，请先/xb")
        else:
            bot.send_message(chat_id=update.message.chat_id, text="小波扫描二维码")

def sts(bot, update):
    logging.info(str(update.message.chat_id) + " send /sts")
    if  True:#user_auth(update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text='这个功能还没写好！')#ERR_NO_PERMISSION)
    else:
        try:
            xiaobo_qr = open(xiaobo_url, 'rb')
            bot.send_photo(chat_id=update.message.chat_id, photo=xiaobo_qr)
            xiaobo_qr.close()
        except:
            logging.warning(str(update.message.chat_id) + " xiaobo_url does not exist")
            bot.send_message(chat_id=update.message.chat_id, text="没有二维码文件，请先/xb")
        else:
            bot.send_message(chat_id=update.message.chat_id, text="小波扫描二维码")

def cc(bot, update):
    logging.info(str(update.message.chat_id) + " send /cc")
    if  user_auth(update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text=ERR_NO_PERMISSION)
    else:
        os.system('rm ~/workspaces/xiaoboQQBot/src/cookie/*')
        os.system('rm ~/workspaces/xiaoboQQBot/src/smart_qq_bot/__pycache__/*')
        os.system('rm ~/workspaces/xiaoboQQBot/src/smart_qq_plugins/__pycache__/*')
        bot.send_message(chat_id=update.message.chat_id, text="小波的缓存已清除！")

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

def show_help(bot, update):
    logging.info(str(update.message.chat_id) + " " + update.message.text)
    bot.send_message(chat_id=update.message.chat_id, text="命令一览：\n/xb - 重启小波\n/qr - 发送小波的二维码\n/su - 管理员指令\ncc - [慎用]清除小波的缓存")

#qq online monitoring bot
class myThread1(threading.Thread):
    def __init__(self):
        super(myThread1, self).__init__()

    def run(self):
        alert = False
        logout = 0
        login  = 0
        while True:
            pic_exist = os.path.exists(xiaobo_url)
            if pic_exist == True and alert == False:
                logout = datetime.datetime.now()
                online_status='小波已掉线！\n掉线时间: '+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                logging.info(online_status)
                bot.send_message(chat_id=userid, text=online_status)
                alert = True
            elif pic_exist == False and alert == True:
                login = datetime.datetime.now()
                logout_duration = (login - logout).seconds
                logout_sec = str(logout_duration % 60)
                logout_min = str(int(logout_duration / 60) % 60)
                logout_hour   = str(int(logout_duration / 3600))
                online_status='小波已恢复上线\n上线时间: '+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'\n本次掉线: '+logout_hour+'小时'+logout_min+'分'+logout_sec+'秒'
                logging.info(online_status)
                bot.send_message(chat_id=userid, text=online_status)
                alert = False
            sleep(5)

if __name__ == '__main__':
    xb_handler = CommandHandler('xb', xb)
    qq_handler = CommandHandler('qr', qr)
    sts_handler = CommandHandler('sts', sts)
    cc_handler = CommandHandler('cc', cc)
    su_handler = CommandHandler('su', su, pass_args=True)
    help_handler = MessageHandler(Filters.text, show_help)

    dispatcher.add_handler(xb_handler)
    dispatcher.add_handler(qr_handler)
    dispatcher.add_handler(sts_handler)
    dispatcher.add_handler(cc_handler)
    dispatcher.add_handler(su_handler)
    dispatcher.add_handler(help_handler)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
    bot = telegram.Bot(token=mytoken)
    try:
        th1 = myThread1()
        th1.start()
    except:
        logging.warning("无法启动小波管理台！")
        bot.send_message(chat_id=userid, text="无法启动小波管理台！")
    else:
        logging.info("小波管理台已启动，输入任何消息查看使用帮助。")
        bot.send_message(chat_id=userid, text="小波管理台已启动，输入任何消息查看使用帮助。")
    finally:
        updater.start_polling()