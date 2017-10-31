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

def handle_command(command, channel):
	if command == None:
		return
	if command.lower().startswith('market price'):
		r = requests.get('https://api.korbit.co.kr/v1/ticker/detailed')
		price_str = '비트코인 가격은 현재 {} 원 입니다. '.format(r['last'])
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
