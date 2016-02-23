from jambot import botModule
#Quote module
class moduleClass(botModule):
    def on_start(self):
        self.buffernick = 'wew'
        self.buffermsg = 'wew'
    pass

    def on_pubmsg(self, c, e):
        self.buffernick = e.source.nick
        self.buffermsg = e.arguments[0]
        pass

    def on_send(self, chan, msg, modulename):
        pass

    def on_event(self, c, e):
        pass

    def do_command(self, c, e, command, args, admin):
        if ((command == "q") or (command == "quote")):
            if self.buffernick and self.buffermsg == 'wew':
                self.send(e.target, "No quote stored")
            elif self.buffermsg == '!quote':
                self.send(e.target, "No quote stored")
            else:
                self.send(e.target, "Quote: " + self.buffernick + ": " + self.buffermsg)
        pass