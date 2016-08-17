from jambot import botModule
#Small sample module
#self.send(chan, msg):
#self.db_query(statement, params)
#self.db_commit()
class moduleClass(botModule):
	dbload = False #Set this to True if this module uses DB access, so it only gets created/loaded when needed
	def init_settings(self):
		'''
		Configurable settings for your module are initialized here

		self.set(setting, value, desc = "", secret = False):
		setting: name of the config setting, put in the config file and changed with set command
		value: default initial value of this setting if not overwritten with the loaded config
		desc: optional description of what the setting does, saved to the config file as well
		secret: Pass true here if the setting contains sensitive data, such as an API key or password
				secret settings can only be accessed by an admin in a private message
		'''
		self.set("bool", False, "a regular boolean setting")
		self.set("secretbool", False, "a protected boolean setting", True)
		self.set("int", 3, "a regular integer setting")
		self.set("secretint", 4, "a protected integer setting", True)
		self.set("float", 3.23342, "a regular float setting")
		self.set("secretfloat", 4.34234, "a protected float setting",True)
		self.set("string", "default string", "a regular string setting")
		self.set("secretstring", "default secret string", "a protected string setting", True)
		#These values can later be retrieved with:
		# self.get(setting)
		# Anything initialized here can be changed on the fly with the main bot's 'set' command

	def on_start(self, c, e):
		self.local_var = 0 #non config based local vars get initialized on start
		self.last_msg = self.get("string") #Example of something to keep track of, initialized with configured setting if wanted

		#other useful things to do here include initializing timers and threads

	def on_load_db(self):
		#If dbload is set to True for this module, your db table can be created here
		self.db_query("CREATE TABLE IF NOT EXISTS sample (id INTEGER PRIMARY KEY ASC, name text UNIQUE NOT NULL, value INTEGER DEFAULT 0)")
		self.db_commit() #Required after every writing action to db
		#Regular SQL queries work from here on with self.db_query(), returns results in a list
		#Writing queries need to be followed by self.db_commit() or they won't be saved
		
	def do_command(self, c, e, command, args, admin):
		if command=="sample": #commands are checked without the configured prefix
			if admin: #admin is true if command was sent from someone with a host configured as admin
				self.say(e.target, "Hello admin " + e.source.nick)
				# send text to irc, self.say(channel, message)
				#useful stuff:
				# e: event object, contains info about recieved irc activity, monitor module is useful for debugging these
				# e.target: name of channel/person event was recieved from
				# e.source: full hostname of what/whoever sent the event
				# e.source.nick: just the nickname of the sender
			if args: #args returns false if empty
				argcount = len(args) #len() can count how many args we got
				self.say(e.target, "You sent " + str(argcount) + " args")
				sentargs = " ".join(args) #args are in a list that can be joined into a string if needed
				self.say(e.target, "Here are your args: " + sentargs)

	def on_send(self, chan, msg, modulename):
		#This hook is triggered whenever a module, including this one, uses self.send()
		if modulename != self.name: #self.name returns our own module name
			print("Module " + modulename + " sent message " + msg + " to channel " + chan)
			#Print statements are useful for console debugging

	def on_pubmsg(self, c, e):
		#This hook is triggered by any public channel message, e.target can be expected to be a public channel
		self.last_msg = e.arguments[0] #message is stored in e as a string in the first element of the arguments list (not sure why the extra array)

	def on_event(self, c, e):
		#This hook is triggered by any non-message where e.target can still be expected as a channel
		#Useful things include checking e.type for "join" or "part"
		if e.type == "join" and e.source.nick != c.nickname:
			# more useful stuff:
			# c: connection object, usually stays the same whole time bot is connected, contains info about... our connection
			# c.nickname: useful way to check our own nickname
			self.send(e.target, "Welcome to " + e.target + ", " + e.source.nick + "!")
			# simple greeting example of using events

	def on_privmsg(self, c, e):
		#This hook is triggered by any event where the bot itself is expected to be e.target (pings, privmsgs)
		if e.type == "privmsg":
			print("Secret from " + e.source.nick + ": " + e.arguments[0])

	def shutdown(self):
		#Run whenever the bot is shutdown, useful for closing opened files if needed (db is handled by main bot already)
		pass
