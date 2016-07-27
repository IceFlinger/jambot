from jambot import botModule
import sys
import requests
import time
import math
from geopy.distance import vincenty
import threading
import cfscrape

pokedex = {
'1': 'Bulbasaur', '2': 'Ivysaur', '3': 'Venusaur', '4': 'Charmander', 
'5': 'Charmeleon', '6': 'Charizard', '7': 'Squirtle', '8': 'Wartortle', 
'9': 'Blastoise', '10': 'Caterpie', '11': 'Metapod', '12': 'Butterfree', 
'13': 'Weedle', '14': 'Kakuna', '15': 'Beedrill', '16': 'Pidgey', 
'17': 'Pidgeotto', '18': 'Pidgeot', '19': 'Rattata', '20': 'Raticate', 
'21': 'Spearow', '22': 'Fearow', '23': 'Ekans', '24': 'Arbok', 
'25': 'Pikachu', '26': 'Raichu', '27': 'Sandshrew', '28': 'Sandslash', 
'29': 'Nidoran♀', '30': 'Nidorina', '31': 'Nidoqueen', '32': 'Nidoran♂', 
'33': 'Nidorino', '34': 'Nidoking', '35': 'Clefairy', '36': 'Clefable', 
'37': 'Vulpix', '38': 'Ninetales', '39': 'Jigglypuff', '40': 'Wigglytuff', 
'41': 'Zubat', '42': 'Golbat', '43': 'Oddish', '44': 'Gloom', '45': 'Vileplume', 
'46': 'Paras', '47': 'Parasect', '48': 'Venonat', '49': 'Venomoth', 
'50': 'Diglett', '51': 'Dugtrio', '52': 'Meowth', '53': 'Persian', 
'54': 'Psyduck', '55': 'Golduck', '56': 'Mankey', '57': 'Primeape', 
'58': 'Growlithe', '59': 'Arcanine', '60': 'Poliwag', '61': 'Poliwhirl', 
'62': 'Poliwrath', '63': 'Abra', '64': 'Kadabra', '65': 'Alakazam', 
'66': 'Machop', '67': 'Machoke', '68': 'Machamp', '69': 'Bellsprout', 
'70': 'Weepinbell', '71': 'Victreebel', '72': 'Tentacool', '73': 'Tentacruel',
'74': 'Geodude', '75': 'Graveler', '76': 'Golem', '77': 'Ponyta', 
'78': 'Rapidash', '79': 'Slowpoke', '80': 'Slowbro', '81': 'Magnemite', 
'82': 'Magneton', '83': 'Farfetch\'d', '84': 'Doduo', '85': 'Dodrio', 
'86': 'Seel', '87': 'Dewgong', '88': 'Grimer', '89': 'Muk', '90': 'Shellder', 
'91': 'Cloyster', '92': 'Gastly', '93': 'Haunter', '94': 'Gengar', '95': 'Onix', 
'96': 'Drowzee', '97': 'Hypno', '98': 'Krabby', '99': 'Kingler', '100': 'Voltorb', 
'101': 'Electrode', '102': 'Exeggcute', '103': 'Exeggutor', '104': 'Cubone', 
'105': 'Marowak', '106': 'Hitmonlee', '107': 'Hitmonchan', '108': 'Lickitung', 
'109': 'Koffing', '110': 'Weezing', '111': 'Rhyhorn', '112': 'Rhydon', 
'113': 'Chansey', '114': 'Tangela', '115': 'Kangaskhan', '116': 'Horsea', 
'117': 'Seadra', '118': 'Goldeen', '119': 'Seaking', '120': 'Staryu', 
'121': 'Starmie', '122': 'Mr. Mime', '123': 'Scyther', '124': 'Jynx', 
'125': 'Electabuzz', '126': 'Magmar', '127': 'Pinsir', '128': 'Tauros', 
'129': 'Magikarp', '130': 'Gyarados', '131': 'Lapras', '132': 'Ditto', 
'133': 'Eevee', '134': 'Vaporeon', '135': 'Jolteon', '136': 'Flareon', 
'137': 'Porygon', '138': 'Omanyte', '139': 'Omastar', '140': 'Kabuto', 
'141': 'Kabutops', '142': 'Aerodactyl', '143': 'Snorlax', '144': 'Articuno', 
'145': 'Zapdos', '146': 'Moltres', '147': 'Dratini', '148': 'Dragonair', 
'149': 'Dragonite', '150': 'Mewtwo', '151': 'Mew' }

