from jambot import botModule


# Quote module
class moduleClass(botModule):
    dbload = True

    def on_start(self, c, e):
        self.buffer = dict()

    def on_load_db(self):
        self.db_query("CREATE TABLE IF NOT EXISTS quotes (nick text, quote text)")
        self.db_commit()

    def on_pubmsg(self, c, e):
        self.buffer.update({e.source.nick:e.arguments[0]})

    def on_send(self, chan, msg, modulename):
        self.buffer.update({self.bot.nickname:msg})

    def on_event(self, c, e):
        if (e.type == "action"):
            self.buffer.update({e.source.nick:"/me " + e.arguments[0]})

    def do_command(self, c, e, command, args, admin):
        if command == "addquote" and args:
            try:
                print(self.buffer[args[0]])
            except KeyError:
                self.send(e.target, "No quote stored")
                return

            if self.buffer[args[0]] == '!quote':
                self.send(e.target, "No quote stored")
            else:
                quote = (args[0], self.buffer.get(args[0]))
                self.db_query("INSERT INTO quotes VALUES (?,?)", quote)
                self.db_commit()
                msg = "Added quote: " + quote[0] + ": " + quote[1]
                self.send(e.target, msg)
                pass

        elif (command == "debug"):
                print(self.buffer)

        elif ((command == "q") or (command == "quote")):
            query = self.db_query('SELECT * FROM quotes ORDER BY RANDOM() LIMIT 1')[0]
            msg = "Quote: " + query[0] + ": " + query[1]
            self.send(e.target, msg)

        elif command == "delquote" and admin and args:
            pass

    def shutdown(self):
        pass