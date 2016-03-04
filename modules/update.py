import git
import os
import time
from jambot import botModule


# Git update check module
# Updating coming next revision

class moduleClass(botModule):
    def on_start(self, c, e):
        self.dir = os.getcwd()
        repo = git.Repo(self.dir)
        assert not repo.bare
        update_notified = 0
        while True:
            commits = repo.iter_commits('master..origin/master')
            count = sum(1 for commit in commits)
            if update_notified != 1:
                print("git check")
                if count >= 1:
                    self.send(e.target, "Update available for jambot!")
                    update_notified = 1
                else:
                    print("no update available")
                    time.sleep(60)
            else:
                print("git update already notified, pass")
                pass
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
        pass

    def shutdown(self):
        pass
