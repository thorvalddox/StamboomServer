__author__ = 'Thorvald'

import time
import sys, os, re
import random
import os.path

from itertools import chain
from collections import namedtuple

import xml.etree.ElementTree as ET

# commands should look like this: user person person_name 01/01/1900 01/01/2000
#                               user family parent_1 parent_2 child_1 child_2
#                               user delete person_name
#                               user parents child parent_1 parent_2
#                               user merge person_1 person_2

Representation = namedtuple("Representation", "head,tail")


class FamilyTree:
    def __init__(self):
        self.families = []
        self.people = []
        self.subHeads = []
        self.head = None

    @property
    def people_linked(self):
        """
        returns a list of people the family tree contains and are connected
        """
        for f in self.families:
            for p in f.parents + f.children:
                yield p

    @property
    def people_all(self):
        """
        returns a list of people the family tree contains, iven the not yet connected ones
        """
        return sorted(self.people, key=lambda x: x.name.split(" ")[1:] + [x.name.split(" ")[0]])

    def get_person(self, name):
        """
        returns a person woth the given name. If there isn't one, it creates a new one and retusn that one
        """
        if isinstance(name,Person):
            return name
        elif not isinstance(name, str):
            raise Exception("{} is not a string".format(name))
        try:
            return [p for p in self.people if name in (p.name, p.uname)][0]
        except IndexError:
            # #print("did not find {}, creating new person".format(name))
            p = Person(name)
            self.people.append(p)
            return p

    def get_family(self, *names):
        """
        returns a family with the given parent names. Makes a new one if not found.
        """
        people = [self.get_person(name) for name in names if name not in ("","*")]
        try:
            return [f for f in self.families if set(f.parents) == set(people)][0]
        except IndexError:
            f = Family(people, [])
            # #print(f)
            self.families.append(f)
            return f

    def get_family_down(self, person):
        """
        returns a iterator of families where the given person is a parent of
        """
        for f in self.families:
            # #print(str(f))
            if person in f.parents:
                yield f

    def get_family_up(self, person):
        """
        returns a the family the person is a child of
        """
        for f in self.families:
            # #print(str(f))
            if person in f.children:
                return f

    def get_representation(self, person):
        """
            Object to represent a part of the family tree.
            head represents the people on the same line indicated by the given person,
            they include the person himself and all the partners he ever had
            tail represents the people on the next line. These contain the children.
            This one is usually chained, as to give the correct representation, they need the head entry of each child
        """
        if person is None:
            #print("Invalid representation")
            return (Representation([], []))
        famlist = list(self.get_family_down(person))
        if len(famlist) == 0:
            # #print(person.name, "never married")
            return Representation([person], [])
        elif len(famlist) == 1:
            # #print(person.name, "married ones")
            fam, = famlist
            return Representation(filter_invalid([person, self.get_parther(person, fam)]), fam.children)
        elif len(famlist) == 2:
            # #print(person.name, "married twice")
            fam1, fam2 = sorted(famlist,key=lambda f:self.get_parther(person,f).ubirth
                                if self.get_parther(person,f) is not None else time.localtime())
            return Representation(
                filter_invalid([self.get_parther(person, fam1), person, self.get_parther(person, fam2)]),
                fam1.children + fam2.children)
        else:
            return Representation([person], [])

    def from_xml(self, filename):
        """
        Build the family tree given an old-format xml file
        """
        # #print(os.getcwd())
        root = ET.parse(filename).getroot()
        for node in root:
            if node.tag == "persoon":
                p = Person(node.attrib["naam"], id_=node.attrib["id"])
                for i in node:
                    if i.tag == "head":
                        self.head = p
                    elif i.tag == "geb":
                        p.birth = i.text
                    elif i.tag == "stf":
                        p.dead = i.text
            elif node.tag == "familie":
                parents = []
                children = []
                div = False
                for i in node:
                    if i.tag in ("ouder", "kind"):
                        try:
                            p = Person.all_[i.text]
                        except KeyError:
                            p = Person("ERROR", id_=i.text)
                        if i.tag == "ouder":
                            parents.append(p)
                        else:
                            children.append(p)
                    elif i.tag == "divorsed":
                        div = True
                self.families.append(Family(parents, children, div))

    def from_code(self, filename, level=0):
        """
        generates family tree from a code object
        0 is admin
        1 is logged in users
        2 is all
        """
        c = CommandLoader(self, list("$#?"[:level + 1]))
        with open("StamboomServer/"+filename) as fff:
            for i in Commands.from_raw(fff.read()):
                c(i)

    def write(self, person):
        """
        returns a string representing the posterity of the given person
        """
        top, bottom = self.get_representation(person)
        return "{} {{ {} }}".format("+".join(t.name for t in top), ",".join(self.write(p) for p in bottom))

    def __str__(self):
        return self.write(self.head)

    def get_parther(self, person, family):
        """
        give the partner of the person in the given family. If you want all pertners the person even had,
        use: get_partners(person)
        """
        for p in family.parents:
            if p != person:
                return p

    def build_commands(self):
        """
        Build a list of commands that could rebuild this whole family tree
        """
        for p in self.people_linked:
            yield "$convbot", "person", p.uname, p.birth, p.dead
            if self.head == p:
                yield "$convbot", "head", p.uname
        for f in self.families:
            p1, p2, *_ = [p.uname for p in f.parents] + [""] * 2
            clist = [c.uname for c in f.children]
            yield ("$convbot", "family", p1, p2) + tuple(clist)
            if f.divorced:
                yield ("$convbot", "divorce", p1, p2)

    def get_parents(self, person):
        """
        returns all persons parents
        """
        for f in self.families:
            if person in f.children:
                for p in f.parents:
                    yield p

    def get_children(self, person):
        """
        returns all persons children
        """
        ret = []
        for f in self.families:
            if person in f.parents:
                for p in f.children:
                    ret.append(p)
        return sorted(ret, key=lambda x: x.ubirth)

    def get_siblings(self, person):
        """
        returns all persons siblings and half-siblings
        """
        for p in self.get_parents(person):
            for c in self.get_children(p):
                if c != person:
                    yield c

    def get_partners(self, person):
        """
        returns all persons partners
        """
        for f in self.families:
            if person in f.parents:
                for p in f.parents:
                    if p != person:
                        yield p

    def get_data(self, person):
        """
        returns all data to use in edit.html
        """
        yield self.get_parents(person)
        yield self.get_partners(person)
        yield self.get_children(person)
        yield list(set(self.get_siblings(person)))

    def get_clan(self, person):
        """
        returns all posterity and there partners
        """
        for p in self.get_representation(person).head:
            yield p
        for p in self.get_representation(person).tail:
            for i in self.get_clan(p):
                yield i

    def get_ancestors(self, person):
        yield person
        for p in self.get_parents(person):
            for i in self.get_ancestors(p):
                yield i

    def build_new(self, key):
        """
        returns new famaily tree representing a certain root of the family.
        Gives the posterity and the single direction ancestors
        """
        #print("1")
        new = FamilyTree()
        families = []
        for p in self.get_clan(key):
            new.people.append(p)
        for p in self.get_ancestors(key):
            new.people.append(p)
        for p in new.people:
            #print(p)
            for f in self.get_family_down(p):
                #print(f)
                if all(p in new.people for p in f.parents) and f not in families:
                    families.append(f)
        #print(new.people)
        new.families = [Family(f.parents, [c for c in f.children if c in new.people]) for f in families]
        # for f in families:
        #     for p in f.children:
        #         if p not in new.people:
        #             new.people.append(p)
        if self.head in new.people:
            new.head = self.head
        else:
            new.head = key
        return new


