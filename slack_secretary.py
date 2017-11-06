# -*- coding: utf-8 -*-

import os
import time
import requests
import re

from slackclient import SlackClient

SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
slack_client = SlackClient(SLACK_BOT_TOKEN)
BOT_NAME = os.environ.get('SLACK_BOT_NAME')
print BOT_NAME
print SLACK_BOT_TOKEN

def get_bot_id():
	api_call = slack_client.api_call('users.list')
	if 'ok' in api_call:
		if api_call['ok'] == True:
			users = api_call['members']
			for user in users:
				if user['name'] == BOT_NAME:
					return user['id']
	print 'log: wrong id'
	return '<wrong_id>'

def parse_command(read_obj, prefix):
	output_list = read_obj
	if output_list and len(output_list) > 0:
		for output in output_list:
			if 'text' in output and prefix in output['text']:
				return output['text'].split(prefix)[1].strip(), output['channel']

	return None, None

mandatory = [u'시세', u'가격', u'얼마', 'price', 'value']
bos_dic = { u'보스':'bos/btc/', 'bos':'bos/btc/' }
url_dic = { 'to_btc':'https://api.coinhills.com/v1/cspa/{}', 'to_krw':'https://api.korbit.co.kr/v1/ticker/detailed?currency_pair={}' }
select_dic1 = { u'비트코인캐시':'bch_krw', 'bitcoincash':'bch_krw', u'이더리움클래식':'etc_krw', 'etheriumclassic':'etc_krw', u'리플':'xrp_krw','ripple':'xrp_krw' }
select_dic2 = { u'비트코인':'btc_krw', 'bitcoin':'btc_krw', u'이더리움': 'eth_krw', 'etherium':'eth_krw' }

def contain(str, mandatory):
	for value in mandatory:
		if str.find(value) > -1:
			return True
	return False

def get_url(refined_cmd):
        for key, value in bos_dic.iteritems():
                if refined_cmd.find(key) > -1:
                        return key, url_dic['to_btc'].format(value)
	for key, value in select_dic1.iteritems():
		if refined_cmd.find(key) > -1:
                        return key, url_dic['to_krw'].format(value)
	for key, value in select_dic2.iteritems():
		if refined_cmd.find(key) > -1:
                        return key, url_dic['to_krw'].format(value)

	return None, None

def get_btc_to_krw():
    res = requests.get(url_dic['to_krw'].format(select_dic2['bitcoin']))
    obj = res.json()
    price = obj['last']
    return price

def handle_command(command, channel):
	if command == None:
		return

	refined_cmd = command.lower().replace(' ', '')

	if contain(refined_cmd, mandatory):
		coin_name, url = get_url(refined_cmd)

		if url == None:
                    slack_client.api_call('chat.postMessage', text = u'코인 이름을 말씀해주세요( 예. 보스코인 가격 얼마야? 비트코인 시세 알려줘:) )', channel=channel, as_user=True)
		    return

                obj = requests.get(url).json()

                #p = re.compile('([0-9,]+)\w+' + coin_name)
                #m = p.match(refined_cmd)
                #count = 1
                #if m:
                #    print m.group(1)
                #    count = int(m.group(1))

                if coin_name == u'보스' or coin_name == 'bos':
                    btc2krw = get_btc_to_krw()
                    bos2btc = obj["data"]["CSPA:BOS/BTC"]["cspa"]
                    bos2krw = float(btc2krw) * float(bos2btc)
                    price_str = u'HitBTC 기준, {} {} 가격은 현재 {} 원, {} BTC 입니다. '.format('1', 'BOS', str(bos2krw), bos2btc)
		    slack_client.api_call('chat.postMessage', text = price_str, channel=channel, as_user=True)
                else:
		    price_str = u'코빗 기준, {} {} 가격은 현재 {} 원 입니다. '.format('1', coin_name, obj['last'])
		    slack_client.api_call('chat.postMessage', text = price_str, channel=channel, as_user=True)
	else:
		slack_client.api_call('chat.postMessage', text = command, channel=channel, as_user=True)

if __name__ == '__main__':
	prefix = "<@" + get_bot_id() + ">"
	if slack_client.rtm_connect():
		print 'log: connected!'
		while(True):
			command, channel = parse_command(slack_client.rtm_read(), prefix)
			handle_command(command, channel)
			time.sleep(1)
	else:
		print 'log: connection fail!'
