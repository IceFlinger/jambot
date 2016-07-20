from jambot import botModule

bottom = False
# g8r module
class moduleClass(botModule):
	bottom = False
	def help(command):
		if command=="bark":
			return "barks"
		return ""

	def on_start(self, c, e):
		pass

	def on_load_db(self):
		pass

	def on_pubmsg(self, c, e):
		global bottom
		if bottom:
			self.send(e.target, "▄███████▄.▲.▲▲▲▲▲▲▲")
			self.send(e.target, "███████████████████▀▀")
			bottom = False

	def on_send(self, chan, msg, modulename):
		pass

	def on_event(self, c, e):
		pass

	def do_command(self, c, e, command, args, admin):
		global bottom
		if (command == "g8r"):
			self.send(e.target, "──────▄▄████▀█▄")
			self.send(e.target, "───▄██████████████████▄")
			self.send(e.target, "─▄█████.▼.▼.▼.▼.▼.▼.▼▼▼▼")
			bottom=True

	def shutdown(self):
		pass
