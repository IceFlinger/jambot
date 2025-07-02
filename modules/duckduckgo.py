from jambot import botModule
import sys
import requests
#ffg module
class moduleClass(botModule):
	def help(command):
		if (command == "dg") or (command == "duck"):
			return "searches duck duck go and returns the top result for the query"
		return ""

	def init_settings(self):
		pass

	def on_start(self, c, e):
		pass

	def on_pubmsg(self, c, e):
		pass

	def on_send(self, chan, msg, modulename):
		pass

	def on_event(self, c, e):
		pass

	def do_command(self, c, e, command, args, admin):
		if (command == "dg") or (command == "duck"):
			if args:
				try:
					msg = ""
					query = ' '.join(args)
					s = requests.Session()
					search = s.get("https://api.duckduckgo.com/",
						params={
							"format": "json",
							"q": query
						})
					results = search.json()
					msg = results[0]["Heading"] + ": " + results[0]["AbstractText"][:40] + "... " + results[0]["AbstractURL"]
					self.send(e.target, msg)
				except:
					msg = "Problem ducking that"
					self.send(e.target, msg)
					for error in sys.exc_info():
						print(str(error))
					pass
			else:
				self.send(e.target, "Please say what to search for.")

	def on_privmsg(self, c, e):
		pass

	def on_shutdown(self):
		pass