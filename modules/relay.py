from jambot import botModule
import time
import logging


#relay module
class moduleClass(botModule):
	def init_settings(self):
		self.set("relay", True, "Toggle for relaying messages on join")
		self.set("buffer", 5, "Maximum number of lines to keep in relay")
		self.set("timestamp_format", "[%m/%d.%H:%M:%S]", "Timestamp format (https://docs.python.org/3.5/library/time.html?highlight=time#time.strftime)")
		self.set("intro", "Latest messages:", "String to intro the relay playback")
		self.logger = logging.getLogger("jambot.relay")

	def timestamp(self):
		return time.strftime(self.get("timestamp_format"))

	def on_start(self, c, e):
		self.own_nick = c.nickname
		self.buffer = []

	def buffer_add(self, msg, targ):
		self.buffer.append((msg, targ))
		while len(self.buffer) > self.get("buffer"):
			self.buffer.pop(0)

	def do_command(self, c, e, command, args, admin):
		if e.type == "pubmsg":
			newmsg = self.timestamp() + " <" + e.source.split("!")[0] + ">: " + e.arguments[0]
			self.buffer_add(newmsg, e.target)
		if (command == "relayclear") and admin:
			self.send(e.target, "Relay buffer cleared")
			self.buffer = []

	def on_send(self, chan, msg, modulename):
		newmsg = self.timestamp() + "<" + self.own_nick + ">: " + msg 
		self.buffer_add(newmsg, chan)

	def on_pubmsg(self, c, e):
		if e.type == "pubmsg":
			newmsg = self.timestamp() + " <" + e.source.split("!")[0] + ">: " + e.arguments[0]
			self.buffer_add(newmsg, e.target)

	def send_replay(self, c, e):
		user = e.source.split("!")[0]
		channel = e.target
		c.notice(user, self.get("intro"))
		for message in self.buffer:
			if (message[1] == channel) or (message[1] == "*"):
				c.notice(user, message[0])

	def on_event(self, c, e):
		if e.type=="nick":
			newmsg = self.timestamp() + " " + e.source.split("!")[0] + " changed nick to " + e.target
			self.buffer_add(newmsg, "*")
		elif e.type=="action":
			newmsg = self.timestamp() + " *" + e.source.split("!")[0] + " "  + e.arguments[0]
			self.buffer_add(newmsg, e.target)
		elif e.type=="mode":
			newmsg = self.timestamp() + " " + e.source.split("!")[0] + " sets mode " + e.arguments[0] + " on " + e.arguments[1]
			self.buffer_add(newmsg, e.target)
		elif e.type=="topic":
			newmsg = self.timestamp() + " " + e.source.split("!")[0] + " sets topic to " + e.arguments[0]
			self.buffer_add(newmsg, e.target)
		elif e.type=="kick":
			newmsg = self.timestamp() + " " + e.source.split("!")[0] + " kicks " + e.arguments[0] + " from " + e.target
			if len(e.arguments) == 2:
				newmsg = newmsg + " (" + e.arguments[1] + ")"
			self.buffer_add(newmsg, e.target)
		elif e.type=="join":
			if (e.source.split("!")[0] != c.nickname) and self.get("relay"):
				self.send_replay(c, e)
			newmsg = self.timestamp() + " " + e.source.split("!")[0] + " joins " + e.target
			self.buffer_add(newmsg, e.target)
		elif e.type=="part":
			newmsg = self.timestamp() + " " + e.source.split("!")[0] + " parts " + e.target
			if e.arguments:
				newmsg = newmsg + " (" + e.arguments[0] + ")"
			self.buffer_add(newmsg, e.target)
		elif e.type=="quit":
			newmsg = self.timestamp() + " " + e.source.split("!")[0] + " quits"
			if e.arguments:
				newmsg = newmsg + " (" + e.arguments[0] + ")"
			self.buffer_add(newmsg, "*")
		self.own_nick = c.nickname