# jambot

Jambot is an irc bot useful for loading different sets of features through modules. When run, a config file can be supplied (or defaulted to jambot.cfg) that contains connection info and a list of modules to be loaded in as features from the /modules folder. Each module can have config options loaded through the same config file, access to a shared SQLite db, and ability to control actions of the bot. 

Required settings to load in the config file:

	[jambot]
	# List of modules to load (seperated by spaces)
	modules = markov 4chan twittertools flags youtube quote tag google urbandict sample rng g8r nickserv monitor say alert
	# Name of database file to use if required by modules #
	database        = jambot.db
	# List of channels to join (seperated by spaces)
	channels        = #test
	# Bot's nickname #
	nickname        = jambot
	# Bot's real name #
	realname        = jambot
	# Server to connect to
	serverhost      = irc.kickinrad.tv
	# Server port
	serverport      = 6697
	# Server password (Blank = none)
	serverpass      =
	# Try and connect with SSL
	ssl     = True
	# Character to trigger commands
	command_prefix  = !
	# Hosts for whom bot will respond to owner commands (seperated by spaces)
	owner_hosts     = loud.house
	# String to help identify config of bot
	version = jambot 2.0

Module config options are described in the modules themselves, as well as in the default jambot.cfg and loaded into the config file with the modules themselves

Regular bot commands:

	Admin commands:
	join #channel: join the specified channel
	part #channel: part the specified channel
	nick nickname: change the bot's nick to nickname
	setprefix !: change the configured command prefix to the specified character
	quit: Disconnect from server and shutdown bot
	set module setting value: Change the 'setting' of 'module' to a new 'value'\
	reset module: reload the config settings for 'module' from the config file
	reset: reload all settings
	save: save all current module settings back to config file

	Regular commands:
	version: print the version string from the config file
	set module setting: query for the current 'setting' of 'module'
	modules: list currently loaded modules

	Commands not caught by these are passed onto every module to be processed

Most of the module API is shown off in the sample.py module:
```python
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
```
All of the module methods are optional and don't need to be defined if they aren't used. For starting a new module, there's the skeleton blank.py to build from:
```python
from jambot import botModule

class moduleClass(botModule):
	#dbload = True
	def init_settings(self):
		pass

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
```

Finally, an outline of some of the existing modules and how they work:

	markov: Learn words from chatter and reply with its own built sentences. Feed a txt file from the web 
	in with the 'feed url' command, check for word count with 'words', check if a word is learned with 
	'known word', or 'clean' the current database so words learned afterwords pop up more

	4chan: Extension of the markov module, use 4chan boards and threads as a word bank for learning markov
	 phrases. Either configured to scan regularly with config settings, or fed an entire board with 
	 'feedboard /vg/ filter', or a specific thread with 'feedthread /board/threadnumber'

	alert: enables 'alert' command which highlights every single person in the channel. only load if 
	you're sure people won't be annoyed.

	cron: schedule other commands to run at scheduled times formatted like cron jobs. formatted as 
	either * for all values, or a comma-seperated list of possible values, ordered like 
	'minute[0-59] hour[0-23] day[1-31] month[1-12] weekday[0-6]'. Jobs are added with 
	'addcron (scheduled time) #channel command args', and can be any commands from other modules. 
	List current jobs with 'listcron' and delete them with 'delcron index'. All cron commands are admin only, 
	and executed as if the bot sent them itself, meaning if the bot's own host is configured as admin, 
	commands will be admin as well.

	flags: Image uploader and resizer. Assumes bot is running on same server as a configured webserver, 
	can save images from url to a local folder and return a url of the new image. Options exist in the 
	config for resizing the image, accepting certain orientations, or adding a border. Images are added
	 by anyone with 'flag url', or running just 'flags' scans the configured web folder for links to 
	 images and returns one at random.

	g8r: funny meme g8r just use 'g8r' command and eat people

	google: Configure proper API keys from google in the config file and use 'g query' command to search 
	google and return results in channel

	monitor: useful for debugging only, dumps e event objects into console as they're recieved

	nickserv: configure a password in config file to automatically register/sign in with nickserv on 
	given server

	rng: useful randomization tools, 'random 0 10' to roll integers between specified values, 
	'choose one two' to randomly select one of many supplied args, or 'shuffle one two' to 
	return the list of args randomly shuffled around.

	sample: described above, simply demos some features of the module api

	say: 'say whatever' command simply echos whatever is supplied as args

	quote: Remember funny stuff that people say. use 'addquote nickname' to add the last thing nickname 
	said into quotes, and use 'q' or 'quote' to retrieve one at random

	tag: custom static command module, arbitrary words can be made into commands with 'tag name data', 
	and later retrieved with just 'name' as a command itself. Useful for storing URLs or images with 
	certain aliases. A txt file to dump saved tags to can be configured in config similar to the folder 
	used for the flags module. Tags can be deleted by admins with 'deltag tagname'. 
	(todo: optionally admin-protect flags i guess)

	twitch: Monitor a list of twitch streamers, announce when they go live or check who's currently
	 live with 'streams', and count minutes bot has tracked stream live (for fun). Check who's 
	 currently tracked and their time with 'liststreams', or admins can 'addstream channelname' 
	 and 'delstream channelname'

	twittertools: Can use twitter API keys to access its own twitter account. Optionally dump timeline
	 as it updates to a specified channel, or admins can write tweets with 'tweet whatever'. Originally
	  conceived as extension for markov module and has features reflecting this, can be configured to 
	  automatically tweet the last messaged generated by certain modules (ex markov) at specified intervals.

	urbandict: look up query on urbandictionary for definition with 'ud query' or 'urbandictionary query'

	youtube: Similar to google module and uses same API keys, search youtube for videos with 'yt query'. 
	Can also be set to parse youtube URLs and retrieve title info as they are pasted into channels.
