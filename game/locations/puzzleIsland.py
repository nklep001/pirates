
from game import location
import game.config as config
from game.display import announce
from game.events import *
import game.items as items

class puzzleIsland (location.Location):

    def __init__ (self, x, y, w):
        super().__init__(x, y, w)
        self.name = "island"
        self.symbol = 'I'
        self.visitable = True
        self.starting_location = Beach_with_ship(self)
        self.locations = {}
        self.locations["beach"] = self.starting_location
        self.locations["trees"] = Trees(self)
        self.locations["tomb"] = Tomb(self)
        self.locations["battleground"] = battleground(self)

    def enter (self, ship):
        print ("arrived at an island")

    def visit (self):
        config.the_player.location = self.starting_location
        config.the_player.location.enter()
        super().visit()

class Beach_with_ship (location.SubLocation):
    def __init__ (self, m):
        super().__init__(m)
        self.name = "beach"
        self.verbs['north'] = self
        self.verbs['south'] = self
        self.verbs['east'] = self
        self.verbs['west'] = self
        self.event_chance = 50
        self.events.append (seagull.Seagull())
        self.events.append(drowned_pirates.DrownedPirates())

    def enter (self):
        announce ("arrive at the beach. Your ship is at anchor in a small bay to the south.")

    def process_verb (self, verb, cmd_list, nouns):
        if (verb == "south"):
            announce ("You return to your ship.")
            config.the_player.next_loc = config.the_player.ship
            config.the_player.visiting = False
        elif (verb == "north"):
            config.the_player.next_loc = self.main_location.locations["trees"]
        elif (verb == "east"):
            config.the_player.next_loc = self.main_location.locations["battleground"]
        elif (verb == "west"):
            config.the_player.next_loc = self.main_location.locations["tomb"]


class Trees (location.SubLocation):
    def __init__ (self, m):
        super().__init__(m)
        self.name = "trees"
        self.verbs['north'] = self
        self.verbs['south'] = self
        self.verbs['east'] = self
        self.verbs['west'] = self

        # Include a couple of items and the ability to pick them up, for demo purposes
        self.verbs['take'] = self
        self.item_in_tree = items.Cutlass()
        self.item_in_clothes = items.Flintlock()

        self.event_chance = 50
        self.events.append(man_eating_monkeys.ManEatingMonkeys())
        self.events.append(drowned_pirates.DrownedPirates())

    def enter (self):
        edibles = False
        for e in self.events:
            if isinstance(e, man_eating_monkeys.ManEatingMonkeys):
                edibles = True
        #The description has a base description, followed by variable components.
        description = "You walk into the small forest on the island."
        if edibles == False:
             description = description + " Nothing around here looks very edible."

        #Add a couple items as a demo. This is kinda awkward but students might want to complicated things.
        if self.item_in_tree != None:
            description = description + " You see a " + self.item_in_tree.name + " stuck in a tree."
        if self.item_in_clothes != None:
            description = description + " You see a " + self.item_in_clothes.name + " in a pile of shredded clothes on the forest floor."
        announce (description)

    def process_verb (self, verb, cmd_list, nouns):
        if (verb == "south" or verb == "north" or verb == "east" or verb == "west"):
            config.the_player.next_loc = self.main_location.locations["beach"]
        #Handle taking items. Demo both "take cutlass" and "take all"
        if verb == "take":
            if self.item_in_tree == None and self.item_in_clothes == None:
                announce ("You don't see anything to take.")
            elif len(cmd_list) > 1:
                at_least_one = False #Track if you pick up an item, print message if not.
                item = self.item_in_tree
                if item != None and (cmd_list[1] == item.name or cmd_list[1] == "all"):
                    announce ("You take the "+item.name+" from the tree.")
                    config.the_player.add_to_inventory([item])
                    self.item_in_tree = None
                    config.the_player.go = True
                    at_least_one = True
                item = self.item_in_clothes
                if item != None and (cmd_list[1] == item.name or cmd_list[1] == "all"):
                    announce ("You pick up the "+item.name+" out of the pile of clothes. ...It looks like someone was eaten here.")
                    config.the_player.add_to_inventory([item])
                    self.item_in_clothes = None
                    config.the_player.go = True
                    at_least_one = True
                if at_least_one == False:
                    announce ("You don't see one of those around.")

