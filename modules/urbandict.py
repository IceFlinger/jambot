from jambot import botModule
import sys
import requests
#Urban Dictionary search module.
class moduleClass(botModule):
	def do_command(self, c, e, command, args, admin):
		if command=="ud" or command=="urbandictionary":
			if args:
				try:
					msg = ""
					query = ' '.join(args)
					s = requests.Session()
					search = s.get("http://api.urbandictionary.com/v0/define",
						params={
							"term": query,
						})
					results = search.json()
					if results["result_type"]=="exact":
						msg = results["list"][0]["word"] + ": " + results["list"][0]["definition"][:395]
						msg = ''.join(msg.splitlines())
						self.send(e.target, msg)
						msg =  "Example: " + results["list"][0]["example"][:395]
						msg = ''.join(msg.splitlines())
						self.send(e.target, msg)
					else:
						msg = "Can't find that."
						self.send(e.target, msg)
				except:
					msg = "Problem looking for that"
					self.send(e.target, msg)
					for error in sys.exc_info():
						print(str(error))
					pass
			else:
				self.send(e.target, "Please say what to search for.")