def filter_invalid(l):
    """
    Filters the None objects out of a list
    """
    return ([x for x in l if x is not None])


def builddate(date):
    """
    Builds a datetime object out of a string
    """
    if date and date != "never":
        date = re.sub(r"[ */-]+", "/", date)
        return time.strptime(date, "%d/%m/%Y")
    else:
        return time.strptime("01/01/3000", "%d/%m/%Y")


def showdate(date):
    """
    Builds a string out of a datetime object
    """
    if date == time.strptime("01/01/3000", "%d/%m/%Y"):
        return ""
    else:
        return time.strftime("%d/%m/%Y", date)


class Person:
    all_ = {}  # used to get people_linked not in the family tree. Only works for id's people_linked in diffrenet trees can have te same name, but not the same id

    def __init__(self, name, birth="", dead="", id_="none"):
        self.name = name
        self.birth = birth
        self.dead = dead
        self.id_ = id_ if id_ != "none" else hex(random.randrange(16 ** 32))
        Person.all_[self.id_] = self
        # #print(self.name, self.id_)

    @property
    def name(self):
        return self.uname.replace("_", " ")

    @name.setter
    def name(self, value):
        self.uname = value.replace(" ", "_")

    @property
    def birth(self):
        return showdate(self.ubirth)

    @birth.setter
    def birth(self, value):
        self.ubirth = builddate(value)

    @property
    def dead(self):
        return showdate(self.udead)

    @dead.setter
    def dead(self, value):
        self.udead = builddate(value)

    @property
    def image(self):
        """
        returns the path to the image
        """
        name = "kopkes/" + self.uname + ".jpg"
        if not os.path.exists("StamboomServer/static/" + name):
            name = "kopkes/smiley.jpg"
        return name

    def __str__(self):
        return self.uname

    def __repr__(self):
        return "Person({})".format(self.uname)