class Tomb (location.SubLocation):
    pillar_1_turns = 0
    pillar_2_turns = 0
    pillar_3_turns = 0
    gate_open = False

    def __init__(self, m):
        super().__init__(m)
        self.name = "tomb"
        self.verbs['north'] = self
        self.verbs['south'] = self
        self.verbs['east'] = self
        self.verbs['west'] = self
        self.verbs['enter'] = self

        self.verbs['turn'] = self
        self.verbs["look"] = self
        self.verbs["investigate"] = self
        self.verbs["search"] = self

        self.event_chance = 10
        self.events.append(man_eating_monkeys.ManEatingMonkeys())
        self.events.append(drowned_pirates.DrownedPirates())

    def enter(self):
        description = "You stumble upon a large stone entrance way carved into a small cliff."
        announce(description)
        announce("The entrance is blocked by a gate, and thhere are three pillars against the wall.\nThey look important, maybe you can turn them.")

    def process_verb(self, verb, cmd_list, nouns):
        if (verb == "south" or verb == "east"):
            config.the_player.next_loc = self.main_location.locations["beach"]
        elif (verb == "north" or verb == "west" or verb == "enter"):
            if self.gate_open != True:
                announce("A sturdy metal portcullas style gate blocks your path.")
            else:
                announce("You enter a chamber containing vast riches and wines, there is enough wine to last a long time.")
                config.the_player.ship.give_food(30)
        elif (verb == "look" or verb == "investigate" or verb == "search"):
            announce("Against the wall are three stone pillars each will an animal carved into each side.")
            announce("Above the iron gate is a carving of three more animals; A monkey, A dolphin, And a Bird of some kind.")
        elif (verb == "turn"):
            pillar = input("Which pillar do you want to turn? 1, 2, or 3: ")
            if pillar == "1":
                self.pillar_1_turns = (self.pillar_1_turns + 1)%3
                if self.pillar_1_turns == 1:
                    announce("The animal on this side of the pillar is a monkey")
                elif self.pillar_1_turns == 2:
                    announce("The animal on this side of the pillar is a dolphin")
                elif self.pillar_1_turns == 0:
                    announce("The animal on this side of the pillar is a bird")
            if pillar == "2":
                self.pillar_2_turns = (self.pillar_2_turns + 1)%3
                print(self.pillar_2_turns)
                if self.pillar_2_turns == 1:
                    announce("The animal on this side of the pillar is a bird")
                elif self.pillar_2_turns == 2:
                    announce("The animal on this side of the pillar is a dolphin")
                elif self.pillar_2_turns == 0:
                    announce("The animal on this side of the pillar is a monkey")
            if pillar == "3":
                self.pillar_3_turns = (self.pillar_3_turns + 1)%3
                if self.pillar_3_turns == 1:
                    announce("The animal on this side of the pillar is a bird")
                elif self.pillar_3_turns == 2:
                    announce("The animal on this side of the pillar is a monkey")
                elif self.pillar_3_turns == 0:
                    announce("The animal on this side of the pillar is a dolphin")
            if (self.pillar_1_turns == 1 and self.pillar_2_turns == 2 and self.pillar_3_turns == 1):
                self.gate_open = True
                announce("The iron gate rises from its stationary hold, away into the wall above it, out of view.")

class battleground(location.SubLocation):

    def __init__(self, m):
        super().__init__(m)
        self.name = "battleground"
        self.verbs['north'] = self
        self.verbs['south'] = self
        self.verbs['east'] = self
        self.verbs['west'] = self

        self.verbs['take'] = self
        self.verbs["investigate"] = self

    def enter(self):
        description = "A large battlefeild lay before you. \nScattered about are the remnents of a great scrimage between what looks like the royal army and a large pirate captains army."
        announce(description)
        announce("At the other end of the body laden plain is a wodden throne on which the corpse of a very regal looking pirate sits.\nPerhaps he is the captain, worth investigating.")

    def process_verb(self, verb, cmd_list, nouns):
        if (verb == "north"):
            announce("You pass the regal captain into the forest, perhaps it is best to let sleeping dogs lie.")
            config.the_player.next_loc = self.main_location.locations["trees"]
        if (verb == "south"):
            announce("Nothing here but water. Your ship is back west.")
        if (verb == "east"):
            announce("On the other edge of the battlefeild is a pile of rubble, probably once a castle.\nIt blocks you from going any further.")
        if (verb == "west"):
            announce("Back the way you came huh? Probably a good idea.")
            config.the_player.next_loc = self.main_location.locations["beach"]
        if (verb == "Investigate"):
            announce("The captain's moldy bones, and rottoin woden chair overlook the carnage between both armies.")
            announce("In the captain's arms is a very old looking book with a cover adorned with jewels and script unknown to you.")