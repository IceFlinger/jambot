from jambot import botModule
#Nickserv module
class moduleClass(botModule):
#	dbload = True
	def on_start(self, c, e):
		self.nickserv_pass	= self.settings["nickserv_pass"]
	def on_privmsg(self, c, e):
		if e.type=="privnotice" and e.source.split("!")[0].lower()=="nickserv":
			if self.nickserv_pass != "":
				if "not registered" in e.arguments[0].lower():
					self.send("nickserv", "register " + self.nickserv_pass)
				elif "is registered" in e.arguments[0].lower():
					self.send("nickserv", "identify " + self.nickserv_pass)
			else:
				print("Nickserv module loaded but no password set, not doing anything")
