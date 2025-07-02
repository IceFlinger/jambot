#!/usr/bin/env python
from jambot import botModule
import requests
from lxml import html
import random
import time
import hashlib
import io
from PIL import Image, ImageOps

debug = False

class moduleClass(botModule):
	def init_settings(self):
		self.set("web_folder", "https://your.domain/folder/", "Web prefix of where to retrieve uploaded images")
		self.set("cacheing", True, "Cache the image list until a new flag is uploaded")
		self.set("command", "flag", "Trigger word for this flag folder instance")

	def on_start(self, c, e):
		self.last_update = 0
		self.cached = False
		self.cached_list = []

	def do_command(self, c, e, command, args, admin):
		if command == self.get("command") and not args:
			if (not self.cached) or (not self.get("cacheing")):
				r = requests.get(self.get("web_folder"))
				d = html.fromstring(r.content)
				imglist = d.xpath('//a[@href]/@href')
				imglist = imglist[5:] #first 4 links are random index shit, lazy way to skip (add check for image extension)
				self.cached_list = imglist
				self.cached = True
			else:
				imglist  = self.cached_list
			id = random.randint(0,len(imglist)-1)
			self.send(e.target, self.get("web_folder") + imglist[id])
