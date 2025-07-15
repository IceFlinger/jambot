from jambot import botModule
import logging
#Monitor Module
class moduleClass(botModule):
	def init_settings(self):
		self.logger = logging.getLogger("jambot.monitor")

	def on_start(self, c, e):
		pass

	def on_pubmsg(self, c, e):
		logging.info("Public msg:")
		logging.info(vars(e))

	def on_send(self, chan, msg, modulename):
		logging.info("Sent msg to " + chan + " from " + modulename + ":")
		logging.info(msg)

	def on_event(self, c, e):
		logging.info("Channel Event:")
		logging.info(vars(e))

	def do_command(self, c, e, command, args, admin):
		logging.info("Command Event:")
		logging.info(vars(e))

	def on_privmsg(self, c, e):
		logging.info("Private Event:")
		logging.info(vars(e))

	def on_shutdown(self):
		logging.info("Shutting down...")
