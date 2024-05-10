
from game import location
import game.config as config
from game.display import announce
from game.events import *
import game.items as items
import pygame
import game.combat as combat
import random
from game.crewmate import CrewMate as crew

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
        self.locations["grotto"] = food_grotto(self)
        self.locations["tower"] = hermits_tower(self)

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
        if (verb == "south" or verb == "east" or verb == "west"):
            config.the_player.next_loc = self.main_location.locations["beach"]
        if (verb == "north"):
            config.the_player.next_loc = self.main_location.locations["grotto"]
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
        self.concertina = True
        self.book = True

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
        if (verb == "investigate"):
            announce("The captain's moldy bones, and rottoin woden chair overlook the carnage between both armies.")
            announce("In the captain's arms is a very old looking book with a cover adorned with jewels and script unknown to you.")
            announce("Next to the chair is a black and red concertina; on close inspection you feel a chill run down youre spine")
        if (verb == "take"):
            if self.concertina == False and self.book == False:
                announce ("You don't see anything to take.")
            if len(cmd_list) > 1:
                if (cmd_list[1] == "concertina"):
                    announce ("You take the concertina from beside the throne.")
                    config.the_player.add_to_inventory([Concertina()])
                    self.concertina = False
                    pygame.mixer.init()
                    pygame.mixer.music.load("game/Three Concertina Tunes.mp3")
                    pygame.mixer.music.set_volume(0.7)
                    pygame.mixer.music.play()
                elif (cmd_list[1] == "book"):
                    announce ("You take the book from from the moldy captain.")
                    config.the_player.add_to_inventory([Book()])
                    self.book = False
                    announce("The captains bones go limp for a beat, but then his eyes begin to glow and suddenly the captain lunges!\nget ready!")
                    self.Boss_battle()
                    announce(" Great work the haunted captain is defeated.")
                    announce("In the aftermath you notice the pirate throne has been blown to bits,\nand underneath is a large chest full of gold.")
                    announce("You take the chest back to your ship, what a sweet deal!")
                    config.the_player.add_to_inventory([Treasure_Chest()])

    def Boss_battle(self):
        monsters = []
        monsters.append(Boss("Moldy Pirate Captain"))
        monsters.append(combat.Drowned("Pirate Soldier"))
        combat.Combat(monsters).combat()

class food_grotto(location.SubLocation):
    def __init__(self, m):
        super().__init__(m)
        self.name = "grotto"
        self.verbs['north'] = self
        self.verbs['south'] = self
        self.verbs['east'] = self
        self.verbs['west'] = self

        self.verbs['take'] = self
        self.verbs["look"] = self

    def enter(self):
        description = "The trees thin and disperse revealing a large open plantation.\nTrees of various fruits are planted in rows seperated by type."
        announce(description)
        announce("At the other end of the long grove is a tower on a small hill.")

    def process_verb (self, verb, cmd_list, nouns):
        food_left = True
        if (verb == "east" or verb == "west"):
            config.the_player.next_loc = self.main_location.locations["beach"]
        if (verb == "south"):
            config.the_player.next_loc = self.main_location.locations["trees"]
        if (verb == "north"):
            config.the_player.next_loc = self.main_location.locations["tower"]
        
        if verb == "take":
            if food_left != False:
                if (cmd_list[1] == "fruit" or cmd_list[1] == "all"):
                    announce ("You take some fruit from the trees.")
                    config.the_player.ship.give_food(30)
                else:
                    announce("You have taken all the food you could, lets hope the land owner does not notice.")
                food_left = False
        if verb == "look":
            announce("The trees are very neat and trimmed, perhaps the caretaker lives in the tower at the other end.")
            announce("The stone tower overlooks the feild from a grassy hill, its small windows let light inside\nthough you cant see anything from here.")

