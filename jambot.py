#!/usr/bin/env python
import irc.client
import irc.bot
import sqlite3
import configparser
import traceback
import importlib
import ssl
import sys

# jambot modular IRC bot
# by ice at irc.kickinrad.tv

config_file = "jambot.cfg"

class botModule():
	dbload = False

	def _load_settings(self, config_file):
		self.config = configparser.ConfigParser()
		self.config.read(config_file)
		if self.name in self.config.sections():
			for key in self.config[self.name]:
				self.settings[key] = self.config[self.name][key]
	def __init__(self, name, config_file, bot):
		self.bot = bot
		self.name = name
		self.settings = {}
		self._load_settings(config_file)

	def on_start(self, c, e):
		pass
	def on_load_db(self):
		pass

	def send(self, chan, msg):
		self.bot.send_msg(chan, msg, self.name)
	def db_query(self, statement, params=()):
		return self.bot.database_query(statement, params)
	def db_commit(self):
		self.bot.database_commit()

	def do_command(self, c, e, command, args, admin):
		pass
	def on_send(self, chan, msg, modulename):
		pass
	def on_pubmsg(self, c, e):
		pass
	def on_event(self, c, e):
		pass
	def on_privmsg(self, c, e):
		pass
	def shutdown(self):
		pass


class botMain(irc.bot.SingleServerIRCBot):
	def _load_settings(self):
		self.config = configparser.ConfigParser()
		self.config.read(config_file)
		self.modulenames = self.config["settings"]["modulenames"].split()
		self.database = self.config["settings"]["database"]
		self.channellist = self.config["settings"]["channellist"].split()
		self.nickname = self.config["settings"]["nickname"]
		self.realname = self.config["settings"]["realname"]
		self.serverhost = self.config["settings"]["serverhost"]
		self.serverport = int(self.config["settings"]["serverport"])
		self.serverpass = self.config["settings"]["serverpass"]
		self.server = [irc.bot.ServerSpec(self.serverhost, self.serverport, self.serverpass)]
		self.ssl = False
		if self.config["settings"]["ssl"] == "True":
			self.ssl = True
		self.command_prefix = self.config["settings"]["command_prefix"][0]
		self.owner_hosts = self.config["settings"]["owner_hosts"].split()
		self.version = self.config["settings"]["version"]

	def _load_modules(self):
		for module in self.modulenames:
			moduleClass = getattr(importlib.import_module("modules." + module), 'moduleClass')
			self.modules.append(moduleClass(module, config_file, self))
			print("Loaded " + module)

	def _load_db(self):
		for module in self.modules:
			if module.dbload:
				if self.db == None:
					self.db = sqlite3.connect(self.database, check_same_thread=False)
				module.on_load_db()

	def __init__(self):
		self.settings = {}
		self.modules = []
		self.db = None
		self._load_settings()
		self._load_modules()
		self._load_db()

	def initialize(self):
		print("Connecting...")
		reactor = irc.connection.Factory()
		if self.ssl:
			reactor = irc.connection.Factory(wrapper=ssl.wrap_socket)
		irc.bot.SingleServerIRCBot.__init__(self, self.server, self.nickname, self.realname, connect_factory=reactor)
		self.start()

	def on_welcome(self, c, e):
		print("Connected!")
		for channel in self.channellist:
			c.join(channel)
		self.c = c
		for module in self.modules:
			module.on_start(c, e)

	def send_msg(self, chan, msg, modulename):
		self.c.privmsg(chan, msg)
		for module in self.modules:
			module.on_send(chan, msg, modulename)

	def database_query(self, statement, params):
		cursor =  self.db.cursor()
		return cursor.execute(statement, params).fetchall()

	def database_commit(self):
		self.db.commit()

	def on_pubmsg(self, c, e):
		if e.arguments[0][0] == self.command_prefix:
			self.on_command(c, e)
		else:
			for module in self.modules:
				module.on_pubmsg(c, e)

	def on_privmsg(self, c, e):
		if e.arguments[0][0] == self.command_prefix:
			self.on_command(c, e)
		else:
			for module in self.modules:
				module.on_privmsg(c, e)

	def on_command(self, c, e):
		command = e.arguments[0].split()[0].split(self.command_prefix)[1]
		args = e.arguments[0].split()[1:]
		admin = False
		if e.type=="privmsg":
			e.target = e.source.split("!")[0]
		for host in self.owner_hosts:
			if e.source.split("@")[1] == host:
				admin = True
		while admin:
			if command == "join":
				for arg in args:
					if arg[0] != "#":
						self.send_msg(e.target, "Invalid channel name", "jambot")
					else:
						self.send_msg(e.target, "Joining " + arg, "jambot")
						c.join(arg)

			elif command == "part":
				if len(args) == 0 and e.target != e.source:
					c.part(e.target)
				elif args:
					for arg in args:
						if arg[0] != "#":
							self.send_msg(e.target, "Invalid channel name", "jambot")
						else:
							self.send_msg(e.target, "Parting " + arg, "jambot")
							c.part(arg)
			elif command == "nick":
				if args[0].isalnum(): #lazy way to check valid nick
					self.send_msg(e.target, "Setting nick to " + args[0], "jambot")
					c.nick(args[0])
					self.nickname = args[0]
				else:
					self.send_msg(e.target, "Invalid nick (" + args[0] + ")", "jambot")

			elif command == "setprefix":
				self.send_msg(e.target, "Setting command prefix to " + args[0][0], "jambot")
				self.command_prefix = args[0][0]

			elif command == "addowner":
				for arg in args:
					if "@" not in arg:
						self.send_msg(e.target, "Invalid host", "jambot")
					else:
						self.send_msg(e.target, "Adding " + arg + "to owners", "jambot")
						self.owners += " " + arg

			elif command == "quit":
				self.send_msg(e.target, "Quitting...", "jambot")
				self.shutdown()

			else:
				break
			return

		if command == "version":
			self.send_msg(e.target, "Version: " + self.version, "jambot")

		else:
			for module in self.modules:
				module.do_command(c, e, command, args, admin)

	def on_error(self, c, e):
		for module in self.modules:
			module.on_privmsg(c, e)
	def on_join(self, c, e):
		for module in self.modules:
			module.on_event(c, e)
	def on_kick(self, c, e):
		for module in self.modules:
			module.on_event(c, e)
	def on_mode(self, c, e):
		for module in self.modules:
			module.on_event(c, e)
	def on_part(self, c, e):
		for module in self.modules:
			module.on_event(c, e)
	def on_ping(self, c, e):
		for module in self.modules:
			module.on_privmsg(c, e)
	def on_privnotice(self, c, e):
		for module in self.modules:
			module.on_privmsg(c, e)
	def on_pubnotice(self, c, e):
		for module in self.modules:
			module.on_event(c, e)
	def on_quit(self, c, e):
		for module in self.modules:
			module.on_event(c, e)
	def on_invite(self, c, e):
		for module in self.modules:
			module.on_event(c, e)
	def on_pong(self, c, e):
		for module in self.modules:
			module.on_privmsg(c, e)
	def on_action(self, c, e):
		for module in self.modules:
			module.on_event(c, e)
	def on_topic(self, c, e):
		for module in self.modules:
			module.on_event(c, e)
	def on_nick(self, c, e):
		for module in self.modules:
			module.on_event(c, e)
	def shutdown(self):
		for module in self.modules:
			module.shutdown()
		if self.db != None:
			self.db.close()
		print("Disconnecting...")
		self.die()

if __name__ == "__main__":
	if "--help" in sys.argv:
		print("Jambot Modular IRC Bot. Usage:")
		print(" jambot.py [config file]")
		print("Defaults to jambot.cfg")
		sys.exit(0)
	if len(sys.argv) > 1:
		config_file = sys.argv[1]
	bot = botMain()
	try:
		bot.initialize()
	except KeyboardInterrupt as e:
		bot.shutdown()
	except SystemExit as e:
		bot.shutdown()
	except:
		traceback.print_exc()
	bot.shutdown()
