from swampbot import botModule
import requests
from urllib.parse import urlparse
import re
import sys

#Youtube module

def video_id(value):
	"""
	Examples:
	- http://youtu.be/SA2iWivDJiE
	- http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
	- http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
	"""
	query = urlparse(value)
	if query.hostname == 'youtu.be':
		return query.path[1:]
	if query.hostname in ('www.youtube.com', 'youtube.com'):
		if query.path == '/watch':
			p = query.query
			return p[p.find("v=")+2:p.find("v=")+13]
		if query.path[:3] == '/v/':
			return query.path.split('/')[2]
	# fail?
	return None

class moduleClass(botModule):
	def do_command(self, c, e, command, args, admin):
		if ((command == "yt") or (command == "youtube")) and len(args) > 0:
			try:
				msg = ""
				g_api_key = self.settings["apikey"]
				query = ' '.join(args)
				s = requests.Session()
				search = s.get("https://www.googleapis.com/youtube/v3/search",
					params={
						"part": "snippet",
						"key": g_api_key,
						"q": query
					})
				results = search.json()
				videoId = results["items"][0]["id"]["videoId"]
				video_title = results["items"][0]["snippet"]["title"]
				channel_name = results["items"][0]["snippet"]["channelTitle"]
				search = s.get("https://www.googleapis.com/youtube/v3/videos",
					params={
						"part": "contentDetails,statistics",
						"key": g_api_key,
						"id": videoId
					})
				results = search.json()
				video_length = ''.join(results["items"][0]["contentDetails"]["duration"][2:])
				video_views = results["items"][0]["statistics"]["viewCount"]
				msg = video_title + ": by " + channel_name + ", (" + video_length.lower() + ") " + video_views + " views http://youtu.be/" + videoId
				#msg = msg.encode('ascii', 'ignore')
				self.send(e.target, msg)
			except:
				self.send(e.target, "Problem youtubing that")
				for error in sys.exc_info():
					print(str(error))
				pass
	def on_pubmsg(self, c, e):
		links = re.findall(r'(https?://\S+)', e.arguments[0])
		
		try:
			for link in links:
				if ('youtube' in link) or ('youtu.be' in link):
					videoId = video_id(link)
					g_api_key = self.settings["apikey"]
					s = requests.Session()
					search = s.get("https://www.googleapis.com/youtube/v3/videos",
						params={
							"part": "snippet,contentDetails,statistics",
							"key": g_api_key,
							"id": videoId
						})
					results = search.json()
					video_title = results["items"][0]["snippet"]["title"]
					channel_name = results["items"][0]["snippet"]["channelTitle"]
					video_length = ''.join(results["items"][0]["contentDetails"]["duration"][2:])
					video_views = results["items"][0]["statistics"]["viewCount"]
					msg = video_title + ": by " + channel_name + ", (" + video_length.lower() + ") " + video_views + " views http://youtu.be/" + videoId
					#msg = msg.encode('ascii', 'ignore')
					self.send(e.target, msg)
		except:
			pass