class hermits_tower(location.SubLocation):
     
    def __init__(self, m):
        super().__init__(m)
        self.name = "grotto"
        self.verbs['north'] = self
        self.verbs['south'] = self
        self.verbs['east'] = self
        self.verbs['west'] = self

        self.verbs['take'] = self
        self.verbs["steal"] = self
        self.verbs["look"] = self
        self.verbs["investigate"] = self
        self.verbs["knock"] = self

    def enter(self):
        description = "Looking up at the stone tower you feel its imposing stature.\nA large wodden door blocks your entrance but the door does have a rather ornamental looking knocker."
        announce(description)
        announce("Despite the towers obvious age it is suprisingly well kept, even including the doormat which reads\n'What're you doing here?'.")

    def process_verb (self, verb, cmd_list, nouns):
        won = True
        if (verb == "east" or verb == "west"):
            config.the_player.next_loc = self.main_location.locations["beach"]
        if (verb == "south"):
            config.the_player.next_loc = self.main_location.locations["grotto"]
        if (verb == "north"):
            announce("Nothing lies beyond the tower, a small cliff leads to the beach.\nPresumably it just wraps back to  the one housing your ship")
        
        #Handle taking items. Demo both "take cutlass" and "take all"
        if verb == "take":
            announce("There is nothing to take, unless you want to steal the doormat.")
        if (verb == "look" or verb == "investigate"):
            announce("It is a rather plain looking tower other than it being somewhat out of place.")
            announce("The only thing of note is the door knocker (Doorbells do not exist yet).")
        if verb == "steal":
            announce("You stole the doormat, congratulations you monster")
            announce("I know you are a pirate and all but did you really need the doormat.")
        if verb == "knock":
            announce("You knock on the door.\nAfter a moment a small window at face height swings open and a rather old looking man peers through, \nhis beard is so ling it almost spills outside of the door.")
            announce("'Oh hello' he says with that high pitched crotchety voice old people have.\n'You folks must be hungry, I have food and CURED MEAT if ya like.'")
            announce("BUT")
            announce("'You must answer my riddles.'")
            announce("It seems to you you have no choice, good luck captain.")
            answer_1 = input("What is your name?: ")
            answer_2 = input("What is your quest?: ")
            answer_3 = input("what is your favorite color?: ")
            announce("Good job that was the first round, two more to go.")
            announce("Each party member has to answer, well three of them at least. \nYou already went so its time for crewmate number one.")
            answer_4 = input("what is your name?:")
            answer_5 = input("what is your favorite color?: ")
            answer_6 = input("Are you sure?: ")
            if answer_6 == "no":
                announce("The floor below the pirats feet springs up sending them flying into the trees below.")
                crew.chosen_target.inflict_damage(10, "falling", combat = True)
            answer_7 = input("What is the capital of Assyria?: ")
            if answer_7 != "assur":
                if answer_7 != "Assur":
                    announce("The floor below the pirats feet springs up sending them flying into the trees below.")
                    crew.chosen_target.inflict_damage(10, "falling", combat = True)
            answer_8 = input("What is your name?: ")
            answer_9 = input("What is your quest?: ")
            answer_10 = input("what is the Airspeed velocity of an unladen swallow?: ")
            if answer_10 != "african or european":
                if answer_10 != "African or European":
                    if answer_10 != "african or european?":
                        if answer_10 != "African or European?":
                            won = False
                            announce("WRONG")
                            announce("The floor below the pirats feet springs up sending them flying into the trees below.")
                            crew.chosen_target.inflict_damage(10, "falling", combat = True)
            if won == True:
                announce("'I don't know' the old hermit says.")
                announce("and right as he finishes speaking the door swings open and the hermit goes flying.\n he is launched so far in the air all you see is a twinkle as he dissapears.")
                announce("There is indeed a ton of food in here just as the hermit claimed, and it seems he won't need it anymore.")
                announce("You obviously take the food.")
                config.the_player.ship.give_food(40)

                


class Concertina(items.Item):
    def __init__(self):
        super().__init__("concertina", 200)

class Book(items.Item):
    def __init__(self):
        super().__init__("book", 200)

class Treasure_Chest(items.Item):
    def __init__(self):
        super().__init__("Treasure chest", 1500)

class Boss(combat.Monster):
    attackPattern = 0
    def __init__ (self, name):
        attacks = {}
        attacks["cut"] = ["cuts",random.randrange(73,75), (7,17)]
        attacks["spit"] = ["spits on",random.randrange(35,51), (5,10)]
        attacks["cannon blast"] = ["cannon blasts",random.randrange(90,95), (10,20)]
        #7 to 19 hp, bite attack, 65 to 85 speed (100 is "normal")
        super().__init__(name, random.randrange(200,250), attacks, 150 + random.randrange(-10,11))

    def pickAction(self):
        attacks = self.getAttacks()
        if self.attackPattern == 0:
            self.attackPattern = (self.attackPattern + 1)%4
            return (attacks[0])
        elif self.attackPattern == 1:
            self.attackPattern = (self.attackPattern + 1)%4
            return (attacks[0])
        elif self.attackPattern == 2:
            self.attackPattern = (self.attackPattern + 1)%4
            return (attacks[2])
        elif self.attackPattern == 3:
            self.attackPattern = (self.attackPattern + 1)%4
            return (attacks[1])
        

    def pickTargets(self, action, attacker, allies, enemies):
        if action.name == "cannon blast":
            return enemies
        else:
            return [random.choice(enemies)]


