import sys, os, time, json, logging, telegram, threading, datetime, requests
from time import sleep
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

json_str = os.popen("cat ~/.secrets/key.json").read()
json_dict=json.loads(json_str)
mytoken=json_dict['telegram_bot']['token']
userid =json_dict['telegram_bot']['userid']
sudopw =json_dict['telegram_bot']['sudopw']

xiaobo_url="/tmp/mojo_webqq_qrcode_default.png"
yue_url="/home/zhiyue.wang/src/qr_yue.jpg"

price_threshold = 1.0

updater = Updater(token=mytoken)
dispatcher = updater.dispatcher

def qq(bot, update):
    logging.info(str(update.message.chat_id) + " send /qq")
    global userid
    if str(userid) != str(update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="请先使用/sudo取得系统权限！")
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

def xb(bot, update):
    logging.info(str(update.message.chat_id) + " send /xb")
    global userid
    if str(userid) != str(update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="请先使用/sudo取得系统权限！")
    else:
        os.system('kill -9 `ps ax | grep [x]iaobo | sed \'s/^\s*//\' | cut -d " " -f 1` && sleep 5')
        os.system('tmux new-window -n xiaobo "cd /home/zhiyue.wang/workspaces/xiaoboQQBot/src && python xiaobo.py"')
        bot.send_message(chat_id=update.message.chat_id, text="小波已重启！")

def qr(bot, update):
    logging.info(str(update.message.chat_id) + " send /qq")
    global userid
    if str(userid) != str(update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="请先使用/sudo取得系统权限！")
    else:
        try:
            os.system('rm ' + yue_url)
            os.system('tmux new-window -n yue "python /home/zhiyue.wang/workspaces/wechat_yue/yue.py remote"')
            sleep(3)
            yue_qr = open(yue_url, 'rb')
            bot.send_photo(chat_id=update.message.chat_id, photo=yue_qr)
            yue_qr.close()
        except:
            logging.warning(str(update.message.chat_id) + " yue_url does not exist")
            bot.send_message(chat_id=update.message.chat_id, text="没有二维码文件，请重新运行/qr")
        else:
            bot.send_message(chat_id=update.message.chat_id, text="微信Yue扫描二维码")

def cc(bot, update):
    logging.info(str(update.message.chat_id) + " send /cc")
    global userid
    if str(userid) != str(update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="请先使用/sudo取得系统权限！")
    else:
        os.system('rm /home/zhiyue.wang/workspaces/xiaoboQQBot/src/cookie/*')
        os.system('rm /home/zhiyue.wang/workspaces/xiaoboQQBot/src/smart_qq_bot/__pycache__/*')
        os.system('rm /home/zhiyue.wang/workspaces/xiaoboQQBot/src/smart_qq_plugins/__pycache__/*')
        bot.send_message(chat_id=update.message.chat_id, text="小波的缓存已清除！")

def ss(bot, update):
    logging.info(str(update.message.chat_id) + " send /ss")
    global userid
    if str(userid) != str(update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="请先使用/sudo取得系统权限！")
    else:
        os.system('sudo kill -9 `ps ax | grep [s]sserver | sed \'s/^\s*//\' | cut -d " " -f 1` && sleep 5')
        os.system('tmux new-window -n shadowsocks "sudo -i ssserver -c /etc/shadowsocks.json"')
        bot.send_message(chat_id=update.message.chat_id, text="已经开始科学冲浪！\n107.167.188.187:7711\naes-256-cfb")

def ks(bot, update):
    logging.info(str(update.message.chat_id) + " send /killss")
    global userid
    if str(userid) != str(update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="请先使用/sudo取得系统权限！")
    else:
        os.system('sudo kill -9 `ps ax | grep [s]sserver | sed \'s/^\s*//\' | cut -d " " -f 1`')
        bot.send_message(chat_id=update.message.chat_id, text="停止科学冲浪！")

def sudo(bot, update, args):
    logging.info(str(update.message.chat_id) + " send /sudo " + ' '.join(args))
    global userid
    if len(args) > 0 and args[0] == sudopw:
        bot.send_message(chat_id=userid, text="用户"+str(update.message.chat_id)+"已经获取系统通知权限！")
        userid = update.message.chat_id
        bot.send_message(chat_id=update.message.chat_id, text="已经获取系统通知权限！")
    else:
        bot.send_message(chat_id=userid, text="用户"+str(update.message.chat_id)+"尝试获取系统通知权限失败！" + ' '.join(args))
        bot.send_message(chat_id=update.message.chat_id, text="密码错误，无法系统通知权限！")

