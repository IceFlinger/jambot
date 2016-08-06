from jambot import botModule
import sys
import requests
#Google module
class moduleClass(botModule):
	def help(command):
		if (command == "g") or (command == "google"):
			return "searches google and returns the top result for the query"
		return ""

	def init_settings(self):
		self.set("apikey", "", True)
		self.set("search_engine_id", "", True)

	def on_start(self, c, e):
		pass

	def on_pubmsg(self, c, e):
		pass

	def on_send(self, chan, msg, modulename):
		pass

	def on_event(self, c, e):
		pass

	def do_command(self, c, e, command, args, admin):
		if (command == "g") or (command == "google"):
			if args:
				try:
					msg = ""
					g_api_key = self.get("apikey")
					search_engine_id = self.get("search_engine_id")
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
			else:
				self.send(e.target, "Please say what to search for.")

	def on_privmsg(self, c, e):
		pass

	def on_shutdown(self):
		pass