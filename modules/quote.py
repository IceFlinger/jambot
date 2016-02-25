from jambot import botModule

# Quote module
class moduleClass(botModule):
	dbload = True
	def on_start(self, c, e):
		self.buffernick = 'wew'
		self.buffermsg = 'wew'

	def on_load_db(self):
		self.db_query("CREATE TABLE IF NOT EXISTS quotes (nick text, quote text)")
		self.db_commit()

	def on_pubmsg(self, c, e):
		self.buffernick = e.source.nick
		self.buffermsg = e.arguments[0]

	def on_send(self, chan, msg, modulename):
		self.buffernick = "jambot"
		self.buffermsg = msg

	def on_event(self, c, e):
		if (e.type == "action"):
			self.buffernick = e.source.nick
			self.buffermsg = "/me " + e.arguments[0]

	def do_command(self, c, e, command, args, admin):
		if (command == "addquote"):
			if self.buffernick and self.buffermsg == 'wew':
				self.send(e.target, "No quote stored")
			elif self.buffermsg == '!quote':
				self.send(e.target, "No quote stored")
			else:
				quote = (self.buffernick, self.buffermsg)
				self.db_query("INSERT INTO quotes VALUES (?,?)", quote)
				self.db_commit()
				msg = "Added quote: " + quote[0] + ": " + quote[1]
				self.send(e.target, msg)

		elif ((command == "q") or (command == "quote")):
			query = self.db_query('SELECT * FROM quotes ORDER BY RANDOM() LIMIT 1')[0]
			msg = "Quote: " + query[0] + ": " + query[1]
			self.send(e.target, msg)

	def shutdown(self):
		pass
