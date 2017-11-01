# -*- coding: utf-8 -*-

import os
import time
import requests

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
select_dic1 = {u'비트코인캐시':'bch_krw', 'bitcoincash':'bch_krw', u'이더리움클래식':'etc_krw', 'etheriumclassic':'etc_krw', u'리플':'xrp_krw','ripple':'xrp_krw'}
select_dic2 = {u'비트코인캐시':'bch_krw', 'bitcoincash':'bch_krw', u'비트코인':'btc_krw', 'bitcoin':'btc_krw', u'이더리움클래식':'etc_krw', 'etheriumclassic':'etc_krw', u'이더리움': 'eth_krw', 'etherium':'eth_krw', u'리플':'xrp_krw','ripple':'xrp_krw'}

def contain(str, mandatory):
	for value in mandatory:
		if str.find(value) > -1:
			return True
	return False

def get_coin_info(refined_cmd, dic1, dic2):
	for key, value in dic1.iteritems():
		if refined_cmd.find(key) > -1:
			return value, key
	for key, value in dic2.iteritems():
		if refined_cmd.find(key) > -1:
			return value, key
	
	return None, None


def handle_command(command, channel):
	if command == None:
		return
	
	refined_cmd = command.lower().replace(' ', '')

	if contain(refined_cmd, mandatory):
		coin_key, coin_name = get_coin_info(refined_cmd, select_dic1, select_dic2)

		if coin_key == None:
			slack_client.api_call('chat.postMessage', text = u'코인 이름을 말씀해주세요(예. 비트코인 가격 얼마야? 이더리움 시세 알려줘.)', channel=channel, as_user=True)
			return

		url = 'https://api.korbit.co.kr/v1/ticker/detailed?currency_pair={}'.format(coin_key)
		res = requests.get(url)
		obj = res.json()
		price_str = u'코빗 기준, {} 가격은 현재 {} 원 입니다. '.format(coin_name, obj['last'])
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
