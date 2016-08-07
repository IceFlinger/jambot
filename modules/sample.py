from jambot import botModule
#Small sample module
#self.send(chan, msg):
#self.db_query(statement, params)
#self.db_commit()
class moduleClass(botModule):
#	dbload = True
	def init_settings(self):
		self.set("bool", False, "a regular boolean setting")
		self.set("secretbool", False, "a protected boolean setting", True)
		self.set("int", 3, "a regular integer setting")
		self.set("secretint", 4, "a protected integer setting", True)
		self.set("float", 3.23342, "a regular float setting")
		self.set("secretfloat", 4.34234, "a protected float setting",True)
		self.set("string", "default string", "a regular string setting")
		self.set("secretstring", "default secret string", "a protected string setting", True)

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
