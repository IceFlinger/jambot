from jambot import botModule
import sqlite3
import pycurl
import sys
import random
import re
import string
from io import BytesIO
#Markov chain jambot module
#By ice at irc.kickinrad.tv

def mangle_line(line):
	links = re.findall(r'(https?://\S+)', line)
	f = string.ascii_letters + string.digits + "():<>[].,!?'/-^%$ "
	line = ' '.join(w for w in line.split() if w not in links)
	line = ' '.join(w for w in line.split() if w[0] not in "[\"(")
	line = ' '.join(w for w in line.split() if w[-1] not in "\;%")
	line = ''.join(c for c in line if c in f)
	return line

class moduleClass(botModule):
	dbload = True
	def on_start(self, c, e):
		self.replyrate = int(self.settings["replyrate"])
		self.learning = False
		self.maxchain = int(self.settings["maxchain"])
		if self.settings["learning"]=="True":
			self.learning = True
		self.nickreplyrate = int(self.settings["nickreplyrate"])

	def on_load_db(self):
		self.db_query("CREATE TABLE IF NOT EXISTS contexts (word1 text, word2 text DEFAULT '', freq int DEFAULT 0, UNIQUE(word1, word2))")
		self.db_commit()

	def on_pubmsg(self, c, e):
		chan = e.target
		msg = e.arguments[0]
		own_nick = c.nickname
		phrase = ""
		if self.learning:
			msg = mangle_line(msg)
			words = msg.split()
			for word1, word2 in zip(words[:-1], words[1:]):
				self.db_query("INSERT OR IGNORE INTO contexts (word1, word2) VALUES (?, ?)", (word1, word2))
				self.db_query("UPDATE contexts SET freq = freq + 1 WHERE word1=? AND word2=?", (word1, word2))
			self.db_query("INSERT OR IGNORE INTO contexts (word1) VALUES (?)", (words[-1], ))
			self.db_query("UPDATE contexts SET freq = freq + 1 WHERE word1=? AND word2 is ''", (words[-1], ))
			self.db_commit()
		if ((self.replyrate>random.randint(1,99)) or ((self.nickreplyrate>random.randint(1,99)) and (own_nick in msg))):
			chainlength = 0
			exist_words = []
			for word in self.db_query("SELECT word1, word2 FROM contexts WHERE instr(?, word1) > 0", [msg]):
				if word[0] in msg.split():
					exist_words.append(word)
			if exist_words:
				currentword = exist_words[random.randint(0,len(exist_words)-1)][0]
				while currentword != None:
					print(currentword, end=" ",flush=True)
					next_words = self.db_query("SELECT * FROM contexts WHERE word1 LIKE ? ORDER BY freq ASC", [currentword])
					total_contexts = 0
					for word in next_words:
						total_contexts += int(word[2])
					selection = random.randint(0, int(total_contexts))
					newword = None
					for word in next_words:
						selection -= int(word[2])
						if selection < 0 and newword == None:
							if word[1] != "":
								newword = word[1]
					if newword != currentword:
						phrase += currentword + " "
						chainlength += 1
					if chainlength > self.maxchain:
						newword = None
					currentword = newword
					self.db_commit()
				print("")
		if phrase != "":
			self.send(e.target, phrase)

	def on_send(self, chan, msg, modulename):
		pass

	def on_event(self, c, e):
		pass

	def do_command(self, c, e, command, args, admin):
		if command=="feed" and admin and len(args)>0:
			print("Downloading: " + args[0])
			self.send(e.target, "Downloading: " + args[0])
			textbytes = BytesIO()
			textconn = pycurl.Curl()
			textconn.setopt(textconn.URL, args[0])
			textconn.setopt(textconn.WRITEDATA, textbytes)
			textconn.perform()
			textconn.close()
			text = textbytes.getvalue().decode('iso-8859-1').split('\n')
			linecount = 0
			print("Learning...")
			self.send(e.target, "Learning")
			for line in text:
				line = mangle_line(line)
				words = line.split()
				for word1, word2 in zip(words[:-1], words[1:]):
					self.db_query("INSERT OR IGNORE INTO contexts (word1, word2) VALUES (?, ?)", (word1, word2))
					self.db_query("UPDATE contexts SET freq = freq + 1 WHERE word1=? AND word2=?", (word1, word2))
				if len(words)!=0:
					self.db_query("INSERT OR IGNORE INTO contexts (word1) VALUES (?)", (words[-1], ))
					self.db_query("UPDATE contexts SET freq = freq + 1 WHERE word1=? AND word2 is ''", (words[-1], ))
				linecount += 1
				if ((linecount%1000)==0):
					print(str(linecount/1000).split(".")[0] + "k lines, ", end="",flush=True)
				
			print("Learned from " + str(linecount) + " lines")
			self.send(e.target, "Learned from " + str(linecount) + " lines")
			self.db_commit()
			print ("Commited to DB")

	def on_privmsg(self, c, e):
		pass

	def shutdown(self):
		pass