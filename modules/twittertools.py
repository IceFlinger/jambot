from jambot import botModule
import sys
import twitter
from threading import Timer
from twitter import *
import time
import random
#Twittertools module

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
	def init_settings(self):
		self.set("consumer_key", "", True)
		self.set("consumer_secret", "", True)
		self.set("access_token", "", True)
		self.set("access_secret", "", True)
		self.set("account_name", "IceFlinger")
		self.set("news_chans", "#twitter")
		self.set("tweeting", True)
		self.set("auto_tweeting", False)
		self.set("tweet_modules", "markov")
		self.set("tweetdelay_lower", 900)
		self.set("tweetdelay_upper", 2000)
		self.set("tweet_length", 4)
		self.set("check_timer", 60)

	def on_start(self, c, e):
		self.channels = []
		self.last_update = 0
		self.lastsentence = {}
		self.tweettimer = time.time()
		if self.get("check_timer") > 0:
			self.twitter_schedule(self.get("check_timer"))
		try:
			t = Twitter(auth=OAuth(self.get("access_token"), self.get("access_secret"),self.get("consumer_key"), self.get("consumer_secret")))
			timeline = t.statuses.home_timeline()
			self.last_update = timeline[0]['id']
		except:
			print("couldn't initiate twitter feed")
			for error in sys.exc_info():
				print(str(error))

	def check_twitter(self):
		try:
			t = Twitter(auth=OAuth(self.get("access_token"), self.get("access_secret"), self.get("consumer_key"), self.get("consumer_secret")))
			timeline = t.statuses.home_timeline()
			tweets = []
			for tweet in timeline:
				if (int(tweet['id']) == self.last_update) or (tweet['user']['screen_name'].lower() == self.get("account_name").lower()):
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
				for channel in self.get("news_chans").split():
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
			lencheck = (len(msg.split()) >= int(self.get("tweet_length")))
			timecheck = (time.time() > self.tweettimer)
			autocheck = (self.get("auto_tweeting"))
			modcheck = (modulename in self.get("tweet_modules").split())
			if (lencheck and timecheck and autocheck and modcheck):
				t = Twitter(auth=OAuth(self.get("access_token"), self.get("access_secret"),self.get("consumer_key"), self.get("consumer_secret")))
				t.statuses.update(status=msg)
				self.send(chan, "*")
				self.tweettimer = time.time() + random.randint(self.get("tweetdelay_lower"), self.get("tweetdelay_upper"))
		except:
			for error in sys.exc_info():
				print(str(error))
			print("Error tweeting")

	def do_command(self, c, e, command, args, admin):
		msg = ""
		if ((command == "tweet") and admin):
			if self.get("tweeting"):
				if len(args) == 0:
					try:
						if ((self.lastsentence[e.target] != "") and (e.target in self.get("tweet_modules").split())):
							t = Twitter(auth=OAuth(self.get("access_token"), self.get("access_secret"),self.get("consumer_key"), self.get("consumer_secret")))
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
						t = Twitter(auth=OAuth(self.get("access_token"), self.get("access_secret"),self.get("consumer_key"), self.get("consumer_secret")))
						t.statuses.update(status=self.lastsentence[e.target])
						t.statuses.update(status=commandText)
						msg = "Tweeted \"" + commandText + "\""
					except:
						for error in sys.exc_info():
							print(str(error))
						msg = "Error tweeting"
			self.send(e.target, msg)

	def on_privmsg(self, c, e):
		pass