class Family:
    def __init__(self, parents, children, divorced=False):
        self.parents = parents
        self.children = children
        self.divorced = divorced

    def __str__(self):
        return "+".join(str(i) for i in self.parents) + "->" + ",".join(str(i) for i in self.children)


class Commands(list):
    """
    This object is a list of tuples of strings. The tuples represent single commands,
    the first element is the user, the second the functions and the rest are the arguments.
    """
    def to_raw(self):
        """
        changes a list of command object to a raw string of commands
        """
        ret = ""
        for c in self:
            args = " ".join(i if i != "" else "*" for i in c)
            ret += args + "\n"
        return ret

    def to_html(self):
        """
        changes a list of command object to a html display, used to show the console on the website
        """
        ret = ""
        for c in self:
            user, func, *args = c
            args = [i if i != "" else "*" for i in args]
            usercolor = {"$": "gold", "#": "olive", "?": "darkgrey"}[user[0]]
            funccolor = {"person": "blue", "family": "green", "delete": "darkcyan", "merge": "purple",
                         "parents": "darkgreen","disconnect":"darkred",
                         "head": "darkblue", "divorce": "darkorange"}.get(func, "orange")
            argscolor = []
            for i in args:
                if i == "ERROR":
                    argscolor.append("red")
                elif re.match(r"[0-9][0-9].[0-9][0-9].[0-9][0-9][0-9][0-9]", i):
                    argscolor.append("darkcyan")
                else:
                    argscolor.append("black")
            ret += """<span style="color:{1}">{0:<15}</span> <span style="color:{3}">{2:<15}</span> {4}</br>""" \
                .format(user, usercolor, func, funccolor,
                        " ".join('<span style="color:{1}">{0:<15}</span>'.format(*a) for a in zip(args, argscolor)))

        return ret

    @classmethod
    def from_raw(cls, data):
        """


        changes a string of commands to a list of command objects
        """
        ret = []
        for line in data.split("\n"):
            if line.count(" ") < 2:
                continue
            ret.append(tuple(i if i != "*" else "" for i in line.split(" ")))
        return cls(ret)


