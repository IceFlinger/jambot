from jambot import botModule
import irc #first module to need this itself
from threading import Timer
import time
import sys

# Cron module

def check_crontime(timestring): #returns true if valid cron is true for this minute
	times = timestring.split()
	minutes = False
	for minute in times[0].split(","):
		if minute == "*" or minute == str(time.localtime(time.time()).tm_min):
			minutes = True
	hours = False
	for hour in times[1].split(","):
		if hour == "*" or hour == str(time.localtime(time.time()).tm_hour):
			hours = True
	days = False
	for day in times[2].split(","):
		if day == "*" or day == str(time.localtime(time.time()).tm_mday):
			days = True
	months = False
	for month in times[3].split(","):
		if month == "*" or month == str(time.localtime(time.time()).tm_mon):
			months = True
	weekdays = False
	for weekday in times[4].split(","):
		if weekday == "*" or weekday == str(time.localtime(time.time()).tm_wday):
			weekdays = True
	return minutes and hours and days and months and weekdays
	#Only returns true if we pass checks for every time slot

def validate_crontime(timestring): #returns true if given string is a valid cron timing
	times = timestring.split()
	if len(times) != 5:
		return False
	valid = True
	try:
		minutes = True
		for minute in times[0].split(","):
			if not (minute == "*"): #bypass checking * as an int, it's a wildcard for everything
				val = int(minute)
				if not ((0 <= val) and (val <= 59)): #each time range needs to be checked between seperate vals
					minutes = False
		hours = True
		for hour in times[1].split(","):
			if not (hour == "*"):
				val = int(hour)
				if not ((0 <= val) and (val <= 23)):
					hours = False
		days = True
		for day in times[2].split(","):
			if not (day == "*"):
				val = int(day)
				if not ((1 <= val) and (val <= 31)):
					days = False
		months = True
		for month in times[3].split(","):
			if not (month == "*"):
				val = int(month)
				if not ((1 <= val) and (val <= 12)):
					months = False
		weekdays = True
		for weekday in times[4].split(","):
			if not (weekday == "*"):
				val = int(weekday)
				if not ((0 <= val) and (val <= 6)):
					weekdays = False
		valid = minutes and hours and days and months and weekdays
	except:
		return False
	return valid

class moduleClass(botModule):
	dbload = True
	def on_start(self, c, e):
		self.cron_schedule(60-time.localtime(time.time()).tm_sec)
		self.ownhost = c.nickname
		self.c = c

	def on_event(self, c, e):
		if e.type == "join" and e.source.split("!")[0] == c.nickname:
			self.ownhost = e.source

	def on_load_db(self):
		self.db_query("CREATE TABLE IF NOT EXISTS cron (id INTEGER PRIMARY KEY ASC, crontime text, channel text, command text)")
		self.db_commit()

	def fake_command(self, channel, command_string):
		newarg = [self.bot.get("command_prefix") + command_string]
		event = irc.client.Event("pubmsg", self.ownhost, channel, arguments=newarg)
		self.bot.on_command(self.c, event)

	def do_command(self, c, e, command, args, admin):
		if (command == "testcommand") and args and admin:
			self.fake_command(args[0], " ".join(args[1:]))
		elif (command == "addcron") and args and admin:
			if len(args) < 7:
				self.send(e.target, "Not enough args, format: *minutes *hours *days *months *wdays channel command [args]")
			else:
				timestring = " ".join(args[0:5])
				channel = args[5]
				command = " ".join(args[6:])
				if validate_crontime(timestring):
					try:
						self.db_query("INSERT INTO cron (crontime, channel, command) VALUES (?, ?, ?)", (timestring, channel, command))
						self.db_commit()
						self.send(e.target, "Added new cron entry, " + timestring + " " + channel + " " + command)
					except:
						self.send(e.target, "Something went wrong inserting into database")
						pass
				else:
					self.send(e.target, "cron timing '" + timestring + "' isn't properly formatted")
		elif (command == "listcron") and admin:
			try:
				query = self.db_query('SELECT * FROM cron')
				self.send(e.target, "cron events: ")
				for item in query:
					self.send(e.target, str(item[0]) + ": " + item[1] + " " + item[2] + " " + item[3])
			except:
				self.send(e.target, "DB error")
				for error in sys.exc_info():
					print(str(error))
				pass
		elif (command == "delcron") and args and admin:
			if len(args) != 1:
				self.send(e.target, "Give a single crontab id to delete")
			else:
				try:
					cronid = int(args[0])
					self.db_query("DELETE FROM cron WHERE id=?", (cronid, ))
					self.db_commit()
					self.send(e.target, "Deleted " + str(cronid) + " from cron list")
				except:
					self.send(e.target, "Something went wrong deleting " + args[0] + " from list")
					for error in sys.exc_info():
						print(str(error))

	def cron_execute(self):
		try:
			query = self.db_query('SELECT * FROM cron')
			for item in query:
				try:
					if check_crontime(item[1]):
						print("cron event: " + str(item[0]) + ": " + item[1] + " " + item[2] + " " + item[3])
						self.fake_command(item[2], item[3])
				except:
					print("cron error!!: " + str(item[0]) + ": " + item[1] + " " + item[2] + " " + item[3])
					for error in sys.exc_info():
						print(str(error))
		except:
			print("DB error?")
			for error in sys.exc_info():
				print(str(error))
			pass
		self.cron_schedule(60)

	def cron_schedule(self, interval):
		timer = Timer(interval, self.cron_execute, ())
		timer.setDaemon(True)
		timer.start()