import argparse
import telethon
from telethon.sync import TelegramClient
import colorama
from colorama import *
from telethon.tl.types import *
from telethon import *
import re
import yaml
import json
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.errors.rpcerrorlist import *

parser = argparse.ArgumentParser()
parser.add_argument('link', action='store', type=str, help='link to a Telegram channel (without t.me)')
parser.add_argument('--keywords', action='store', type=str, help='file with keywords, each keyword has to be on a new line')
parser.add_argument('--results', action='store', type=str, help='file to write results to')
parser.add_argument('--limit', action='store', type=int, help='how many posts should be checked, max')
args = parser.parse_args()
colorama.init()

with open("config.yaml") as config_file:
	config = yaml.safe_load(config_file.read())

with open(args.keywords) as keywords_file:
	keywords = [line[:-1] for line in keywords_file]

client = TelegramClient(config["number"], config["api_id"], config["api_hash"])
client.connect()
if(not client.is_user_authorized()):
	client.send_code_request(config["number"])
	print("Enter code:")
	code = input('>')
	client.sign_in(client._phone, code)
	print(Fore.GREEN+"Logged in."+Fore.RESET)

channelname = args.link
channel = client.get_entity(channelname)

posts = client(GetHistoryRequest(
    peer=channel,
    limit=args.limit,
    offset_date=None,
    offset_id=0,
    max_id=0,
    min_id=0,
    add_offset=0,
    hash=0))

with open(args.results, 'w') as results_file: 
	results_file.write("sep=;\n")
	for post in posts.messages:
		try:
			for comment in client.iter_messages(channel, reply_to=post.id):
				print(comment.text)
				for keyword in keywords:
					if(len(keyword)<=1):
						continue
					if(keyword in comment.text):
						link = f"https://t.me/{channelname}/{post.id}?comment={comment.id}"
						text = comment.text.replace('\n','')
						results_file.write(f"{keyword};{text};{link}\n")
		except MsgIdInvalidError:
			continue
