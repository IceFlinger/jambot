from jambot import botModule
import random
# rng module
class moduleClass(botModule):
	def do_command(self, c, e, command, args, admin):
		if command == "random":
			if not args:
				self.send(e.target, "One number to roll up to or two to roll in between")
			elif len(args) == 1:
				try:
					self.send(e.target, str(random.randint(1, int(args[0]))))
				except:
					self.send(e.target, "That's not a number")
			elif len(args) == 2:
				try:
					self.send(e.target, str(random.randint(int(args[0]), int(args[1]))))
				except:
					self.send(e.target, "Those aren't numbers")
		elif (command == "choose") and len(args)>1:
			try:
				choice = random.randint(0, len(args)-1)
				self.send(e.target, args[choice])
			except:
				self.send(e.target, "Couldn't choose for some reason")
		elif (command == "shuffle") and len(args)>1:
			try:
				random.shuffle(args)
				self.send(e.target, " ".join(args))
			except:
				self.send(e.target, "Couldn't shuffle for some reason")