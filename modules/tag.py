from jambot import botModule
import sys

# Tagging module
class moduleClass(botModule):
	dbload = True
	def help(command):
		if command=="tag":
			return "usage: <tag> <content>; used to save a message or URL to a certain tag"
		return ""

	def on_start(self, c, e):
		pass

	def on_load_db(self):
		self.db_query("CREATE TABLE IF NOT EXISTS tags (id INTEGER PRIMARY KEY ASC, name text UNIQUE NOT NULL, tagtext text DEFAULT '')")
		self.db_commit()

	def on_pubmsg(self, c, e):
		pass

	def on_send(self, chan, msg, modulename):
		pass

	def on_event(self, c, e):
		pass

	def do_command(self, c, e, command, args, admin):
		if (command == "tag") and len(args)>1:
			try:
				self.db_query("INSERT OR IGNORE INTO tags (name) VALUES (?)", (args[0], ))
				self.db_query("UPDATE tags SET tagtext = ? WHERE name=?", (' '.join(w for w in args[1:]), args[0]))
				self.db_commit()
				self.send(e.target, "Tagged " + args[0] + " with '" + ' '.join(w for w in args[1:]) + "'")
			except:
				self.send(e.target, "Couldn't set tag")
		tags = self.db_query("SELECT name FROM tags")
		for tag in tags:
			if tag[0] == command:
				tagtext = self.db_query("SELECT tagtext FROM tags WHERE name=?", (command, ))[0][0]
				self.db_commit()
				self.send(e.target, tagtext)

	def shutdown(self):
		pass
