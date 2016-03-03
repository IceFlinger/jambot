from jambot import botModule


# Bark module
class moduleClass(botModule):
    def on_start(self, c, e):
        pass

    def on_load_db(self):
        pass

    def on_pubmsg(self, c, e):
        pass

    def on_send(self, chan, msg, modulename):
        pass

    def on_event(self, c, e):
        pass

    def do_command(self, c, e, command, args, admin):
        if (command == "bark"):
            self.send(e.target, "bark")

    def shutdown(self):
        pass
