from jambot import botModule


# Quote module
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
        if (command == "say"):
            say = str.split(e.arguments[0], " ", maxsplit=1)
            self.send(e.target, say[1])

    def shutdown(self):
        pass
