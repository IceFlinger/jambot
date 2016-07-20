from jambot import botModule
import sys
import random

# Choosing module
class moduleClass(botModule):
	dbload = False
	def help(command):
		if command=="tag":
			return "usage: chooses a single paramater randomly out of many"
		return ""

	def on_start(self, c, e):
		pass

	def on_load_db(self):
		pass

	def on_pubmsg(self, c, e):
		pass

	def on_send(self, chan, msg, modulename):
		pass

	def on_event(self, c, e):
		pass

	def do_command(self, c, e, command, args, admin):
		if (command == "choose") and len(args)>1:
			try:
				choice = random.randint(0, len(args)-1)
				self.send(e.target, args[choice])
			except:
				self.send(e.target, "Couldn't choose for some reason")

	def shutdown(self):
		pass
