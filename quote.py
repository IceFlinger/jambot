from jambot import botModule
#Quote module
class moduleClass(botModule):
    def on_start(self):
        global buffernick
        global buffermsg
        global radbuffer
        buffernick = 'wew'
        buffermsg = 'wew'
        radbuffer = 'wew'

    pass

    def on_pubmsg(self, c, e):
        global buffernick
        global buffermsg
        global radbuffer
        print('buffernick 1: ' + buffernick)
        print('buffermsg 1: ' + buffermsg)
        print(e)
        a = e.arguments[0].split("!", 1)
        if len(a) > 1:
            self.do_command(e, a[1].strip())
        buffernick = e.source.nick
        buffermsg = e.arguments[0]
        print('buffernick 2: ' + buffernick)
        print('buffermsg 2: ' + buffermsg)
        if e.source == 'Radbot!Radbot@krad-no7d07.house':
            radbuffer == e.arguments[0]
        return

    def on_send(self, chan, msg, modulename):
        pass

    def on_event(self, c, e):
        pass

    def do_command(self, c, e, command, args, admin):
        if ((command == "q") or (command == "quote")):
            global buffernick
            global buffermsg
            global radbuffer
            if buffernick and buffermsg == 'wew':
                self.send(e.target, "No quote stored")
            elif buffermsg == '!quote':
                self.send(e.target, "No quote stored")
            else:
                self.send(e.target, "Quote: " + buffernick + ": " + buffermsg)
        pass
