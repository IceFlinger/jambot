from jambot import botModule


# g8r module
class moduleClass(botModule):
	def init_settings(self):
		self.set("g8r", True, "Enable/disable g8r trap")

	def on_start(self, c, e):
		self.bottom = False

	def on_pubmsg(self, c, e):
		if self.bottom:
			self.send(e.target, "▄███████▄.▲.▲▲▲▲▲▲▲")
			self.send(e.target, "███████████████████▀▀")
			self.bottom = False

	def do_command(self, c, e, command, args, admin):
		if (command == "g8r") and self.get("g8r"):
			self.send(e.target, "──────▄▄████▀█▄")
			self.send(e.target, "───▄██████████████████▄")
			self.send(e.target, "─▄█████.▼.▼.▼.▼.▼.▼.▼▼▼▼")
			self.bottom=True