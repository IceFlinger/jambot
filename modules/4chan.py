from jambot import botModule
import sys
import requests
import threading
import time
import random
import math
import re
import string
import html.parser
#4chan module for jambot
#Requires markov module to be loaded for learning functions to work
def mangle_line(line):
	line = ' '.join(w for w in line.split() if not len(w)>26) #Remove long stuff
	f = string.ascii_letters + string.digits + "():<>[].,!?/-^%$#@ "
	line = ''.join(c for c in line if c in f) #Filter whole string with f chars
	return line

class moduleClass(botModule):
	def init_settings(self):
		self.set("check_timer", 300)
		self.set("learning_boards", "vg")
		self.set("thread_filter", "srg")

	def on_start(self, c, e):
		self.learning_boards = []
		if self.get("learning_boards").split() and "markov" in self.bot.get("modules"):
			for board in self.get("learning_boards").split():
				self.learning_boards.append([board, 0]) #learning boards only load on init, changes to settings won't affect them
		else:
			print("You need to load the markov module to learn from 4chan boards.")
		if self.get("check_timer") > 0:
			self.learn_schedule(self.get("check_timer"))

	def thread_learning(self, threadno, board, minpost = 0):
		try:
			if (threadno != 0):
				newmin = minpost
				threadrequest = 'http://a.4cdn.org/' + board + '/thread/' + str(threadno) + '.json'
				r = requests.get(threadrequest) 
				jason = r.json()
				for idx, val in enumerate(jason['posts']):
					post = jason['posts'][idx]
					if ('com' in post) and (post["no"] > minpost):
						newpost = post['com']
						lines = newpost.split('<br>')
						for text in lines:
							regexstring = '<[^<]+?>|\&gt\;\&gt\;\d*|https?://[^ ]*'
							text = re.sub(regexstring, '', text) 
							text = html.parser.HTMLParser().unescape(text)
							text = mangle_line(str(text))
							words = text.split()
							if len(words)!=0:
								self.db_query("INSERT OR IGNORE INTO contexts (word2) VALUES (?)", (words[0], ))
								self.db_query("UPDATE contexts SET freq = freq + 1 WHERE word2=? AND word1 is ''", (words[-1], ))
								self.db_commit()
							for word1, word2 in zip(words[:-1], words[1:]):
								self.db_query("INSERT OR IGNORE INTO contexts (word1, word2) VALUES (?, ?)", (word1, word2))
								self.db_query("UPDATE contexts SET freq = freq + 1 WHERE word1=? AND word2=?", (word1, word2))
								self.db_commit()
							if len(words)!=0:
								self.db_query("INSERT OR IGNORE INTO contexts (word1) VALUES (?)", (words[-1], ))
								self.db_query("UPDATE contexts SET freq = freq + 1 WHERE word1=? AND word2 is ''", (words[-1], ))
						if post["no"] > newmin:
								newmin = post["no"]
				self.db_commit()
				return newmin
		except:
			for error in sys.exc_info():
				print(str(error))
		return minpost
		
	def board_learning(self, restart_timer = True, boards = [], threadfilter = ""):
		try:
			filter = threadfilter
			if restart_timer:
				filter = self.get("thread_filter")
				boards = self.learning_boards
			for board in boards:
				boardrequest = 'http://a.4cdn.org/' + board[0] + '/catalog.json'
				r = requests.get(boardrequest)
				jason = r.json()
				newmin = 0
				for idx, val in reversed(list(enumerate(jason))):
					for idx2, val2 in reversed(list(enumerate(jason[idx]['threads']))):
						thread = jason[idx]['threads'][idx2]
						maxpost = 0
						if filter == "":
							threadnum = thread['no']
							print(str(time.time()) + ": Learning from /" + board[0] + "/ page " + str(idx+1) + " thread " + str(idx2+1) + ", ID = " + str(threadnum) + " (%" + str(int((math.fabs(((float(idx)*15)+(float(idx2+1)))-150)/150)*100)) + " done)")
							maxpost = self.thread_learning(threadnum, board[0], board[1])
						else:
							try:
								if filter in thread['sub']:
									threadnum = thread['no']
									print(str(time.time()) + ": Learning from /" + board[0] + "/ page " + str(idx+1) + " thread " + str(idx2+1) + ", ID = " + str(threadnum) + " (%" + str(int((math.fabs(((float(idx)*15)+(float(idx2+1)))-150)/150)*100)) + " done)")
									maxpost = self.thread_learning(threadnum, board[0], board[1])
							except:
								print(str(time.time()) + ": Skipped /" + board[0] + "/ page " + str(idx+1) + " thread " + str(idx2+1) + ", ID = " + str(threadnum) + "(missing subject with filter on) (%" + str(int((math.fabs(((float(idx)*15)+(float(idx2+1)))-150)/150)*100)) + " done)")
						if maxpost > newmin:
							newmin = maxpost
				if restart_timer:
					board[1] = newmin
			print(str(time.time()) + ": Finished learning!")
		except:
			for error in sys.exc_info():
				print(str(error))

	def feed_board(self, chan, boards, filter):
		words = self.db_query("SELECT COUNT(*) FROM (SELECT DISTINCT LOWER(word1) FROM contexts)")[0][0]
		contexts = self.db_query("SELECT sum(freq) FROM contexts")[0][0]
		self.send(chan, "Had " + str(words) + " words and " + str(contexts)  + " contexts.")
		self.board_learning(False, boards, filter)
		words = self.db_query("SELECT COUNT(*) FROM (SELECT DISTINCT LOWER(word1) FROM contexts)")[0][0]
		contexts = self.db_query("SELECT sum(freq) FROM contexts")[0][0]
		boardstring = ""
		for board in boards:
			boardstring += "/" + board[0] + "/ "
		self.send(chan, "Finished learning from " + boardstring)
		self.send(chan, "Now have " + str(words) + " words and " + str(contexts)  + " contexts.")

	def feed_thread(self, chan, board, thread):
		words = self.db_query("SELECT COUNT(*) FROM (SELECT DISTINCT LOWER(word1) FROM contexts)")[0][0]
		contexts = self.db_query("SELECT sum(freq) FROM contexts")[0][0]
		self.send(chan, "Had " + str(words) + " words and " + str(contexts)  + " contexts.")
		self.thread_learning(board, thread)
		words = self.db_query("SELECT COUNT(*) FROM (SELECT DISTINCT LOWER(word1) FROM contexts)")[0][0]
		contexts = self.db_query("SELECT sum(freq) FROM contexts")[0][0]
		self.send(chan, "Finished learning from /" + board + "/" + thread)
		self.send(chan, "Now have " + str(words) + " words and " + str(contexts)  + " contexts.")

	def do_command(self, c, e, command, args, admin):
		#Need to add thread searching so this module isn't just a tumor of markov
		if command=="feedboard" and (("markov" in self.bot.get("modules")) and admin):
			if args:
				boardcount = 0
				for arg in args:
					if arg[0]!="/" or arg[-1]!="/":
						break
					boardcount += 1
				else:
					pass
				boards = []
				if boardcount > 0:
					for board in args[0:boardcount]:
						boards.append([board.split('/')[1], 0])
				else:
					for board in self.get("learning_boards").split():
						boards.append([board, 0])
				t = threading.Thread(target=self.feed_board, args=(e.target, boards, ' '.join(args[boardcount:])))
				t.daemon = True
				t.start()
			else:
				t = threading.Thread(target=self.feed_board, args=(e.target, ([board, 0] for board in self.get("learning_boards").split), self.get("thread_filter")))
				t.daemon = True
				t.start()
		elif command=="feedthread" and (("markov" in self.bot.get("modules")) and admin):
			if len(args)==1 and len(args[0].split('/'))==3:
				t = threading.Thread(target=self.feed_thread, args=(e.target, args[0].split('/')[2], args[0].split('/')[1]))
				t.daemon = True
				t.start()
			else:
				self.send(e.target, "Format your thread like /board/threadnumber")

	def learn_schedule(self, checktimer):
		timer = threading.Timer(checktimer, self.learn_execute, ())
		timer.setDaemon(True)
		timer.start()

	def learn_execute(self):
		print("Starting board autolearn...")
		self.board_learning()
		print("Finished and restarting board autolearn.")
		self.learn_schedule(self.get("check_timer"))
