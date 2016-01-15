# Created by Jeramy Lochner
# 100% Fan made tools
# No association with Numenera or Monte Cook Games
# Any content in .ini files will be taken down upon official request.

import configparser
import random


def get_input(msg, restrictions = [], needed = 1):
    """
    :param msg: 'input()' message
    :param restrictions: answers to choose from
    :param needed: how many answers
    :return:
    """
    var = []
    print(msg)
    if restrictions == [] or restrictions == ['']:
        return input('> ')
    for i, r in enumerate(restrictions):
        print('('+str(i+1)+') '+r)
    while len(var) < needed:
        i = None
        while i not in restrictions:
            i = input('> ')
            if i.isdigit():
                try:
                    i = restrictions[int(i)-1]
                except IndexError:
                    print("That number is not an option")
            else:
                if i == 'random' and 'random' not in restrictions:
                    i = random.choice(restrictions)
                else:
                    i = i.strip('\n')
            if i in var:
                print("You've already selected that option before")
                i = None
            else:
                var.append(i)
    if len(var) == 1:
        return var[0]
    return var

class Character:
    # General Variables
    name = ''
    clas = ''
    descriptor = ''
    focus = ''
    connection = ''
    tier = 1

    # Stats
    pool = 0
    effort = 0
    pools = {}
    edge = {}

    # Moveset
    skills = []
    moves = []
    possible = []

    # Recommendations
    appearance = []

    # Inventory
    shins = 0
    cypher_count = 0
    oddity_count = 0
    equipment = []
    oddities = []
    cyphers = []

    def __init__(self, name, clas, tier):
        self.name = name
        self.clas = clas
        self.tier = int(tier)
        self.get_default(clas)

    """ Print out a basic report of the character """
    def __str__(self):
        s = ""
        s += ('You are %s, the %s %s who %s\n' % (self.name, self.descriptor, self.clas.title(), self.focus))
        s += ('Might: %d | %d\n' % (self.pools['might'], self.edge['might']))
        s += ('Speed: %d | %d\n' % (self.pools['speed'], self.edge['speed']))
        s += ('Intellect: %d | %d\n' % (self.pools['intellect'], self.edge['intellect']))
        s += ('Skills:\n')
        for skill in self.skills:
            s += ('\t%s\n' % skill)
        s += ('Moves:\n')
        for move in self.moves:
            s += ('\t%s\n' % move)
        s += ('Equipment:\n')
        for equip in self.equipment:
            s += ('\t%s\n' % equip)
        s += ('You probably look like:\n')
        for appear in self.appearance:
            s += ('\t%s\n' % appear)
        return s

    """ Get the default values for many of the variables
    based on which class was chosen """
    def get_default(self, clas):
        class_conf = configparser.ConfigParser()
        class_conf.read(clas+'.ini')
        self.pool = int(class_conf['default']['Pool'])
        self.effort = int(class_conf['default']['Effort'])
        self.cypher_count = int(class_conf['default']['Cyphers'])
        self.oddity_count = int(class_conf['default']['Oddities'])
        self.shins = int(class_conf['default']['Shins'])
        self.pools = dict(class_conf['default_pools'])
        for key in self.pools:
            self.pools[key] = int(self.pools[key])
        self.edge = dict(class_conf['default_edge'])
        for key in self.edge:
            self.edge[key] = int(self.edge[key])
        def_move = dict(class_conf['default_moves'])
        for key,move in def_move.items():
            self.moves.append(str(key).title() + ' - ' +str(move))
        if 'default_skills' in class_conf.sections():
            self.skills.append(get_input("Pick a skill. (If no options, type anything)", class_conf['default_skills']['Skills'].split(',')))
        self.get_possible_moves(self.clas, self.tier)

    """ Change might, intellect, or speed by a certain value (usually 1) """
    def change_pools(self, p, value):
        self.pools[p.lower()] += value

    """ Set the focus, and add any values that pertain to that focus """
    def set_focus(self, focus, focus_conf):
        self.focus = focus
        self.connection = focus_conf[focus]['connection']
        self.appearance.append(focus_conf[focus]['appearance'])
        self.equipment.append(focus_conf[focus]['add_equip'])
        for t in range(1, int(self.tier)+1):
            for move in focus_conf[focus]['tier'+str(t)].split('$'):
                self.moves.append(move)

    """ Set the character descriptor and add any values that pertain to
    that descriptor """
    def set_descriptor(self, descriptor, descriptor_conf):
        self.descriptor = descriptor
        keys = list(descriptor_conf[descriptor].keys())
        for skill in descriptor_conf[descriptor]['skills'].split('$'):
            self.skills.append(skill)
        for pool in self.pools.keys():
            if pool in keys:
                self.pools[pool] += int(descriptor_conf[descriptor][pool])
        if 'shin' in keys:
            self.shins += int(descriptor_conf[descriptor]['shin'])
        if 'add_equip' in keys:
            for equip in descriptor_conf[descriptor]['add_equip'].split('$'):
                self.equipment.append(equip)
        if 'moves' in keys:
            for move in descriptor_conf[descriptor]['moves'].split('$'):
                self.moves.append(move)

    """ Get all the possible moves from 1 to tier for a given class
    Returned in the format = [[Move, Description, tier], [...]] """
    def get_possible_moves(self, clas, tier):
        class_conf = configparser.ConfigParser()
        class_conf.read(clas+'.ini')
        for x in range(1, int(tier)+1):
            for key,item in dict(class_conf['Tier'+str(x)+'_moves']).items():
                self.possible.append([key.title(), item, int(x)])

    """ Pick moves based on user input given the possibilties based on
    the tier and previously picked moves """
    def pick_moves(self, tier):
        p = []
        for move in self.possible:
            x = (move[0].title() + ' | ' + move[1])
            if move[2] <= int(tier) and x not in self.moves:
                p.append(x)
        needed = move_allowed[int(tier)-1]
        m = "What move will you select for tier " + str(tier) + " (Pick " + str(needed) + ")"
        selected = get_input(m, p, needed)
        if type(selected) == str:
            self.moves.append(selected)
        else:
            for move in selected:
                self.moves.append(move)

# Simple commandline version
if __name__ == '__main__':
    default_conf = configparser.ConfigParser()
    default_conf.read('default.ini')
    classes = list(dict(default_conf['Descriptions']).keys())
    move_allowed = [int(default_conf['New_moves']['tier'+str(x)]) for x in range(1, 7)]

    # Basic information         
    name = get_input("What's your name?")
    clas = get_input('What class would you like to play?', restrictions = classes)
    tier = get_input('What tier are you starting at?', restrictions = [str(x) for x in range(1, 7)])
    char = Character(name, clas, tier)

    # Focus
    focus_conf = configparser.ConfigParser()
    focus_conf.read('foci.ini', encoding='utf-8')
    focus = get_input("What focus do you want?", restrictions = focus_conf.sections())
    char.set_focus(focus, focus_conf)

    # Descriptor
    descriptor_conf = configparser.ConfigParser()
    descriptor_conf.read('descriptors.ini', encoding='utf-8')
    descriptor = get_input("What descriptor do you want?", restrictions = descriptor_conf.sections())
    char.set_descriptor(descriptor, descriptor_conf)

    # Picking moves
    for tier in range(1, char.tier+1):
        char.pick_moves(tier)

    print(char)
