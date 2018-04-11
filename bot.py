import sys, os, json, logging, telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

json_str = os.popen("cat ~/.secrets/key.json").read()
json_dict=json.loads(json_str)
mytoken=json_dict['telegram_bot']['token']

xiaobo_url="/tmp/mojo_webqq_qrcode_default.png"

updater = Updater(token=mytoken)
dispatcher = updater.dispatcher

def qq(bot, update):
    logging.info(str(update.message.chat_id) + " send /qq")
    try:
        xiaobo_qr = open(xiaobo_url, 'rb')
        bot.send_photo(chat_id=update.message.chat_id, photo=xiaobo_qr)
        xiaobo_qr.close()
    except:
        logging.warning(str(update.message.chat_id) + " xiaobo_url does not exist")
    bot.send_message(chat_id=update.message.chat_id, text="小波扫描二维码")

def xb(bot, update):
	logging.info(str(update.message.chat_id) + " send /xb")
    os.system('kill -9 `ps ax | grep [x]iaobo | sed \'s/^\s*//\' | cut -d " " -f 1` && sleep 5')
    os.system('tmux new-window -n xiaobo "cd /home/zhiyue.wang/workspaces/xiaoboQQBot/src && python xiaobo.py"')
    bot.send_message(chat_id=update.message.chat_id, text="小波已重启！")

def cc(bot, update):
	logging.info(str(update.message.chat_id) + " send /cc")
    os.system('rm /home/zhiyue.wang/workspaces/xiaoboQQBot/src/cookie/*')
    os.system('rm /home/zhiyue.wang/workspaces/xiaoboQQBot/src/smart_qq_bot/__pycache__/*')
    os.system('rm /home/zhiyue.wang/workspaces/xiaoboQQBot/src/smart_qq_plugins/__pycache__/*')
    bot.send_message(chat_id=update.message.chat_id, text="小波的缓存已清除！")

def ss(bot, update):
	logging.info(str(update.message.chat_id) + " send /ss")
    os.system('sudo kill -9 `ps ax | grep [s]sserver | sed \'s/^\s*//\' | cut -d " " -f 1` && sleep 5')
    os.system('tmux new-window -n shadowsocks "sudo -i ssserver -c /etc/shadowsocks.json"')
    bot.send_message(chat_id=update.message.chat_id, text="已经开始科学冲浪！\n107.167.188.187:7711\naes-256-cfb")

def ks(bot, update):
	logging.info(str(update.message.chat_id) + " send /killss")
    os.system('sudo kill -9 `ps ax | grep [s]sserver | sed \'s/^\s*//\' | cut -d " " -f 1`')
    bot.send_message(chat_id=update.message.chat_id, text="停止科学冲浪！")

def show_help(bot, update):
	logging.info(str(update.message.chat_id) + " " + update.message.text)
    bot.send_message(chat_id=update.message.chat_id, text="命令一览：\n/qq 发送QQ号小波的二维码\nXB 重启小波\n[慎用]CC 清除小波的缓存\nSS 科学冲浪\nKILLSS 普通冲浪")

qq_handler = CommandHandler('qq', qq)
xb_handler = CommandHandler('xb', xb)
cc_handler = CommandHandler('cc', cc)
ss_handler = CommandHandler('ss', ss)
ks_handler = CommandHandler('killss', ks)
help_handler = MessageHandler(Filters.text, show_help)

dispatcher.add_handler(qq_handler)
dispatcher.add_handler(xb_handler)
dispatcher.add_handler(cc_handler)
dispatcher.add_handler(ss_handler)
dispatcher.add_handler(ks_handler)
dispatcher.add_handler(help_handler)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
updater.start_polling()
