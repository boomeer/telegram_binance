import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import os
import binance
from binance.websockets import BinanceSocketManager
from binance.client import Client
from binance.depthcache import DepthCacheManager
from binance.client import Client
import dropbox
import time
import json
import datetime

PORT = int(os.environ.get('PORT', 5000))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TOKEN = os.environ.get('TELEGRAM_TOKEN', None)

dropboxToken = ''

def start(update, context):
    update.message.reply_text('Hi!')

def loadJsonFromDropbox(dbx):
	meta, resp = dbx.files_download('/totalData.txt')
	body = resp.content.decode('utf-8')
	resp.close()
	return json.loads(body)

def getHistory():
	dbx = dropbox.Dropbox(dropboxToken)
	prices = loadJsonFromDropbox(dbx)

	timeNow = time.time()
	dtNow = datetime.datetime.now()
	dtToday = dtNow.replace(hour=0, minute=0, second=1)
	dtWeek = dtToday - datetime.timedelta(days=dtToday.weekday())
	dtAllTime = dtNow - datetime.timedelta(days=100000)

	stats = {
		'this week': {
			'since': dtWeek.timestamp(),
			'till': dtNow.timestamp(),
			'prices': []
		},
		'all time': {
			'since': dtAllTime.timestamp(),
			'till': dtNow.timestamp(),
			'prices': []
		}
	}

	for item in prices:
		for stat in stats:
			if stats[stat]['since'] < item['ts'] < stats[stat]['till']:
				stats[stat]['prices'].append(item)

	text = ''
	totalBalance = 0.
	totalBalanceUsd = 0.
	for stat in stats:
		usdt = [p['usd'] for p in stats[stat]['prices']]

		if len(usdt) >= 1:
			u1 = usdt[-1]
			u2 = usdt[0]
			valueUsd = '{:+.2f} USD'.format(u1 - u2)
		else:
			value = 'n/a'
			valueBtc = 'n/a'
			valueUsd = 'n/a'
			fxRate = 'n/a'
		text += '{}: {}\n'.format(stat, valueUsd)
		if stat == 'all time':
			totalBalanceUsd = u1
				
	dt = datetime.datetime.fromtimestamp(prices[-1]['ts'])
	text += '\nLast update: {:%A %H:%M:%S} UTC+0\n'.format(dt)

	return update.message.reply_text(text, parse_mode='markdown')

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stats", getHistory))

    dp.add_handler(MessageHandler(Filters.text, echo))

    dp.add_error_handler(error)

    updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
    print(TOKEN + ' <- TOKEN | ' + str(PORT) + ' <- PORT')
    updater.bot.setWebhook('https://ваш_хероку_апп.com/' + TOKEN)

    updater.idle()

if __name__ == '__main__':
    main()
