from jambot import botModule


# Quote module
class moduleClass(botModule):
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
		msg = ""
		if (command == "alert"):
			for user in self.userlist(c, e):
				msg += user + " "
		if msg != "":
			self.send(e.target, msg)

	def shutdown(self):
		pass