class moduleClass(botModule):
	def on_start(self, c, e):
		self.checktimer = int(self.settings["check_timer"])
		self.shitmons = self.settings["shitmons"].split()
		self.alert_chan = self.settings["alert_chan"]
		self.lat = self.settings["lat"]
		self.lon = self.settings["lon"]
		self.session = cfscrape.create_scraper()
		self.last_scan = []
		if self.checktimer > 0:
			self.search_schedule(self.checktimer)

	def sec2min(self, secs):
		mins = math.floor(secs/60)
		secs = str(math.floor(secs-(60*mins)))
		if len(secs) == 1:
			secs = "0" + secs
		return str(mins) + ":" + secs

	def search_pokemon(self, manual = False, chan = ""):
		pokelist = []
		alert = ""
		if manual:
			print("Manually scanning " + self.lat + "/" + self.lon + " at " + str(time.time()))
		else:
			print("Auto scanning " + self.lat + "/" + self.lon + " at " + str(time.time()))
			chan = self.alert_chan
		try:
			scan = self.session.get("https://pokevision.com/map/scan/" + self.lat + "/" + self.lon)
			datar = self.session.get("https://pokevision.com/map/data/" + self.lat + "/" + self.lon)
			data = datar.json()
			if data["status"] == "success":
				pokelist = data["pokemon"]
				self.last_scan = []
			else:
				alert = "Couldn't retrieve map data"
			index = 0
			for pokemon in pokelist:
				if not str(pokemon["pokemonId"]) in self.shitmons:
					self.last_scan.append(pokemon)
					anchor = (float(self.lat), float(self.lon))
					spotted = (pokemon["latitude"], pokemon["longitude"])
					distance = vincenty(anchor, spotted).meters
					msg = "{" + str(index) + "} " + pokedex[str(pokemon["pokemonId"])] + " " + self.sec2min(int(pokemon["expiration_time"])- time.time()) + " " + str(int(distance)) + "m | "
					index += 1
					alert += msg
			if index == 0 and manual:
				alert= "Nothing found (" + str(len(pokelist)) + " ignored)"
		except:
			for error in sys.exc_info():
				print(str(error))
		if manual and alert == "":
			alert= "Site possibly under maintenence"
		while len(alert) > 383:
			self.send(chan, alert[:383])
			alert = alert[384:]
		self.send(chan, alert)


	def do_command(self, c, e, command, args, admin):
		if command == "scan":
			self.search_pokemon(True, e.target)
		elif command == "locate" and args:
			try:
				self.send(e.target, ("https://google.ca/maps/place/" + str(self.last_scan[int(args[0])]["latitude"]) + "," + str(self.last_scan[int(args[0])]["longitude"])))
			except:
				self.send(e.target, "Incorrect index for last scan")
		elif command == "anchor" and args:
			try:
				newlat = float(args[0])
				newlon = float(args[1])
				self.lat = str(newlat)
				self.lon = str(newlon)
				self.send(e.target, "Set new anchor point to:")
				self.send(e.target, ("https://google.ca/maps/place/" + self.lat + "," + self.lon))
			except:
				q = "https://pokevision.com/map/lookup/" + "%20".join(args)
				try:
					lookupr = self.session.get(q)
					lookup = lookupr.json()
					if lookup["status"] == "success":
						self.lat = str(lookup["latitude"])
						self.lon = str(lookup["longitude"])
						self.send(e.target, "Set new anchor point to:")
						self.send(e.target, ("https://google.ca/maps/place/" + self.lat + "," + self.lon))
					elif lookup["status"] == "error":
						self.send(e.target, lookup["message"])
					else:
						self.send(e.target, "Something went wrong retrieving map data")
				except:
					for error in sys.exc_info():
						print(str(error))
					self.send(e.target, "Something went wrong retrieving map data")
		elif command == "anchor":
			self.send(e.target, ("https://google.ca/maps/place/" + self.lat + "," + self.lon))
		elif command == "shitmons" and args:
			try:
				selected = []
				invdex = {v: k for k, v in pokedex.items()} #magically invert pokedex dict to lookup names
				for arg in args:
					selected.append(invdex[arg])
				for mon in selected:
					if mon in self.shitmons:
						self.shitmons.remove(mon)
					else:
						self.shitmons.append(mon)
				shitmons = ""
				for shitmon in self.shitmons:
					shitmons += pokedex[shitmon] + " "
				self.send(e.target, "Now ignoring: " + shitmons)
			except:
				self.send(e.target, "Couldn't recognize some pokemon")
		elif command == "shitmons":
			shitmons = ""
			for shitmon in self.shitmons:
				shitmons += pokedex[shitmon] + " "
			self.send(e.target, "Currently ignoring: " + shitmons)

	def search_schedule(self, checktimer):
		timer = threading.Timer(checktimer, self.search_execute, ())
		timer.setDaemon(True)
		timer.start()

	def search_execute(self):
		print("Searching for pokemon...")
		self.search_pokemon()
		print("Finished and restarting search timer.")
		self.search_schedule(self.checktimer)
