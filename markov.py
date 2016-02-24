from jambot import botModule
import sqlite3
import pycurl
import sys
import random
import re
from io import BytesIO
#Markov chain jambot module
#By ice at irc.kickinrad.tv
#self.send(e.target, msg)
class moduleClass(botModule):
	def on_start(self):
		self.db = sqlite3.connect(self.settings["database"])
		self.replyrate = int(self.settings["replyrate"])
		self.learning = False
		if self.settings["learning"]=="True":
			self.learning = True
		self.nickreplyrate = int(self.settings["nickreplyrate"])
		self.c = self.db.cursor()
		self.c.execute("CREATE TABLE IF NOT EXISTS contexts (word1 text, word2 text, freq int)")
		self.db.commit()
		
	def on_pubmsg(self, c, e):
		chan = e.target
		msg = e.arguments
		own_nick = c.nickname
		phrase = ""
		if self.learning:
			links = re.findall(r'(https?://\S+)', msg[0])
			if not links:
				exist_words_q = "SELECT word1, word2 FROM contexts WHERE instr(?, word1) > 0"
				exist_words = self.c.execute(exist_words_q, msg).fetchall()
				words = msg[0].split()
				new_contexts = []
				for word1, word2 in zip(words[:-1], words[1:]):
					new_contexts.append((word1, word2))
				new_contexts.append((words[-1], None))
				for context in new_contexts:
						if context in exist_words:
							self.c.execute("UPDATE contexts SET freq = freq + 1 WHERE word1=? AND word2=?", context)
						else:
							self.c.execute("INSERT INTO contexts VALUES (?, ?, 1)", context)
							exist_words.append(context)
				self.db.commit()
			else:
				print("Skipping link " + links[0])
		if ((self.replyrate>random.randint(1,99)) or ((self.nickreplyrate>random.randint(1,99)) and (own_nick in msg[0]))):
			exist_words_q = "SELECT word1, word2 FROM contexts WHERE instr(?, word2) > 0"
			exist_words = []
			for word in self.c.execute(exist_words_q, msg).fetchall():
				if word[1] in msg[0].split():
					exist_words.append(word)
			if exist_words:
				currentword = exist_words[random.randint(0,len(exist_words)-1)][0]
				while currentword != None:
					print(currentword, end=" ",flush=True)
					exist_words_q = "SELECT * FROM contexts WHERE word1 LIKE ? ORDER BY freq ASC"
					next_words = self.c.execute(exist_words_q, [currentword]).fetchall()
					total_contexts = 0
					for word in next_words:
						total_contexts += int(word[2])
					selection = random.randint(0, int(total_contexts))
					newword = None
					for word in next_words:
						selection -= int(word[2])
						if selection < 0 and newword == None:
							newword = word[1]
					if newword != currentword:
						phrase += currentword + " "
					currentword = newword
					self.db.commit()
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
			wordcount = 0
			contextcount = 0
			linecount = 0
			print("Learning...")
			self.send(e.target, "Learning")
			for line in text:
				links = re.findall(r'(https?://\S+)', line)
				if not links:
					exist_words = self.c.execute("SELECT word1, word2 FROM contexts WHERE instr(?, word1) > 0", [line]).fetchall()
					words = line.split()
					for word1, word2 in zip(words[:-1], words[1:]):
						if (word1, word2) in exist_words:
							self.c.execute("UPDATE contexts SET freq = freq + 1 WHERE word1=? AND word2=?", (word1, word2))
							contextcount += 1
						else:
							self.c.execute("INSERT INTO contexts VALUES (?, ?, 1)", (word1, word2))
							wordcount += 1
							contextcount += 1
					if len(words)!=0:
						if (words[-1], None) in exist_words:
							self.c.execute("UPDATE contexts SET freq = freq + 1 WHERE word1=? AND word2=?", (words[-1], None))
							contextcount += 1
						else:
							self.c.execute("INSERT INTO contexts VALUES (?, ?, 1)", (words[-1], None))
							wordcount += 1
							contextcount += 1
					linecount += 1
					if ((wordcount%100)==0):
						print("+", end="",flush=True)
					if ((contextcount%100)==0):
						print(".", end="",flush=True)
					if ((linecount%1000)==0):
						print(str(linecount/1000).split(".")[0] + "k", end="",flush=True)
				
			print("Learned " + str(wordcount) + " new words and " + str(contextcount) + " new contexts")
			self.send(e.target, "Learned " + str(wordcount) + " new words and " + str(contextcount) + " new contexts")
			self.db.commit()
			print("Commited to DB file")
	def on_privmsg(self, c, e):
		pass
	def shutdown(self):
		self.db.close()