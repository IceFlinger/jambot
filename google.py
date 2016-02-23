from jambot import botModule
import sys
import requests
#Google module
#self.send(e.target, msg)
class moduleClass(botModule):
	def on_start(self):
		pass
	def on_pubmsg(self, c, e):
		pass
	def on_send(self, chan, msg, modulename):
		pass
	def on_event(self, c, e):
		pass
	def do_command(self, c, e, command, args, admin):
		if ((command == "g") or (command == "google")) and len(args) > 0:
			try:
				msg = ""
				g_api_key = self.settings["apikey"]
				search_engine_id = self.settings["search_engine_id"]
				query = ' '.join(args)
				s = requests.Session()
				search = s.get("https://www.googleapis.com/customsearch/v1",
					params={
						"alt": "json",
						"key": g_api_key,
						"cx": search_engine_id,
						"q": query
					})
				results = search.json()
				msg = results["items"][0]["title"] + ": " + results["items"][0]["snippet"][:40] + "... " + results["items"][0]["link"]
				self.send(e.target, msg)
			except:
				msg = "Problem googling that"
				self.send(e.target, msg)
				for error in sys.exc_info():
					print(str(error))
				pass
	def on_privmsg(self, c, e):
		pass