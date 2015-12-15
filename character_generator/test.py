# Created by Jeramy Lochner
# 100% Fan made tools
# No association with Numenera or Monte Cook Games
# Any content in .ini files will be taken down upon official request.

import configparser
import random
from tkinter import *

""" Used to get user input on console
Params:
msg = The message printed before options
restrictions = list of options to pick from
needed = int of how many options need to be picked"""
def get_input(msg, restrictions = [], needed = 1):
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
    move_allowed = []
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
        s += ('You are Tier %d\n' % (self.tier))
        s += ('Might: %d | %d\n' % (self.pools['might'], self.edge['might']))
        s += ('Speed: %d | %d\n' % (self.pools['speed'], self.edge['speed']))
        s += ('Intellect: %d | %d\n' % (self.pools['intellect'], self.edge['intellect']))
        s += ('Skills:\n')
        for skill in self.skills:
            s += ('\t%s\n' % skill)
        s += ('\nMoves:\n')
        for move in self.moves:
            s += ('\t%s\n' % move)
        s += ('\nEquipment:\n')
        for equip in self.equipment:
            s += ('\t%s\n' % equip)
        s += ('\nYou probably look like:\n')
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
            
        default_conf = configparser.ConfigParser()
        default_conf.read('default.ini')
        move_allowed = [int(default_conf['New_moves']['tier'+str(x)]) for x in range(1, 7)]
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

class App:

    def __init__(self, master):
        frame = Frame(master)
        frame.pack()

        self.nameEntry = Entry(frame)
        self.nameEntry.insert(0, "Insert Name Here")
        self.nameEntry.grid(row=0, column=0)

        self.tierScale = Scale(frame, from_=1, to=6, label='Pick Tier')
        self.tierScale.grid(row=0, column=1)

        self.classListbox = Listbox(frame, exportselection=0)
        for cl in self.get_classes():
            self.classListbox.insert(END, cl)
        self.classListbox.select_set(0)
        self.classListbox.bind('<<ListboxSelect>>', self.change_class)
        self.classListbox.grid(row=1,column=0)

        self.classText = StringVar()
        self.classLabel = Label(frame, textvariable=self.classText, wraplength=100)
        self.classLabel.grid(row=1,column=1)

        self.fociListbox = Listbox(frame, exportselection=0)
        for focus in self.get_foci():
            self.fociListbox.insert(END, focus)
        self.fociListbox.select_set(0)
        self.fociListbox.bind('<<ListboxSelect>>', self.change_focus)
        self.fociListbox.grid(row=2,column=0)

        self.fociText = StringVar()
        self.fociLabel = Label(frame, textvariable=self.fociText, wraplength=100)
        self.fociLabel.grid(row=2,column=1)

        self.descriptorListbox = Listbox(frame, exportselection=0)
        for descriptor in self.get_descriptors():
            self.descriptorListbox.insert(END, descriptor)
        self.descriptorListbox.select_set(0)
        self.descriptorListbox.bind('<<ListboxSelect>>', self.change_descriptor)
        self.descriptorListbox.grid(row=3,column=0)

        self.descriptorText = StringVar()
        self.descriptorLabel = Label(frame, textvariable=self.descriptorText, wraplength=100)
        self.descriptorLabel.grid(row=3,column=1)

        self.doneButton = Button(frame, text="Done", command=self.basic_setup, width=100)
        self.doneButton.grid(row=4,column=0,columnspan=5)

        self.moveListbox = Listbox(frame, exportselection=0)
        for move in self.get_moves():
            self.moveListbox.insert(END, move)
        self.moveListbox.select_set(0)
        self.moveListbox.bind('<<ListboxSelect>>', self.change_move)
        self.moveListbox.grid(row=1, column=2)

        self.moveText = StringVar()
        self.moveText = Label(frame, textvariable=self.moveText, wraplength=100)
        self.moveLabel.grid(row=1, column=3)

    def get_foci(self):
        focus_conf = configparser.ConfigParser()
        focus_conf.read('foci.ini', encoding='utf-8')
        foci = focus_conf.sections()
        return foci

    def change_focus(self, picked):
        listbox = picked.widget
        focus_conf = configparser.ConfigParser()
        focus_conf.read('foci.ini', encoding='utf-8')
        focus = focus_conf[listbox.get(ACTIVE)]['description']
        self.fociText.set(focus)

    def get_descriptors(self):
        descriptor_conf = configparser.ConfigParser()
        descriptor_conf.read('descriptors.ini', encoding='utf-8')
        descriptors = descriptor_conf.sections()
        return descriptors

    def change_descriptor(self, picked):
        listbox = picked.widget
        descriptor_conf = configparser.ConfigParser()
        descriptor_conf.read('descriptors.ini', encoding='utf-8')
        descriptor = descriptor_conf[listbox.get(ACTIVE)]['description']
        self.descriptorText.set(descriptor)

    def get_classes(self):
        default_conf = configparser.ConfigParser()
        default_conf.read('default.ini')
        classes = list(dict(default_conf['Descriptions']).keys())
        return classes
    
    def change_class(self, picked):
        listbox = picked.widget
        default_conf = configparser.ConfigParser()
        default_conf.read('default.ini')
        clas = default_conf['Descriptions'][listbox.get(ACTIVE)]
        self.classText.set(clas)

    def get_moves(self):
        #TODO
        return []
    def change_move(self, picked):
        #TODO
        listbox = picked.widget
        
    def basic_setup(self):
        name = self.nameEntry.get()
        clas = self.classListbox.get(ACTIVE)
        descriptor = self.descriptorListbox.get(ACTIVE)
        focus = self.fociListbox.get(ACTIVE)
        tier = self.tierScale.get()
        for x in [name, clas, descriptor, focus, tier]:
            if not x:
                print("You haven't selected everything you need to")
        char = Character(name, clas, tier)
        
        focus_conf = configparser.ConfigParser()
        focus_conf.read('foci.ini', encoding='utf-8')
        char.set_focus(focus, focus_conf)

        descriptor_conf = configparser.ConfigParser()
        descriptor_conf.read('descriptors.ini', encoding='utf-8')
        char.set_descriptor(descriptor, descriptor_conf)
        print(char)
        
# Simple commandline version
if  __name__ == '__main__':
    root = Tk()

    app = App(root)
    root.mainloop()
else:
    # Picking moves
    for tier in range(1, char.tier+1):
        char.pick_moves(tier)

    print(char)
