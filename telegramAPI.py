#!/usr/bin/python3

import requests, json

TOKEN = None
URL = None
PUBLIC_KEY = '/etc/lighttpd/certs/public.pem'
WEBHOOK_URL = None

class Method:
  def __init__(self, name):
    self.name = name

  def invoke(self):
    self.r = requests.post(URL + '/' + self.name)

  def dump(self):
    print(self.r.text)

class GetMe(Method):
  def __init__(self):
    Method.__init__(self, 'getMe')

class DeleteWebhook(Method):
  def __init__(self):
    Method.__init__(self, 'deleteWebhook')

class GetWebhookInfo(Method):
  def __init__(self):
    Method.__init__(self, 'getWebhookInfo')

class SetWebhook(Method):
  def __init__(self):
    Method.__init__(self, 'setWebhook')
  def invoke(self):
    data = {'url':WEBHOOK_URL}
    files = {'certificate': open(PUBLIC_KEY, 'rb')}
    self.r = requests.post(URL + '/' + self.name, data=data, files=files)

class SendMessage(Method):
  def __init__(self, chatid, text):
    Method.__init__(self, 'sendMessage')
    self.chatid = chatid
    self.text = text
  def invoke(self):
    data = {'chat_id':self.chatid, 'text': self.text}
    self.r = requests.post(URL + "/" + self.name, data=data)

#deleteWH = DeleteWebhook()
#deleteWH.invoke()
#deleteWH.dump()

#setWH = SetWebhook()
#setWH.invoke()
#setWH.dump()

#infoWH = GetWebhookInfo()
#infoWH.invoke()
#infoWH.dump()

class Chat:
  def __init__(self, data):
    self._id = data['id']

class User:
  def __init__(self, data):
    self._id = data['id']
    self._is_bot = data['is_bot']
    self._first_name = data['first_name']
    self._last_name = None
    self._username = None
    self._language_code = None
    if 'last_name' in data:
      self._last_name = data['last_name']
    if 'username' in data:
      self._username = data['username']
    if 'language_code' in data:
      self._language_code = data['language_code']

class Message:
  def __init__(self, data):
    self._id = data['message_id']
    self._text = None
    self._from = None
    self._chat = None
    if 'text' in data:
      self._text = data['text']

    if 'chat' in data:
      self._chat = Chat(data['chat'])

    if 'from' in data:
      self._from = User(data['from'])

class Update:
  def __init__(self, jsondata):
    self._parsed_ok = False
    self._update_id = -1
    self._message = None
    try:
      self._json = json.loads(jsondata)
      self._update_id = self._json['update_id']
      # Message
      if 'message' in self._json:
        self._message = Message(self._json['message'])
        self._parsed_ok = True
    except:
      self._parsed_ok = False
