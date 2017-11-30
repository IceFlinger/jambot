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
		self.set("upload_delay", 300, "Delay between allowing flag uploads")
		self.set("local_folder", "/path/to/local/folder/", "local folder to store converted flags into (backend location of web folder)", True)
		self.set("save_unconverted", True, "Choose to save images in unconverted form as well")
		self.set("unconverted_folder", "/path/to/local/unconverted/folder/", "a folder to keep unconverted images in",True)
		self.set("web_folder", "https://your.domain/folder/", "Web prefix of where to retrieve uploaded images")
		self.set("max_filesize", 2097152, "Maximum filesize of uploaded files")
		self.set("resize", True, "Switch for resizing images before uploading")
		self.set("border", True, "Switch for adding a border to resized images")
		self.set("resize_width", 500, "Width of resized images")
		self.set("resize_height", 192, "Height of resized images")
		self.set("flag_logfile", "", "Local filepath for uploaded flag logs")
		self.set("border_size", 1, "Width of border to add to resized images if enabled")
		self.set("orent_check", "none", "set to 'long' or 'tall' to only accept images oriented that way")


	def on_start(self, c, e):
		self.last_update = 0

	def upload_flag(self, e, url):
		try:
			if self.get("web_folder") in url:
				self.send(e.target, "Don't reupload flags")
				raise
			r = requests.get(url, stream=True)
			size = 0
			ctt = io.BytesIO()
			for chunk in r.iter_content(2048):
				size += len(chunk)
				ctt.write(chunk)
				if size > self.get("max_filesize"):
					r.close()
					self.send(e.target, "That file is too big")
					raise
			content = ctt.getvalue()
			img_in = Image.open(io.BytesIO(content))
			hash = hashlib.md5()
			hash.update(content)
			i = hash.hexdigest()
			if img_in.format == "GIF" and not self.get("resize"):
				img_in.save(self.get("local_folder") + i + '.gif', 'GIF', save_all=True)
				self.send(e.target, self.get("web_folder") + i + ".gif")
			else:
				img_size = img_in.size
				if img_size[0] < img_size[1] and self.get("orent_check") == "long":
					self.output("That image isn't long", ("", source, target, c, e))
					raise
				elif img_size[0] > img_size[1] and self.get("orent_check") == "tall":
					self.output("That image isn't tall", ("", source, target, c, e))
					raise
				if self.get("save_unconverted"):
					img_in.save(self.get("unconverted_folder") + i + '.png', 'PNG')
				img_out = img_in
				if self.get("resize"):
					x = self.get("resize_width")
					y = self.get("resize_height")
					if self.get("border"):
						border = self.get("border_size")
						img_out = img_in.resize((x-(border*2),y-(border*2)), Image.ANTIALIAS)
						img_out = ImageOps.expand(img_out,border=border,fill='black')
					else:
						img_out = img_in.resize((x,y), Image.ANTIALIAS)
				img_out.save(self.get("local_folder") + i + '.png', 'PNG')
				self.send(e.target, self.get("web_folder") + i + ".png")
			if self.get("flag_logfile") != "":
				dump = open(self.get("flag_logfile"), "a")
				dump.write(str(time.time()) + "\t" + e.source.nick + "\t" + i + "\n")
				dump.close()
			return True
		except:
			self.send(e.target, "Problem flagging that")
			if debug:
				raise
			else:
				pass
		return False

	def do_command(self, c, e, command, args, admin):
		if command == "flag" and args and admin:
			self.upload_flag(e, args[0])
		elif command == "flag" and args and (time.time() > self.last_update + self.get("upload_delay")):
			if self.upload_flag(e, args[0]):
				self.last_update = time.time()
		elif command == "flag" and args:
			self.send(e.target, "Wait " + str(int((self.last_update + self.get("upload_delay")) - time.time())) + " seconds")
		elif command == "flag" and not args:
			r = requests.get(self.get("web_folder"))
			d = html.fromstring(r.content)
			imglist = d.xpath('//a[@href]/@href')
			imglist = imglist[5:] #first 4 links are random index shit, lazy way to skip (add check for image extension)
			id = random.randint(0,len(imglist)-1)
			self.send(e.target, self.get("web_folder") + imglist[id])
