from jambot import botModule
#Nickserv module
class moduleClass(botModule):
#	dbload = True

	def init_settings(self):
		self.set("nickserv_pass", "", True)

	def on_privmsg(self, c, e):
		if e.type=="privnotice" and e.source.split("!")[0].lower()=="nickserv":
			if self.get("nickserv_pass") != "":
				if "not registered" in e.arguments[0].lower():
					self.send("nickserv", "register " + self.get("nickserv_pass"))
				elif "is registered" in e.arguments[0].lower():
					self.send("nickserv", "identify " + self.get("nickserv_pass"))
			else:
				print("Nickserv module loaded but no password set, not doing anything")
