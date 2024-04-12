#Empty py intended as a suggestion for a type of event a student could add. For ease of merging, students should append their names or other id to this py and any classes, to reduce conflicts.
from game import event
from game.player import Player
from game.context import Context
import game.config as config
import random
class fishies (Context, event.Event):
    def __init__ (self):
        super().__init__()
        self.name = "School of Fish"
        self.verbs['catch'] = self
        self.verbs['shoot'] = self
        self.verbs['ignore'] = self
        self.verbs['help'] = self
        self.result = {}
        self.go = False

    def process_verb (self, verb, cmd_list, nouns):
        if (verb == "catch"):
            self.go = True
            r = random.randint(1,10)
            if (r < 4):
                self.result["message"] = "you don't manage to catch any fish."
            else:
                c = random.choice(config.the_player.get_pirates())
                if (c.isLucky() == True):
                    self.result["message"] = "luckly, 30 food worth is caught."
                    config.the_player.ship.give_food(30)
                else:
                    self.result["message"] = c.get_name() + " catches 10 food worth."
                    config.the_player.ship.give_food(10)
        elif (verb == "shoot"):
            self.result["message"] = "You miss, what a waste. Cannon shot - 1!"
            config.the_player.CHARGE_SIZE -= 1
            self.go = True
        elif (verb == "ignore"):
            self.go = True

    def process (self, world):

        self.go = False
        self.result = {}
        self.result["newevents"] = [ self ]
        self.result["message"] = "default message"

        while (self.go == False):
            print (" A school of fish has appeared what do you want to do?")
            Player.get_interaction ([self])

        return self.result