import git
import os
import time
import threading
from jambot import botModule


# Git update check module
# Updating coming next revision

class moduleClass(botModule):
    def on_start(self, c, e):
        self.channels = []
        dir = os.getcwd()
        self.repo = git.Repo(dir)
        assert not self.repo.bare
        pass

    def on_load_db(self):
        pass

    def on_pubmsg(self, c, e):
        pass

    def on_send(self, chan, msg, modulename):
        pass

    def on_event(self, c, e):
        if e.source.split("!")[0] == c.nickname:
            if e.type == "join":
                self.channels.append(e.target)
            elif e.type == "part":
                self.channels.remove(e.target)

        self.update_notified = 0
        while True:
            self.repo.git.fetch()
            commits = self.repo.iter_commits('master..origin/master')
            count = sum(1 for c in commits)
            if self.update_notified != 1:
                print("git check")
                if count >= 1:
                    for channel in self.channels:
                        self.send(channel, "Update available for jambot!")
                    self.update_notified = 1
                else:
                    print("no update available")
                    threading.Thread.run(time.sleep(60))
            else:
                print("git update already notified, stop")
                return
        pass

    def do_command(self, c, e, command, args, admin):
        if (command == "updatecheck"):
            print("why")
            if self.update_notified == 1:
                self.send(e.target, "Update available for jambot!")
            elif self.update_notified == 0:
                self.send(e.target, "Jambot is up to date!")
            else:
                self.send(e.target, "You somehow broke the update module.")
        pass

    def shutdown(self):
        pass
