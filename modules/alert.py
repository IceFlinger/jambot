from jambot import botModule
import logging
import sys

# Quote module
class moduleClass(botModule):
	dbload = True

	def init_settings(self):
		self.logger = logging.getLogger("jambot.alert")

	def on_load_db(self):
		self.db_query("CREATE TABLE IF NOT EXISTS alert (id INTEGER PRIMARY KEY ASC, name text)")
		self.db_commit()

	def do_command(self, c, e, command, args, admin):
		msg = ""
		caller = e.source.nick
		if(admin and args):
			caller = args[0]
		if (command == "unalert"):
			try:
				existing = self.db_query('SELECT name FROM alert')
				if (caller, ) not in existing:
					self.db_query("INSERT INTO alert (name) VALUES (?)", (caller, ))
					self.db_commit()
					self.send(e.target, "Now ignoring " + caller + " from alerts")
				else:
					self.send(e.target, caller + " is already ignored from alerts")
			except:
				self.send(e.target, "Something went wrong inserting into database")
				for error in sys.exc_info():
					logging.info(str(error))
		if (command == "realert"):
			try:
				existing = self.db_query('SELECT name FROM alert')
				if (caller, ) in existing:
					self.db_query("DELETE FROM alert WHERE name=?", (caller, ))
					self.db_commit()
					self.send(e.target, "Now alerting " + caller)
				else:
					self.send(e.target, caller + " isn't ignored from alerts.")
			except:
				self.send(e.target, "Something went wrong removing from database")
				for error in sys.exc_info():
					logging.info(str(error))
		elif (command == "listalert") and admin:
			try:
				query = self.db_query('SELECT * FROM alert')
				self.send(e.target, "ignored alerts: ")
				for item in query:
					self.send(e.source.nick, str(item[0]) + ": " + item[1])
			except:
				self.send(e.source.nick, "DB error")
				for error in sys.exc_info():
					logging.info(str(error))
		if (command == "alert"):
			ignore = self.db_query('SELECT name FROM alert')
			for user in self.userlist(c, e):
				if (caller != user) and ((user,) not in ignore):
					msg += user + " "
		if msg != "":
			self.send(e.target, msg)
