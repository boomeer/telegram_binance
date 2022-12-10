import json
import time
import logging
import os
import binance
import dropbox
from binance.client import Client

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

binanceKey = ['XXX']
binanceSecret = ['YYY']

dropboxToken = 'ZZZ'

SLEEP_TIMEOUT = 1 * 60

def getBalance(idx):
    client = Client(binanceKey[idx], binanceSecret[idx])
    balances = client.get_account()['balances']
    balanceUsd = 0
    prices = client.get_all_tickers()
    for b in balances:
        curB = float(b['free']) + float(b['locked'])
        asset = b['asset']
        if curB < 0.000001:
            continue
        if asset == "USDT":
            balanceUsd += curB
        prices = sorted(prices, key=lambda p: p['symbol'])
        for p in prices:
            if p['symbol'] == str(asset) + "USDT":
                balanceUsd += float(curB) * float(p['price'])
    balanceUsd = float("%.2f" % balanceUsd)
    curt = time.time()
    return balanceUsd, curt

def getAccountInfo():
        amountUsd, timenow = getBalance(0)
        return {'usd': amountUsd, 'ts': timenow}

def loadJsonFromDropbox(dbx):
    for i in range(1):
        try:
            meta, resp = dbx.files_download('/totalData.txt')
            print(meta, resp)
            body = resp.content.decode('utf-8')
            resp.close()
            return json.loads(body)
        except Exception as ex:
            time.sleep(0.5 * (2 ** i))
            print(ex)

def saveJsonToDropbox(dbx, content):
    jsonBytes = json.dumps(content, indent=4).encode('utf-8')
    dbx.files_upload(jsonBytes, '/totalData.txt', mode=dropbox.files.WriteMode('overwrite'))

def addInfoPointToDropbox(dbx):
        content = loadJsonFromDropbox(dbx)
        content += [getAccountInfo()]
        saveJsonToDropbox(dbx, content)

def main():
    dbx = dropbox.Dropbox(dropboxToken)
    while True:
        addInfoPointToDropbox(dbx)
        time.sleep(SLEEP_TIMEOUT)

if __name__ == '__main__':
	main()