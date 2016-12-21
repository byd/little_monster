#coding=utf8

import itchat
from itchat.content import *
import threading
import time
import os
import pprint
import ConfigParser
import random
import codecs
import re
import json
import sys
import requests
import json

reload(sys)
sys.setdefaultencoding("utf8")

CONF_FILE_TIMESTAMP = 0
CONF_FILE = 'auto_reply.conf'
conf = ConfigParser.ConfigParser()
BotChat = False
botOnCmd = re.compile(u".*((聊天)|(出来)|(陪我)|(来嘛)|(hello)).*")
botOffCmd = re.compile(u".*((走开)|(退下)|(去吧)|(睡觉去)|(回家)).*")
UandMe = [u'@73a8e09619df8c771ea8f3a5fc58e92a',u'@b3e34a494ed851f538cbc38f8ba2354e']

def turing_reply(msg, user):
	turing_api = 'http://www.tuling123.com/openapi/api'
	params = {
		'key': 'bc57e924d89e4e2c92dc3efcc5530eb9',
		'info': msg, 'userid':user
	}
	r = requests.post(turing_api, params = params)
	res = ''
	if len(r.text) > 0:
		try:
			resp = json.loads(r.text)
			if resp['code'] == 100000:
				res = resp['text']
			elif resp['code'] == 200000:
				res = u'%s\n%s' % (resp['text'], resp['url'])
			elif resp['code'] == 302000:
				res = resp['text'] + "\n" + "\n\n".join(map(lambda x:x['article']+'\n'+x['source']+'\n'+x['detailurl'], resp['list']))
			elif resp['code'] == 308000:
				res = resp['text'] + "\n" + "\n\n".join(map(lambda x:x['info']+'\n'+x['detailurl'], resp['list']))
			else:
				res = '出了点问题，小怪兽要回家(%d)' % resp['code']
		except Exception:
			pass
	return res

def group_tweet(msg, kwd=None):
	global CONF_FILE_TIMESTAMP
	mtime = os.stat(CONF_FILE).st_mtime
	if mtime > CONF_FILE_TIMESTAMP:
		#conf.read(CONF_FILE)
		conf.readfp(codecs.open(CONF_FILE, 'r', 'utf8'))
		CONF_FILE_TIMESTAMP = mtime
	if kwd:
		replies = conf.get('group_tweet', kwd)
		return random.choice(replies.split('<#>'))
	tweet_keywords = conf.options('group_tweet')
	for kwd in tweet_keywords:
		if kwd in msg:
			replies = conf.get('group_tweet', kwd)
			return random.choice(replies.split('<#>'))
	return ''

@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
	bot_reply = turing_reply(msg['Content'], msg['FromUserName'])
	try:
		itchat.send(bot_reply, msg['FromUserName'])
	except Exception,e:
		print e


@itchat.msg_register(TEXT, isGroupChat=True)
def text_reply(msg):
	global BotChat, UandMe
	if msg['ActualUserName'] in UandMe:
		reply = group_tweet(msg['Content'])
		if len(reply) > 0:
			try:
				itchat.send(reply, msg['FromUserName'])
			except Exception,e:
				print e

	bot_reply = ''
	if msg['isAt']:
		content = msg['Content'].replace(u"小怪兽","")
		if botOnCmd.match(content):
			BotChat = True
		if botOffCmd.match(content):
			BotChat = False
			bot_reply = group_tweet('', u'退出')
		if len(bot_reply) < 1:
			bot_reply = turing_reply(content, msg['ActualUserName'])
	if BotChat:
		bot_reply = turing_reply(msg['Content'], msg['ActualUserName'])	
	if len(bot_reply)>0:
		try:
			itchat.send(bot_reply, msg['FromUserName'])
		except Exception,e:
			print e

'''
itchat.auto_login(enableCmdQR=2, hotReload=True)
itchat.run()
'''

itchat.auto_login(enableCmdQR=1, hotReload=True)
t = threading.Thread(target=itchat.run)
t.start()

while True:
	time.sleep(random.random() * 60 * 30)
	try:
		itchat.send("heart beat %d" % time.time(), u'filehelper')
	except Exception,e:
		print e
	

