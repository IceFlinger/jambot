from jambot import botModule
import sys

# Tagging module
class moduleClass(botModule):
	dbload = True
	def help(command):
		if command=="tag":
			return "usage: <tag> <content>; used to save a message or URL to a certain tag"
		return ""

	def init_settings(self):
		self.set("local_dumpfile", "", "Local file to dump tags to when requested", True)
		self.set("web_dumpfile", "", "Web location of dumped text file to return on dumps")

	def on_load_db(self):
		self.db_query("CREATE TABLE IF NOT EXISTS tags (id INTEGER PRIMARY KEY ASC, name text UNIQUE NOT NULL, tagtext text DEFAULT '')")
		self.db_commit()

	def do_command(self, c, e, command, args, admin):
		if (command == "tag") and len(args)>1:
			try:
				self.db_query("INSERT OR IGNORE INTO tags (name) VALUES (?)", (args[0], ))
				self.db_query("UPDATE tags SET tagtext = ? WHERE name=?", (' '.join(w for w in args[1:]), args[0]))
				self.db_commit()
				self.send(e.target, "Tagged " + args[0] + " with '" + ' '.join(w for w in args[1:]) + "'")
			except:
				self.send(e.target, "Couldn't set tag")
		elif command == "dumptags" and admin:
			try:
				dump = open(self.get("local_dumpfile"), "w")
				tags = self.db_query("SELECT * FROM tags")
				for tag in tags:
					dump.write(str(tag[0]) + "\t" + str(tag[1]) + "\t" + str(tag[2]) + "\n")
				if self.get("web_dumpfile") != "":
					self.send(e.target, "Dumped tags to " + self.get("web_dumpfile"))
				dump.close()
			except:
				self.send(e.target, "Couldn't dump tags")
				pass
		elif (command == "deltag") and args and admin:
			if len(args) != 1:
				self.send(e.target, "Give a single tag to delete")
			else:
				try:
					self.db_query("DELETE FROM tags WHERE name=?", (args[0], ))
					self.db_commit()
					self.send(e.target, "Deleted " + args[0] + " from tags")
				except:
					self.send(e.target, "Something went wrong deleting " + args[0] + " from list")
					for error in sys.exc_info():
						print(str(error))
		else:
			tags = self.db_query("SELECT name FROM tags")
			for tag in tags:
				if tag[0] == command:
					tagtext = self.db_query("SELECT tagtext FROM tags WHERE name=?", (command, ))[0][0]
					self.db_commit()
					self.send(e.target, tagtext)
