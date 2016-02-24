from jambot import botModule
#Small sample module
#self.send(e.target, msg)
class moduleClass(botModule):
	def on_start(self):
		pass
	def on_pubmsg(self, c, e):
		pass
	def on_send(self, chan, msg, modulename):
		pass
	def on_event(self, c, e):
		pass
	def do_command(self, c, e, command, args, admin):
		pass
	def on_privmsg(self, c, e):
		pass
	def shutdown(self):
		pass