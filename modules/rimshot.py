from jambot import botModule


# Rimshot module
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
        if (command == "rimshot"):
            self.send(e.target, "Badummm TIS!")

    def shutdown(self):
        pass
