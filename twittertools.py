from jambot import botModule
import sys
import twitter
from threading import Timer
from twitter import *
import time
import random
#Twittertools module
#self.send(e.target, msg)

class bcolors:
	TIME = '\x0310'
	NAME = '\x032'
	HANDLE = '\x033'
	MENTION = '\x033'
	MSG = '\x0f'
	EXTRAS = '\x0313'
	HASHTAG = '\x038'
	ENDC = '\x0f'

class moduleClass(botModule):
	def on_start(self):
		self.channels = []
		self.last_update = 0
		self.lastsentence = {}
		self.tweettimer = time.time()
		self.checktimer = int(self.settings["check_timer"])
		self.consumer_key= self.settings["consumer_key"]
		self.consumer_secret = self.settings["consumer_secret"]
		self.access_token = self.settings["access_token"]
		self.access_secret = self.settings["access_secret"]
		if self.checktimer > 0:
			self.twitter_schedule(self.checktimer)
		try:
			t = Twitter(auth=OAuth(self.access_token, self.access_secret,self.consumer_key, self.consumer_secret))
			timeline = t.statuses.home_timeline()
			self.last_update = timeline[0]['id']
		except:
			print("couldn't initiate twitter feed")
			for error in sys.exc_info():
				print(str(error))


	def check_twitter(self):
		try:
			t = Twitter(auth=OAuth(self.access_token, self.access_secret,self.consumer_key, self.consumer_secret))
			timeline = t.statuses.home_timeline()
			tweets = []
			for tweet in timeline:
				if (int(tweet['id']) == self.last_update) or (tweet['user']['screen_name'] == self.settings["account_name"]):
					break
				tweet_name = tweet['user']['name']
				tweet_handle = tweet['user']['screen_name']
				tweet_text_pre = tweet['text'].split()
				tweet_text = ""
				for line in tweet_text_pre:
					if line[0] == "@":
						if line == ("@" + tweet_handle):
							line = bcolors.HANDLE + line + bcolors.MSG
						else:
							line = bcolors.MENTION + line + bcolors.MSG
					elif (line[0] == ".") and (len(line) > 1):
						if line[1] == "@":
							if line == (".@" + tweet_handle):
								line = bcolors.HANDLE + line + bcolors.MSG
							else:
								line = bcolors.MENTION + line + bcolors.MSG
					elif line[0] == "#":
						line = bcolors.HASHTAG + line + bcolors.MSG
					tweet_text += line + " "
				tweet_link = ""
				if "urls" in tweet["entities"]:
					for url in tweet["entities"]["urls"]:
						tweet_link += url["display_url"] + " "
				tweet_extras = ""
				if 'media' in tweet['entities']:
					for media in tweet['entities']['media']:
						tweet_extras += "[" + media['type']+ "]"
				tweet_string = bcolors.NAME + tweet_name + bcolors.HANDLE + " @" + tweet_handle + ": " + bcolors.MSG + tweet_text + " " + bcolors.EXTRAS + tweet_extras + bcolors.MSG + tweet_link + bcolors.ENDC
				tweets.append(tweet_string)
			for tweet in reversed(tweets):
				for channel in self.channels:
					self.send(channel, tweet)
			self.last_update = int(timeline[0]['id'])
		except TwitterHTTPError:
			pass
		except:
			for error in sys.exc_info():
				print(str(error))
			print("Error fetching tweets")

	def twitter_schedule(self, checktimer):
		timer = Timer(checktimer, self.twitter_execute, ())
		timer.setDaemon(True)
		timer.start()

	def twitter_execute(self):
		self.check_twitter()
		self.twitter_schedule(self.checktimer)

	def on_pubmsg(self, c, e):
		pass
	def on_send(self, chan, msg, modulename):
		if modulename != "twittertools":
			self.lastsentence[chan]=msg
		try:
			if ((len(msg.split()) >= int(self.settings["tweet_length"])) and (time.time() > self.tweettimer) and (self.settings["auto_tweeting"] == "True") and (self.settings["tweeting"] == "True") and (e.target in self.settings["tweet_modules"].split())):
				t = Twitter(auth=OAuth(self.access_token, self.access_secret,self.consumer_key, self.consumer_secret))
				t.statuses.update(status=msg)
				self.send(chan, "*")
				self.tweettimer = time.time() + random.randint(int(self.settings["tweetdelay_lower"]), int(self.settings["tweetdelay_upper"]))
		except:
			for error in sys.exc_info():
				print(str(error))
			print("Error tweeting")
			raise
	def on_event(self, c, e):
		if e.source.split("!")[0]==c.nickname:
			if e.type=="join":
				self.channels.append(e.target)
			elif e.type=="part":
				self.channels.remove(e.target)
	def do_command(self, c, e, command, args, admin):
		msg = ""
		if ((command == "tweet") and admin):
			if self.settings["tweeting"] == "True":
				if len(args) == 0:
					try:
						if ((self.lastsentence[e.target] != "") and (e.target in self.settings["tweet_modules"].split())):
							t = Twitter(auth=OAuth(self.access_token, self.access_secret,self.consumer_key, self.consumer_secret))
							t.statuses.update(status=self.lastsentence[e.target])
							msg = "Tweeted \"" + self.lastsentence[e.target] + "\""
						else:
							msg = "Wait until I say something first"
					except:
						print("Last message: " + self.lastsentence[e.target])
						for error in sys.exc_info():
							print(str(error))
						msg = "Error tweeting"
				else:
					commandText = ""
					for word in args:
							commandText += word + ' '
					try:
						t = Twitter(auth=OAuth(self.access_token, self.access_secret,self.consumer_key, self.consumer_secret))
						t.statuses.update(status=commandText)
						msg = "Tweeted \"" + commandText + "\""
					except:
						for error in sys.exc_info():
							print(str(error))
						msg = "Error tweeting"
			self.send(e.target, msg)
	def on_privmsg(self, c, e):
		pass