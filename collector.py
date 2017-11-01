import sys
from getpass import getpass
from time import sleep

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.errors.rpc_errors_400 import UsernameNotOccupiedError
from telethon.errors.rpc_errors_420 import FloodWaitError
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.tl.types import ChannelParticipantsSearch, InputChannel

# First you need create app on https://my.telegram.org
api_id = 0
api_hash = ''
phone = ''
limit = 100


def get_chat_info(username, client):
	try:
		chat = client(ResolveUsernameRequest(username))
	except UsernameNotOccupiedError:
		print('Chat/channel not found!')
		sys.exit()
	result = {
		'chat_id': chat.peer.channel_id,
		'access_hash': chat.chats[0].access_hash
	}
	return result


def dump_users(chat, client):
	counter = 0
	offset = 0
	chat_object = InputChannel(chat['chat_id'], chat['access_hash'])
	all_participants = []
	print('Process...')
	while True:
		participants = client.invoke(GetParticipantsRequest(
                    chat_object, ChannelParticipantsSearch(''), offset, limit
                ))
		if not participants.users:
			break
		all_participants.extend(['{} {}'.format(x.id, x.username)
                           for x in participants.users])
		users_count = len(participants.users)
		offset += users_count
		counter += users_count
		print('{} users collected'.format(counter))
		sleep(2)
	with open('users.txt', 'w') as file:
		file.write('\n'.join(map(str, all_participants)))


def main():
	channel_name = input('Input a channel name, without "@": ')
	client = TelegramClient('current-session', api_id, api_hash)
	print('Connecting...')
	client.connect()
	if not client.is_user_authorized():
		try:
			client.send_code_request(phone)
			print('Sending a code...')
			client.sign_in(phone, code=input('Enter code: '))
			print('Successfully!')
		except FloodWaitError as FloodError:
			print('Flood wait: {}.'.format(FloodError))
			sys.exit()
		except SessionPasswordNeededError:
			client.sign_in(password=getpass('Enter password: '))
			print('Successfully!')
	dump_users(get_chat_info(channel_name, client), client)
	print('Done!')

if __name__ == '__main__':
	main()
