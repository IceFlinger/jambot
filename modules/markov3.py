from jambot import botModule
from random import choice
import pycurl
import sys
import random
import re
import time
import string
import threading
import math

from io import BytesIO
#Markov chain jambot module
#By ice at irc.kickinrad.tv

def mangle_line(line):
	links = re.findall(r'(https?://\S+)', line) 
	f = string.ascii_letters + string.digits + "():<>[].,!?/-^%$#@ "
	line = ' '.join(w for w in line.split() if w not in links) #Remove URLs
	line = ' '.join(w for w in line.split() if w[0] not in "[\"(") #Remove timestamp type stuff and quotes
	line = ' '.join(w for w in line.split() if w[-1] not in "\;\"%") #Remove broken words
	line = ' '.join(w for w in line.split() if w[-1]!=">" and w[0]!="<") #Remove nick tags
	line = ' '.join(w for w in line.split() if not len(w)>26) #Remove long stuff
	line = ''.join(c for c in line if c in f) #Filter whole string with f chars
	return line

class moduleClass(botModule):
	dbload = True

	def init_settings(self):
		self.set("replyrate", 0.01, "Percentage rate for randomly replying to messages, 0-1")
		self.set("learning", False, "Learn new words from IRC channels joined")
		self.set("nickreplyrate", 1, "Percentage rate to reply when own nick is mentioned")
		self.set("maxchain", 20, "Maximum length of generated sentences")
		self.set("sanity", 50, "0-100 tuning value for context selection (0=absurd, 100=boring)")
		self.set("nicklesschans", "#discord", "Don't mention user nicks in these channels") #relay bot safety
		self.set("cooldown", 2, "Cooldown in seconds before able to generate another reply")
		self.set("altnick", "jambot", "Respond to an alternate nickname as if it was our own")
		self.set("bridged", False, "Name fixes for discord bridged mode")

	def help(command):
		if (command == "words"):
			return "shows a count of words known by markov module"
		elif (command == "known"):
			return "usage: known <word> ; shows number of known contexts for specific word"
		return ""

	def on_start(self, c, e):
		self.nickreply = False
		self.lastmsg = 0

	def on_load_db(self):
		self.db_query("CREATE TABLE IF NOT EXISTS contexts3 (word1 text DEFAULT '', word2 text DEFAULT '', word3 text DEFAULT '', freq int DEFAULT 0, UNIQUE(word1, word2, word3))")
		self.db_commit()

	def select_context(self, contexts):
		newpairs = {}
		for pair in contexts:
			key = (pair[0].lower(), pair[1].lower())
			if key in newpairs:
				newpairs[key] += pair[2]
			else:
				newpairs[key] = pair[2]
		#print(newpairs)
		sort = sorted(newpairs, key=newpairs.get, reverse=True)
		for pair in sort:
			roll = random.randint(1,100)
			if roll <= self.get("sanity"):
				return pair
		return sort[-1]

	def single_word_contexts(self, word):
		exist_contexts = []
		single_contexts = []
		for context in self.db_query("SELECT word1, word2, word3, freq FROM contexts3 WHERE (LOWER(word1) LIKE LOWER(?) OR LOWER(word2) LIKE LOWER(?) OR LOWER(word3) LIKE LOWER(?)) GROUP BY word1, word2, word3 ORDER BY sum(freq) DESC", (word, word, word)):
			single_contexts.append(context)
		for context in single_contexts:
			if context[0].lower() == word.lower() or context[1].lower() == word.lower():
				exist_contexts.append((context[0], context[1], context[3]))
			if context[1].lower() == word.lower() or context[2].lower() == word.lower():
				exist_contexts.append((context[1], context[2], context[3]))
		return exist_contexts

	def build_sentence(self, c, e, msg, sender):
		phrase = []
		try:
			chainlength = 0
			exist_contexts = [] #look for words in the trigger sentence that we know already
			words = msg.split()
			own_nick = c.nickname
			if self.get("altnick") in msg.lower():
				own_nick = self.get("altnick")
			for i in range(len(words)):
				if words[i].lower() == own_nick.lower():
					words[i] = "#nick"
			if len(words) == 3 and words[0] == "#nick":
				for context in self.db_query("SELECT word1, word2, freq FROM contexts3 WHERE (LOWER(word1) LIKE LOWER(?) AND LOWER(word2) LIKE LOWER(?)) GROUP BY word1, word2 ORDER BY sum(freq)", (words[1], words[2])):
					exist_contexts.append(context)
				for context in self.db_query("SELECT word2, word3, freq FROM contexts3 WHERE (LOWER(word2) LIKE LOWER(?) AND LOWER(word3) LIKE LOWER(?)) GROUP BY word2, word3 ORDER BY sum(freq)", (words[1], words[2])):
					exist_contexts.append(context)
				if len(exist_contexts) == 0: #we didn't find that exact pair's context, so check for each word individually
					exist_contexts+=self.single_word_contexts(words[1])
					exist_contexts+=self.single_word_contexts(words[2])
			elif len(words) == 2 and words[0] == "#nick":
				exist_contexts+=self.single_word_contexts(words[1])
			else:
				for word1, word2 in zip(words[:-1], words[1:]):
					#for context in self.db_query("SELECT * FROM contexts WHERE (LOWER(word1) LIKE LOWER(?) AND LOWER(word2) LIKE LOWER(?)) OR (LOWER(word2) LIKE LOWER(?) AND LOWER(word3) LIKE LOWER(?)) GROUP BY word1, word2, word3 ORDER BY sum(freq)", (word1, word2, word1, word2)):
					#	exist_contexts.append(context)
					for context in self.db_query("SELECT word1, word2, freq FROM contexts3 WHERE (LOWER(word1) LIKE LOWER(?) AND LOWER(word2) LIKE LOWER(?)) GROUP BY word1, word2 ORDER BY sum(freq)", (word1, word2)):
						exist_contexts.append(context)
					for context in self.db_query("SELECT word2, word3, freq FROM contexts3 WHERE (LOWER(word2) LIKE LOWER(?) AND LOWER(word3) LIKE LOWER(?)) GROUP BY word2, word3 ORDER BY sum(freq)", (word1, word2)):
						exist_contexts.append(context)
			if exist_contexts:
				phrase_seed = self.select_context(exist_contexts)
				#print(phrase_seed)
				if phrase_seed[0] == "#nick":
					phrase.append(sender)
				else:
					phrase.append(phrase_seed[0])
				if phrase_seed[1] == "#nick":
					phrase.append(sender)
				else:
					phrase.append(phrase_seed[1])
				current_pair = phrase_seed
				while current_pair[1] != None: #begin building sentence forewards from seed word
					next_contexts = self.db_query("SELECT * FROM contexts3 WHERE (LOWER(word1) LIKE LOWER(?)) AND (LOWER(word2) LIKE LOWER(?)) ORDER BY freq DESC", current_pair)
					if len(next_contexts) == 0:
						break
					next_link = next_contexts[-1]
					for context in next_contexts:
						roll = random.randint(1,100)
						if roll <= self.get("sanity"):
							next_link = context
					if next_link[2] == "#nick":
						phrase.append(sender)
					else:
						phrase.append(next_link[2])
					if len(phrase) > self.get("maxchain"):
						current_pair = (next_link[1], None)
					else:
						current_pair = (next_link[1], next_link[2])
				#print(phrase, end=" ",flush=True)
				current_pair = phrase_seed
				while current_pair[0] != None: #begin building sentence backwards from seed word
					next_contexts = self.db_query("SELECT * FROM contexts3 WHERE (LOWER(word2) LIKE LOWER(?)) AND (LOWER(word3) LIKE LOWER(?)) ORDER BY freq DESC", current_pair)
					if len(next_contexts) == 0:
						break
					next_link = next_contexts[-1]
					for context in next_contexts:
						roll = random.randint(1,100)
						if roll <= self.get("sanity"):
							next_link = context
					if next_link[0] == "#nick":
						phrase.insert(0, sender)
					else:
						phrase.insert(0, next_link[0])
					if len(phrase) > self.get("maxchain"):
						current_pair = (None, next_link[1])
					else:
						current_pair = (next_link[0], next_link[1])
		except:
			raise
		sentence = " ".join(phrase)
		if sentence[0] == " ":
			sentence = sentence[1:]
		if sentence != "":
			self.send(e.target, sentence)

	def learn_sentence(self, msg):
		try:
			#print(words)
			words = msg.split()
			if len(words)>2:
				named = False
				own_nick = self.bot.get("nickname")
				if self.get("altnick").lower() in msg.lower():
					own_nick = self.get("altnick")
				for word in range(len(words)):
					if words[word].lower() in own_nick.lower():
						named = True
						words[word]="#nick"
				index = 0
				if not (named and len(words)<5):
					if "jambot" in words:
						print(words)
						exit()
					if (len(words) > 3):
						self.db_query("INSERT OR IGNORE INTO contexts3 (word2, word3) VALUES (?, ?)", (words[0], words[1]))
						self.db_query("UPDATE contexts3 SET freq = freq + 1 WHERE word2=? AND word3=? AND word1 is ''", (words[0], words[1]))
					while index < len(words)-2:
						word1 = words[index]
						word2 = words[index+1]
						word3 = words[index+2]
						self.db_query("INSERT OR IGNORE INTO contexts3 (word1, word2, word3) VALUES (?, ?, ?)", (word1, word2, word3))
						self.db_query("UPDATE contexts3 SET freq = freq + 1 WHERE word1=? AND word2=? AND word3=?", (word1, word2, word3))
						index += 1
					if (len(words) > 3):
						self.db_query("INSERT OR IGNORE INTO contexts3 (word1, word2) VALUES (?, ?)", (words[-2], words[-1]))
						self.db_query("UPDATE contexts3 SET freq = freq + 1 WHERE word1=? AND word2=? AND word3 is ''", (words[-2], words[-1]))
		except:
			raise

	def on_pubmsg(self, c, e):
		msg = " "
		sender = ""
		thisbot = True
		lametrig = False
		if self.get("bridged"):
			try:
				msg_end = e.arguments[0].index(">")
				msg = mangle_line(e.arguments[0][msg_end:])
				sender = e.arguments[0][e.arguments[0].index("<")+4:e.arguments[0].index(">")-1]
			except:
				sender = self.bot.get("nickname")
				msg = " "
				thisbot = False
				pass
		else:
			msg = mangle_line(e.arguments[0])
			sender = e.source.nick
		own_nick = c.nickname
		if self.get("altnick") in msg.lower():
			own_nick = self.get("altnick")
		roll = self.get("replyrate")>random.random()
		nickroll = self.get("nickreplyrate")>random.random()
		named = (own_nick.lower() in msg.lower()) or (self.get("altnick").lower() in msg.lower())
		cooled = time.time()>(self.lastmsg+self.get("cooldown"))
		if (roll or (nickroll and named)) and cooled:
			#t = threading.Thread(target=self.build_sentence, args=(c, e, msg, sender))
			#t.daemon = True
			#t.start()
			self.build_sentence(c, e, msg, sender)
			self.lastmsg = time.time()
		if thisbot and self.get("learning") and not lametrig:
			try:
				self.learn_sentence(msg)
				self.db_commit()
			except:
				pass

	def on_send(self, chan, msg, modulename):
		pass

	def on_event(self, c, e):
		pass

	def do_command(self, c, e, command, args, admin):
		if command=="feed" and admin and args:
			print("Downloading: " + args[0])
			self.send(e.target, "Downloading: " + args[0])
			textbytes = BytesIO()
			try:
				textconn = pycurl.Curl()
				textconn.setopt(textconn.URL, args[0])
				textconn.setopt(textconn.WRITEDATA, textbytes)
				textconn.perform()
				textconn.close()
				text = textbytes.getvalue().decode('iso-8859-1').split('\n')
				linecount = 0
				print("Learning...")
				self.send(e.target, "Learning")
				try:
					multi = 1
					if len(args)>1:
						multi = int(args[1])
					for line in text:
						line = mangle_line(line)
						self.learn_sentence(line)
						linecount += 1
						if ((linecount%1000)==0):
							print(str(linecount/1000).split(".")[0] + "k lines, ", end="" , flush=True)
					self.db_commit()
				except:
					self.send(e.target, "Interrupted while learning from file (Something else accessing DB?)")
					raise
				try:
					print("Learned from " + str(linecount) + " lines")
					self.send(e.target, "Learned from " + str(linecount) + " lines")
					self.db_commit()
					print("Commited to DB")
				except:
					pass
			except:
				self.send(e.target, "Couldn't download file.")
				raise
		elif command=="words":
			words = self.db_query("SELECT COUNT(*) FROM (SELECT DISTINCT LOWER(word1) FROM contexts3)")[0][0]
			contexts = self.db_query("SELECT sum(freq) FROM contexts3")[0][0]
			self.send(e.target, "Currently have " + str(words) + " words and " + str(contexts)  + " contexts.")
		elif command=="known" and args:
			for word in args[:8]:
				contexts = self.db_query("SELECT sum(freq) FROM contexts3 WHERE LOWER(word1) LIKE LOWER(?) OR LOWER(word2) LIKE LOWER(?) OR LOWER(word3) LIKE LOWER(?)", (word, word, word))[0][0]
				if contexts != None:
					self.send(e.target, "I know " + word + " in " + str(contexts)  + " contexts.")
				else:
					self.send(e.target, "I don't know " + word)
		elif command=="clean" and admin:
			contexts = self.db_query("SELECT sum(freq) FROM contexts3")[0][0]
			self.send(e.target, "Used to have " + str(contexts)  + " contexts.")
			self.db_query("UPDATE contexts SET freq = cast((freq+1)/2 as int)")
			contexts = self.db_query("SELECT sum(freq) FROM contexts3")[0][0]
			self.db_commit()
			self.send(e.target, "Now have " + str(contexts)  + " contexts.")

	def on_privmsg(self, c, e):
		pass

	def shutdown(self):
		pass
