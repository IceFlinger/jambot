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
debug = True

class botModule():
	dbload = False

	def set(self, setting, value, secret = False):
		try:
			secret = self.bot.settings[self.name][setting][1]
		except:
			pass
		self.bot.settings[self.name][setting] = (value, secret)

	def get(self, setting):
		return self.bot.settings[self.name][setting][0]

	def init_settings(self):
		pass

	def __init__(self, name, config_file, bot):
		self.bot = bot
		self.name = name
		self.init_settings()

	def help(command):
		return ""

	def on_start(self, c, e):
		pass

	def on_load_db(self):
		pass

	def userlist(self, c, e):
		return self.bot.channels[e.target].users()

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

	def set(self, setting, value):
		self.settings["jambot"][setting] = value

	def get(self, setting):
		return self.settings["jambot"][setting]

	def _load_settings(self):
		self.config = configparser.ConfigParser()
		self.config.read(config_file)
		self.set("modules", self.config["jambot"]["modules"].split())
		self.set("database", self.config["jambot"]["database"])
		self._load_modules()
		for module in self.get("modules"):
			self._load_module_settings(module)
		self._load_db()
		self.set("channels", self.config["jambot"]["channels"].split())
		self.set("nickname", self.config["jambot"]["nickname"])
		self.set("realname", self.config["jambot"]["realname"])
		self.set("serverhost", self.config["jambot"]["serverhost"])
		self.set("serverport", int(self.config["jambot"]["serverport"]))
		self.set("serverpass", self.config["jambot"]["serverpass"])
		self.server = [irc.bot.ServerSpec(self.get("serverhost"), self.get("serverport"), self.get("serverpass"))]
		self.set("ssl", self.config["jambot"].getboolean("ssl"))
		self.set("command_prefix", self.config["jambot"]["command_prefix"][0])
		self.set("owner_hosts", self.config["jambot"]["owner_hosts"].split())
		self.set("version", self.config["jambot"]["version"])

	def _load_modules(self):
		for module in self.get("modules"):
			moduleClass = getattr(importlib.import_module("modules." + module), 'moduleClass')
			self.settings[module] = {}
			newmodule = moduleClass(module, config_file, self)
			self.modules.append(newmodule)
			print("Loaded " + module)

	def _load_module_settings(self, loadtarget):
		error = True
		for module in self.modules:
			if module.name == loadtarget:
				error = False #right module was found in conf, attempt to parse it
				self.config.read(config_file)
				for setting in self.settings[loadtarget]:
					if loadtarget in self.config.sections():
						for conf in self.config[loadtarget]:
							if setting == conf: #we want to ignore both missing and extra configs, only attempt matching pairs
								value = self.settings[loadtarget][setting][0]
								try:
									if type(value) is int:
										module.set(setting, self.config[loadtarget].getint(conf))
									elif type(value) is float:
										module.set(setting, self.config[loadtarget].getfloat(conf))
									elif type(value) is bool:
										module.set(setting, self.config[loadtarget].getboolean(conf))
									else:
										module.set(setting, self.config[loadtarget][conf])
								except:
									error = True #at least one setting/conf pair is malformed
					else:
						error = True #Module settings don't exist in file
		return not error

	def _load_db(self):
		for module in self.modules:
			if module.dbload:
				if self.db == None:
					self.db = sqlite3.connect(self.get("database"), check_same_thread=False)
				module.on_load_db()

	def __init__(self):
		self.settings = {}
		self.settings["jambot"] = {}
		self.modules = []
		self.db = None
		self._load_settings()

	def initialize(self):
		print("Connecting...")
		irc.client.ServerConnection.buffer_class = irc.buffer.LenientDecodingLineBuffer
		reactor = irc.connection.Factory()
		if self.get("ssl"):
			reactor = irc.connection.Factory(wrapper=ssl.wrap_socket)
		irc.bot.SingleServerIRCBot.__init__(self, self.server, self.get("nickname"), self.get("realname"), connect_factory=reactor)
		self.start()

	def on_welcome(self, c, e):
		print("Connected!")
		for channel in self.get("channels"):
			c.join(channel)
		self.c = c
		for module in self.modules:
			module.on_start(c, e)

	def send_msg(self, chan, msg, modulename = "jambot"):
		self.c.privmsg(chan, msg)
		for module in self.modules:
			module.on_send(chan, msg, modulename)

	def database_query(self, statement, params):
		cursor = self.db.cursor()
		return cursor.execute(statement, params).fetchall()

	def database_commit(self):
		self.db.commit()

	def on_pubmsg(self, c, e):
		try:
			if e.arguments[0][0] == self.get("command_prefix"):
				self.on_command(c, e)
			else:
				for module in self.modules:
					module.on_pubmsg(c, e)
		except:
			for error in sys.exc_info():
				print(str(error))
			if debug:
				raise
			else:
				pass

	def on_privmsg(self, c, e):
		try:
			if e.arguments[0][0] == self.get("command_prefix"):
				self.on_command(c, e)
			else:
				for module in self.modules:
					module.on_privmsg(c, e)
		except:
			for error in sys.exc_info():
				print(str(error))
			if debug:
				raise
			else:
				pass

	def on_command(self, c, e):
		command = e.arguments[0].split()[0].split(self.get("command_prefix"))[1]
		args = e.arguments[0].split()[1:]
		admin = False
		if e.type == "privmsg":
			e.target = e.source.split("!")[0]
		for host in self.get("owner_hosts"):
			if e.source.split("@")[1] == host:
				admin = True
		while admin: #Don't remember why I did this this way
			if command == "join":
				for arg in args:
					if arg[0] != "#":
						self.send_msg(e.target, "Invalid channel name")
					else:
						self.send_msg(e.target, "Joining " + arg)
						c.join(arg)

			elif command == "part":
				if len(args) == 0 and e.target != e.source:
					c.part(e.target)
				elif args:
					for arg in args:
						if arg[0] != "#":
							self.send_msg(e.target, "Invalid channel name")
						else:
							self.send_msg(e.target, "Parting " + arg)
							c.part(arg)
			elif command == "nick":
				if args[0].isalnum():  # lazy way to check valid nick
					self.send_msg(e.target, "Setting nick to " + args[0])
					c.nick(args[0])
					self.set("nickname", args[0])
				else:
					self.send_msg(e.target, "Invalid nick (" + args[0] + ")")

			elif command == "setprefix":
				self.send_msg(e.target, "Setting command prefix to " + args[0][0])
				self.set("command_prefix", args[0][0])

			elif command == "addowner":
				for arg in args:
					if "@" not in arg:
						self.send_msg(e.target, "Invalid host")
					else:
						self.send_msg(e.target, "Adding " + arg + "to owners")
						self.set("owner_hosts", (self.get("owner_hosts") + " " + arg))

			elif command == "quit":
				self.send_msg(e.target, "Quitting...")
				self.shutdown()

			elif command == "set" and args:
				if len(args) >= 3:
					qmodule = args[0]
					qsetting = args[1]
					qvalue = " ".join(args[2:])
					if qmodule in self.get("modules"):
						if qsetting in self.settings[qmodule]:
							if e.type == "privmsg" or not self.settings[qmodule][qsetting][1]:
								try:
									oldvalue = self.settings[qmodule][qsetting][0]
									newvalue = oldvalue
									if type(oldvalue) is float:
										newvalue = float(qvalue)
									elif type(oldvalue) is int:
										newvalue = int(qvalue)
									elif type(oldvalue) is bool:
										if qvalue.lower() in ['true', '1', 'on', 'y', 'yes']:
											newvalue = True
										elif qvalue.lower() in ['false', '0', 'off', 'n', 'no']:
											newvalue = False
									else:
										newvalue = str(qvalue)
									self.settings[qmodule][qsetting] = (newvalue, self.settings[qmodule][qsetting][1])
									self.send_msg(e.target, qmodule + " setting " + qsetting + " changed from " + str(oldvalue) + " to " + str(newvalue))
								except:
									self.send_msg(e.target, qmodule + " setting " + qsetting + " could not be set to " + str(qvalue))
							else:
								self.send_msg(e.target, qmodule + " setting " + qsetting + " is protected, set with a privmsg")
						else:
							self.send_msg(e.target, qsetting + " isn't a setting of " + qmodule)
					else:
						self.send_msg(e.target, qmodule + " is not a loaded module")
				elif len(args) == 2:
					qmodule = args[0]
					qsetting = args[1]
					if qmodule in self.get("modules"):
						print(qmodule + ": " + str(self.settings[qmodule]))
						if qsetting in self.settings[qmodule]:
							if e.type == "privmsg" or not self.settings[qmodule][qsetting][1]:
								value = self.settings[qmodule][qsetting][0]
								self.send_msg(e.target, qmodule + " setting " + qsetting + " is set to " + str(value))
							else:
								self.send_msg(e.target, qmodule + " setting " + qsetting + " is protected, check with a privmsg")
						else:
							self.send_msg(e.target, qsetting + " isn't a setting of " + qmodule)
					else:
						self.send_msg(e.target, qmodule + " is not a loaded module")
				else:
					self.send_msg(e.target, "Not enough args: expect 'modulename setting (value)'")

			elif command == "reset" and args:
				for arg in args:
					qmodule = arg
					if qmodule in self.get("modules"):
						if self._load_module_settings(qmodule):
							self.send_msg(e.target, "Reloaded config values for " + qmodule)
						else:
							self.send_msg(e.target, "Error reading config values for " + qmodule + " (missing section or malformed values)")
					else:
						self.send_msg(e.target, qmodule + " is not a loaded module")

			elif command == "reset":
				loaded = ""
				for module in self.get("modules"):
					if self._load_module_settings(qmodule):
						loaded += module + " "
					else:
						self.send_msg(e.target, "Error reading config values for " + module + " (missing section or malformed values)")
				self.send_msg(e.target, "Reloaded config values for " + loaded)

			elif command == "save":
				conf = open(config_file, 'w')
				conf.write('[jambot]\n')
				for setting in self.settings["jambot"]: 
					newconf = self.settings["jambot"][setting]
					if type(newconf) is list:
						newconf = " ".join(self.settings["jambot"][setting])
					conf.write(setting + '\t= ' + str(newconf) + "\n")
				conf.write('\n')
				for module in self.get("modules"):
					conf.write('[' + module + ']\n')
					for setting in self.settings[module]:
						conf.write(setting + '\t= ' + str(self.settings[module][setting][0]) + "\n")
					conf.write('\n')
				conf.close()
				self.send_msg(e.target, "Saved new config to " + config_file)

			else:
				break #Probably for seperate behavior between admins/non with the same command
			return

		if command == "version":
			self.send_msg(e.target, "Version: " + self.get("version"))

		elif command == "set" and args:
			if len(args) < 2:
				self.send_msg(e.target, "Not enough args: expect 'modulename setting'")
			else:
				qmodule = args[0]
				qsetting = args[1]
				if qmodule in self.get("modules"):
					if qsetting in self.settings[qmodule]:
						if not self.settings[qmodule][qsetting][1]:
							value = str(self.settings[qmodule][qsetting][0])
							self.send_msg(e.target, qmodule + " setting " + qsetting + " is set to " + str(value))
						else:
							self.send_msg(e.target, qmodule + " setting " + qsetting + " is protected")
					else:
						self.send_msg(e.target, qsetting + " isn't a setting of " + qmodule)
				else:
					self.send_msg(e.target, qmodule + " is not a loaded module")

		elif command == "modules":
			modulelist = ''
			for module in self.get("modules"):
				modulelist = modulelist + " " + module
			self.send_msg(e.target, "Loaded modules:" + modulelist)

		elif command == "help" and args:
			return #gonna work on help later
			for module in self.modules:
				helpmsg = ""
				helpmsg = module.help(args[0])
				if helpmsg != "":
					self.send_msg(e.target, module.name + ": " + helpmsg)

		elif command == "help":
			return
			self.send_msg(e.target,"help: type " + "help <command> for help on a specific command")

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