class CommandLoader:
    """
    An object that can execute commands.
    Its member functions match the names of the different commands, and are the
    functions that are actually called when executing the command.
    """
    def __init__(self, tree, accepted=[]):
        self.tree = tree
        self.accepted = accepted + ["$"]

    def __call__(self, command):
        # #print(command)
        user, func, *args = command
        args = list(args) + [""] * 4  # missing last arguments
        if any(user.startswith(pref) for pref in self.accepted):
            getattr(self, func)(*args)

    def person(self, name, birth, dead, *_):
        # #print("making",name)
        p = self.tree.get_person(name)
        p.birth = birth
        p.dead = dead

    def family(self, p1, p2, *children):
        # #print("making family")
        parentlist = [p for p in (p1, p2) if p != ""]
        f = self.tree.get_family(*parentlist)
        f.children.extend(self.tree.get_person(p) for p in children if p != "" and p not in f.children)

    def delete(self, person, *_):
        person = self.tree.get_person(person)
        for f in self.tree.families:
            if person in f.parents:
                #print("delete downlink")
                f.parents.remove(person)
            if person in f.children:
                #print("delete uplink")
                f.children.remove(person)
        self.tree.people.remove(person)
        del person

    def merge(self, person1, person2, *_):
        for f in self.tree.families:
            if person2 in f.parents:
                f.parents.remove(person2)
                f.parents.append(person1)
            if person2 in f.children:
                f.children.remove(person2)
                f.children.append(person1)

    def disband(self, person1, person2, *_):
        f = self.tree.get_family(person1, person2)
        self.tree.families.remove(f)
        del f

    def disconnect(self, person1, person2, child, *_):
        f = self.tree.get_family(person1, person2)
        f.children = [c for c in f.children if child not in (c.name,c.uname)]

    def parents(self, child, p1, p2, *_):
        child=self.tree.get_person(child)
        for f in self.tree.families:
            if child in f.children:
                f.children.remove(child)
        self.family(p1, p2, child.uname)

    def divorce(self, p1, p2, *_):
        parentlist = [p for p in (p1, p2) if p != ""]
        f = self.tree.get_family(*parentlist)
        f.divorced = True

    def remarry(self, p1, p2, *_):
        parentlist = [p for p in (p1, p2) if p != ""]
        f = self.tree.get_family(*parentlist)
        f.divorced = False

    def head(self, p, *_):
        self.tree.head = self.tree.get_person(p)

    def subhead(self, p, *_):
        self.tree.subhead.append(self.tree.get_person(p))

    def sibling(self, old, new):
        for f in self.tree.families:
            if new in f.children:
                f.children.remove(new)
        f = self.tree.get_family_up(old)
        f.children.append(new)

    def loginas(self, name, *_):
        """not actually a command, but is added to the log to track the author of different commands"""
        pass

    def logout(self,  *_):
        """not actually a command, but is added to the log to track the author of different commands"""
        pass

def addcommand_ip(request, data):
    """
    adds a command to the command log for a user that is not logged in.
    """
    with open("StamboomServer/data.log", "a") as fff:
        fff.write("?{} {}\n".format(request.environ['REMOTE_ADDR'], data))


def addcommand_user(session, data):
    """
    adds a command to the command log for a user who is logged in
    """
    with open("StamboomServer/data.log", "a") as fff:
        fff.write("#{} {}\n".format(session["username"], data))


def addcommand(request, session, data):
    """
    adds a command to the command log
    """
    if "username" in session:
        addcommand_user(session, data)
    else:
        addcommand_ip(request, data)


def xmlTest():
    f = FamilyTree()
    f.from_xml("alles.xml")
    return Commands(f.build_commands()).to_html()


def bashTest():
    f = FamilyTree()
    f.from_code("data.log")
    return Commands(f.build_commands()).to_html()


def rawCode():
    with open("StamboomServer/data.log") as fff:
        return Commands.from_raw(fff.read()).to_html()


def main():
    f = FamilyTree()
    f.from_xml("dox.xml")
    with open("StamboomServer/autodata.log", "w") as fff:
        fff.write(Commands(f.build_commands()).to_raw())


if __name__ == "__main__":
    main()
