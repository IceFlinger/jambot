from jambot import botModule

class moduleClass(botModule):
	#dbload = True
	def init_settings(self):
		pass

	def on_start(self, c, e):
		pass

	def on_load_db(self):
		pass

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
