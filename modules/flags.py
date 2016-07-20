#!/usr/bin/env python
from jambot import botModule
import requests
from lxml import html
import random
import time
import hashlib
import io
from PIL import Image, ImageOps

class moduleClass(botModule):
	def on_start(self, c, e):
		self.last_update = 0
		self.upload_delay = int(self.settings["upload_delay"])
		self.local_folder = self.settings["local_folder"]
		self.unconverted_folder = self.settings["unconverted_folder"]
		self.web_folder = self.settings["web_folder"]
		self.max_filesize = int(self.settings["max_filesize"])

	def upload_flag(self, e, url):
		try:
			if self.web_folder in url:
				self.send(e.target, "Don't reupload flags")
				raise
			r = requests.get(url, stream=True)
			size = 0
			ctt = io.BytesIO()
			for chunk in r.iter_content(2048):
				size += len(chunk)
				ctt.write(chunk)
				if size > self.max_filesize:
					r.close()
					self.send(e.target, "That file is too big")
					raise
			content = ctt.getvalue()
			img_in = Image.open(io.BytesIO(content))
			img_size = img_in.size
			if img_size[0] < img_size[1]:
				self.output("That image isn't flag shaped", ("", source, target, c, e))
				raise
			hash = hashlib.md5()
			hash.update(content)
			i = hash.hexdigest()
			img_in.save(self.unconverted_folder + i + '.png', 'PNG')
			img_out = img_in.resize((498,190), Image.ANTIALIAS)
			img_out = ImageOps.expand(img_out,border=1,fill='black')
			img_out.save(self.local_folder + i + '.png', 'PNG')
			self.send(e.target, self.web_folder + i + ".png")
			return True
		except:
			self.send(e.target, "Problem flagging that")
			pass
		return False

	def do_command(self, c, e, command, args, admin):
		if command == "flag" and args and admin:
			self.upload_flag(e, args[0])
		elif command == "flag" and args and (time.time() > self.last_update + self.upload_delay):
			if self.upload_flag(e, args[0]):
				self.last_update = time.time()
		elif command == "flag" and args:
			self.send(e.target, "Wait " + str(int((self.last_update + self.upload_delay) - time.time())) + " seconds")
		elif command == "flag" and not args:
			r = requests.get(self.web_folder)
			d = html.fromstring(r.content)
			list = d.xpath('//a[@href]/@href')
			id = random.randint(0,len(list))
			self.send(e.target, self.web_folder + list[id])