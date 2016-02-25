from jambot import botModule
import sqlite3


# Quote module
class moduleClass(botModule):
    def on_start(self):
        self.conn = sqlite3.connect(self.settings["database"])
        self.cql = self.conn.cursor()
        self.buffernick = 'wew'
        self.buffermsg = 'wew'
        self.cql.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='quotes'")
        result = self.cql.fetchone()
        if result:
            pass
        else:
            self.cql.execute("CREATE TABLE quotes (nick text, quote text)")

    pass

    def on_pubmsg(self, c, e):
        self.buffernick = e.source.nick
        self.buffermsg = e.arguments[0]
        pass

    def on_send(self, chan, msg, modulename):
        pass

    def on_event(self, c, e):
        if (e.type == "action"):
            self.buffernick = e.source.nick
            self.buffermsg = "/me " + e.arguments[0]
        pass

    def do_command(self, c, e, command, args, admin):
        if (command == "addquote"):
            if self.buffernick and self.buffermsg == 'wew':
                self.send(e.target, "No quote stored")
            elif self.buffermsg == '!quote':
                self.send(e.target, "No quote stored")
            else:
                quote = (self.buffernick, self.buffermsg)
                self.cql.execute("INSERT INTO quotes VALUES (?,?)", quote)
                self.conn.commit()
                msg = "Added quote: " + quote[0] + ": " + quote[1]
                self.send(e.target, msg)

        elif ((command == "q") or (command == "quote")):
            self.cql.execute('SELECT * FROM quotes ORDER BY RANDOM() LIMIT 1')
            msg = self.cql.fetchone()
            msg = "Quote: " + msg[0] + ": " + msg[1]
            self.send(e.target, msg)
        pass

    def shutdown(self):
        self.conn.close()