def tr(bot, update, args):
    logging.info(str(update.message.chat_id) + " send /tr " + ' '.join(args))
    global userid, price_threshold
    if str(userid) != str(update.message.chat_id):
        bot.send_message(chat_id=update.message.chat_id, text="请先使用/sudo取得系统权限！")
    else:
        if len(args) == 0:
            bot.send_message(chat_id=update.message.chat_id, text="当前阈值: "+str(price_threshold)+"%")
        else:
            try:
                float(args[0])
            except:
                bot.send_message(chat_id=update.message.chat_id, text="参数错误，无法更改参数阈值！")
            else:
                if float(args[0]) >= 0:
                    price_threshold = float(args[0])
                    bot.send_message(chat_id=update.message.chat_id, text="已经更改通知阈值！")
                else:
                    bot.send_message(chat_id=update.message.chat_id, text="阈值参数不能为负数！")

def show_help(bot, update):
    logging.info(str(update.message.chat_id) + " " + update.message.text)
    bot.send_message(chat_id=update.message.chat_id, text="命令一览：\n/qq - 发送小波的二维码\n/xb - 重启小波\n/qq - 发送Yue的二维码\n/ss - 科学冲浪\n/killss - 普通冲浪\n/sudo - 切换系统提示通知对象\n/tr - 查询或修改通知阈值\ncc - [慎用]清除小波的缓存")

#virtual currency bot
class myThread1(threading.Thread):
    def __init__(self):
        super(myThread1, self).__init__()

    def run(self):
        currency_num = 20
        currency_type = ['BTC', 'ETH', 'BCH', 'XEM']
        price_old = {}
        price_new = {}
        coin_data = {}
        while True:
            global price_threshold
            r = requests.get("https://api.coinmarketcap.com/v1/ticker/?convert=jpy")

            for n in range(currency_num):
                coin_data[r.json()[n]['symbol']] = r.json()[n]

            for i in currency_type:
                price_new[i] = float(coin_data[i]['price_jpy'])
                if i not in price_old:
                    price_old[i] = price_new[i]
                rate = (price_new[i] - price_old[i]) / price_old[i] * 100
                if rate > price_threshold:
                    price_status='醒一醒，'+coin_data[i]['symbol']+'拉盘了！过去5分内+'+str(round(rate,2))+'%，现在价格'+str("{:,.1f}".format(price_new[i]))+'円'
                    bot.send_message(chat_id=userid, text=price_status)
                elif rate < -price_threshold:
                    price_status='醒一醒，'+coin_data[i]['symbol']+'崩盘了！过去5分内'+str(round(rate,2))+'%，现在价格'+str("{:,.1f}".format(price_new[i]))+'円'
                    bot.send_message(chat_id=userid, text=price_status)
                price_old[i] = price_new[i]
            sleep(300)

#qq online monitoring bot
class myThread2(threading.Thread):
    def __init__(self):
        super(myThread2, self).__init__()

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
    qq_handler = CommandHandler('qq', qq)
    xb_handler = CommandHandler('xb', xb)
    qr_handler = CommandHandler('qr', qr)
    cc_handler = CommandHandler('cc', cc)
    ss_handler = CommandHandler('ss', ss)
    ks_handler = CommandHandler('killss', ks)
    sudo_handler = CommandHandler('sudo', sudo, pass_args=True)
    tr_handler = CommandHandler('tr', tr, pass_args=True)
    help_handler = MessageHandler(Filters.text, show_help)

    dispatcher.add_handler(qq_handler)
    dispatcher.add_handler(xb_handler)
    dispatcher.add_handler(qr_handler)
    dispatcher.add_handler(cc_handler)
    dispatcher.add_handler(ss_handler)
    dispatcher.add_handler(ks_handler)
    dispatcher.add_handler(sudo_handler)
    dispatcher.add_handler(tr_handler)
    dispatcher.add_handler(help_handler)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
    bot = telegram.Bot(token=mytoken)
    try:
        th1 = myThread1()
        th1.start()
        th2 = myThread2()
        th2.start()
    except:
        logging.warning("无法启动小波监视器！")
        bot.send_message(chat_id=userid, text="无法启动小波监视器！")
    else:
        logging.info("小波监视器已启动。将启动Telegram bot。")
        bot.send_message(chat_id=userid, text="小波监视器已启动。将启动Telegram bot。")
    finally:
        updater.start_polling()