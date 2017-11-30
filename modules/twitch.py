from jambot import botModule
import sys
import requests
from threading import Timer
import time
#Twitch module

def lim_space(string, count):
	if string == None:
		string = "" #REALLY TWITCH
	if len(string) > count:
		return string[0:count-3] + "..."
	else:
		return string



class moduleClass(botModule):
	dbload = True
	def init_settings(self):
		self.set("check_streams", True, "Enable or disable querying for stream info (needed to count time)")
		self.set("announce_chans", "", "Announce when a tracked stream comes online in these channels")
		self.set("max_gamelength", 16, "Maximum length to print of game titles")
		self.set("max_statuslength", 24, "Maximum length to print of game titles")
		self.set("api_client_id", "", "Client ID for twitch API usage", True)

	def on_load_db(self):
		self.db_query("CREATE TABLE IF NOT EXISTS streams (id INTEGER PRIMARY KEY ASC, channel text, totaltime INTEGER DEFAULT 0)")
		self.db_commit()

	def on_start(self, c, e):
		self.channels = []
		self.check_streams(True)
		self.check_schedule(60)

	def validate_twitch_name(self, twitchname):
		try:
			s = requests.Session()
			check = s.get("https://api.twitch.tv/kraken/channels/" + twitchname,
						headers={
							"Client-ID": self.get("api_client_id")
						})
			result = check.json()
			if "error" in result:
				return False
			return True
		except:
			return False

	def announce_stream(self, stream):
		for ircchan in self.get("announce_chans").split(" "):
			msg = ""
			name = stream["channel"]["name"]
			game =  lim_space(stream["game"], self.get("max_gamelength"))
			status = lim_space(stream["channel"]["status"], self.get("max_statuslength"))
			msg = name + " is now streaming " + game + " at https://twitch.tv/" + name + " (" + status + ")"
			self.send(ircchan, msg)

	def check_streams(self, silent = False):
		if self.get("check_streams"):
			query = [""]
			streams = []
			updated = []
			try:
				names = self.db_query("SELECT channel FROM streams")
				for name in names:
					query.append(name[0])
				s = requests.Session()
				check = s.get("https://api.twitch.tv/kraken/streams",
						headers={
							"Client-ID": self.get("api_client_id")
						},
						params={
							"channel":	",".join(query)
						})
				streams = check.json()["streams"]
				for channel in self.channels:
					live = False
					for stream in streams:
						if stream["channel"]["name"] == channel["channel"]["name"]:
							live = True
					if not live:
						self.channels.remove(channel)
			except:
				for error in sys.exc_info():
						print(str(error))
				print("Something went wrong checking current streams")
			if streams is None:
				streams = []
			for stream in streams:
				new = True
				for channel in self.channels:
					if stream["channel"]["name"] == channel["channel"]["name"]:
						new = False
				if new:
					self.channels.append(stream)
					if not silent:
						self.announce_stream(stream)
				if not silent:
					try:
						self.db_query("UPDATE streams SET totaltime=totaltime+1 WHERE channel=?", (stream["channel"]["name"], ))
						self.db_commit()
						updated.append(stream["channel"]["name"])
					except:
						for error in sys.exc_info():
							print(str(error))
						print("Error updating time for stream " + stream["channel"]["name"])
			if updated:
				print(str(time.time()) + " Updated stream times for: " + ",".join(updated))

	def check_schedule(self, checktimer):
		timer = Timer(checktimer, self.check_execute, ())
		timer.setDaemon(True)
		timer.start()

	def check_execute(self):
		self.check_streams()
		self.check_schedule(60)

	def do_command(self, c, e, command, args, admin):
		if command == "streams":
			msg = ""
			if not self.channels:
				self.send(e.target, "No streams are currently live")
			else:
				for stream in self.channels:
					name = stream["channel"]["name"]
					game = lim_space(stream["game"], self.get("max_gamelength")) 
					status = lim_space(stream["channel"]["status"], self.get("max_statuslength"))
					viewers = str(stream["viewers"])
					msg = msg + "https://twitch.tv/" + name + ", " + game + ", " + status + ", " + viewers + "v | "
			while len(msg) > 383:
				self.send(e.target, msg[:383])
				msg = msg[384:]
			self.send(e.target, msg)
		elif (command == "liststreams") or (command == "streamlist"):
			try:
				query = self.db_query('SELECT * FROM streams ORDER BY totaltime DESC')
				self.send(e.target, "Keeping track of these twitch streams: ")
				for item in query:
					self.send(e.target, str(item[0]) + ": " + item[1] + " (" + str(item[2]) + " minutes)")
			except:
				self.send(e.target, "DB error")
				for error in sys.exc_info():
					print(str(error))
				pass
		elif (command == "streamtime") or (command == "timestreamed"):
			if len(args) != 1:
				self.send(e.target, "Give a single stream name to delete")
			else:
				try:
					query = self.db_query('SELECT * FROM streams WHERE channel=?', (args[0],))
					if len(query) == 0:
						self.send(e.target, "Stream not found")
					else:
						for item in query:
							self.send(e.target, item[1] + " (" + str(item[2]) + " minutes)")
				except:
					self.send(e.target, "DB error")
					for error in sys.exc_info():
						print(str(error))
					pass
		elif (command == "delstream") and args and admin:
			if len(args) != 1:
				self.send(e.target, "Give a single stream name to delete")
			else:
				try:
					self.db_query("DELETE FROM streams WHERE channel=?", (args[0], ))
					self.db_commit()
					self.send(e.target, "Deleted " + args[0] + " from stream list")
				except:
					self.send(e.target, "Something went wrong deleting " + args[0] + " from list")
					for error in sys.exc_info():
						print(str(error))
		elif (command == "setstreamtime") and admin:
			if len(args) != 2:
				self.send(e.target, "Usage: setstreamtime streamname time (stream name 'all' for all)")
			else:
				try:
					if(args[0]=="all"):
						self.db_query("UPDATE streams SET totaltime=?", (int(args[1]), ))
					else:
						self.db_query("UPDATE streams SET totaltime=? WHERE channel=?", (int(args[1]),args[0]))
					self.db_commit()
					self.send(e.target, "Updated " + args[0] + " to have " + args[1] + " minutes streamed.")
				except:
					self.send(e.target, "Something went wrong changing " + args[0] + " time")
					for error in sys.exc_info():
						print(str(error))
		elif (command == "addstream") and args and admin:
			if len(args) != 1:
				self.send(e.target, "Give a single twitch stream to add to the list")
			else:
				if self.validate_twitch_name(args[0]):
					try:
						existing = self.db_query('SELECT channel FROM streams')
						if (args[0], ) not in existing:
							self.db_query("INSERT INTO streams (channel) VALUES (?)", (args[0], ))
							self.db_commit()
							self.send(e.target, "Added new stream entry, " + args[0])
						else:
							self.send(e.target, args[0] + " is already added to the list")
					except:
						self.send(e.target, "Something went wrong inserting into database")
						for error in sys.exc_info():
							print(str(error))
				else:
					self.send(e.target, args[0] + " isn't a real twitch stream")
