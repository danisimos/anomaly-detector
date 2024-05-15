import telebot
from apscheduler.schedulers.background import BackgroundScheduler

from app import get_prometheus_metrics
from app.utils import check_anomaly_now
from config import get_config

cfg = get_config()
bot = telebot.TeleBot(cfg.TELEGRAM_API_KEY)

def sensor():
    with open('chats.txt') as file:
        lines = file.readlines()

        for line in lines:

            params = line.split()
            chat_id = params[0]
            timeframe = params[1]
            anomaly_model = params[2]
            prometheus_url = params[3]

            is_anomaly = check_anomaly_now(timeframe, anomaly_model, prometheus_url)



            if is_anomaly['cpu']:
                bot.send_message(chat_id, f'Detected CPU Anomaly with {anomaly_model} model in {timeframe} timeframe')

            if is_anomaly['memory']:
                bot.send_message(chat_id, f'Detected RAM Anomaly with {anomaly_model} model in {timeframe} timeframe')


schedule = BackgroundScheduler(daemon=True)
schedule.add_job(sensor, 'interval', minutes=3)
schedule.start()

@bot.message_handler(commands=['start'])
def send_welcome(message):

    bot.send_message(message.chat.id, 'Success')
    with open('chats.txt', 'a') as f:
        f.write(str(message.chat.id) + ' ' + message.text.split()[1] + ' ' + message.text.split()[2] + ' ' + message.text.split()[3])



def main():
    bot.polling(none_stop=True)

