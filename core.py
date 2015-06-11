__author__ = 'Thorvald'

import time
import sys,os,re
import random


import xml.etree.ElementTree as ET

# comment should look like this: user person person_name 01/01/1900 01/01/2000
#                               user family parent_1 parent_2 child_1 child_2
#                               user delete person_name
#                               user parents child parent_1 parent_2
#                               user merge person_1 person_2

class FamilyTree:
    def __init__(self):
        self.families = []
        self.head = None

    @property
    def people(self):
        for f in self.families:
            for p in f.parents + f.children:
                yield p

    def get_person(self, name):
        if not isinstance(name,str):
            Exception("{} is not a string".format(name))
        try:
            return [p for p in self.people if p.name == name][0]
        except IndexError:
            #print("did not find {}, looking in unconnected people".format(name))
            try:
                return [p for p in Person.all_.values() if p.uname == name or p.name == name][0]
            except IndexError:
                    #print("did not find {}, creating new person".format(name))
                    return Person(name)

    def get_family(self, *names):
        people = [self.get_person(name) for name in names]
        try:
            return [f for f in self.families if set(f.parents) == set(people)][0]
        except IndexError:
            f = Family(people, [])
            #print(f)
            self.families.append(f)
            return f

    def get_family_down(self, person):
        for f in self.families:
            #print(str(f))
            if person in f.parents:
                yield f

    def get_representation(self, person):
        famlist = list(self.get_family_down(person))
        if len(famlist) == 0:
            #print(person.name, "never married")
            return ([person], [])
        elif len(famlist) == 1:
            #print(person.name, "married ones")
            fam, = famlist
            return (filter_invalid([person, self.get_parther(person, fam)]), fam.children)
        elif len(famlist) == 2:
            #print(person.name, "married twice")
            fam2, fam1 = famlist
            return (
                filter_invalid([self.get_parther(person, fam1), person, self.get_parther(person, fam2)]),
                fam1.children + fam2.children)

    def from_xml(self, filename):
        #print(os.getcwd())
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
    def from_code(self,filename):
        c = CommandLoader(self)
        with open(filename) as fff:
            for i in Commands.from_raw(fff.read()):
                c(i)

    def write(self, person):
        top, bottom = self.get_representation(person)
        return "{} {{ {} }}".format("+".join(t.name for t in top), ",".join(self.write(p) for p in bottom))

    def __str__(self):
        return self.write(self.head)

    def get_parther(self, person, family):
        for p in family.parents:
            if p != person:
                return p

    def get_children(self, person):
        for f in self.get_family_down(person):
            for p in f.children:
                yield p

    def build_commands(self):
        for p in self.people:
            yield "$convbot","person",p.uname,p.birth,p.dead
            if self.head == p:
                yield "$convbot","head",p.uname
        for f in self.families:
            p1,p2,*_ = [p.uname for p in f.parents] + [""]*2
            clist = [c.uname for c in f.children]
            yield ("$convbot","family",p1,p2) + tuple(clist)
            if f.divorced:
                yield ("$convbot","divorce",p1,p2)


def filter_invalid(l):
    return ([x for x in l if x is not None])


def builddate(date):
    if date and date != "never":
        date = re.sub(r"[ */-]+","/",date)
        return time.strptime(date, "%d/%m/%Y")
    else:
        return time.strptime("01/01/3000", "%d/%m/%Y")


def showdate(date):
    if date == time.strptime("01/01/3000", "%d/%m/%Y"):
        return ""
    else:
        return time.strftime("%d/%m/%Y", date)


class Person:
    all_ = {}  # used to get people not in the family tree. Only works for id's people in diffrenet trees can have te same name, but not the same id

    def __init__(self, name, birth="", dead="", id_="none"):
        self.name = name
        self.birth = birth
        self.dead = dead
        self.id_ = id_ if id_ != "none" else hex(random.randrange(16**32))
        Person.all_[self.id_] = self
        #print(self.name, self.id_)

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
    def to_raw(self):
        ret = ""
        for c in self:
            args = " ".join(i if i != "" else "*" for i in c)
            ret += args+"\n"
        return ret

    def to_html(self):
        ret = ""
        for c in self:
            user,func,*args = c
            args = [i if i != "" else "*" for i in args]
            usercolor = {"$":"olive","#":"gold","?":"darkgrey"}[user[0]]
            funccolor = {"person":"blue","family":"green","delete":"orange","merge":"purple","parents":"darkgreen"}[func]
            argscolor = []
            for i in args:
                if i == "ERROR":
                    argscolor.append("red")
                elif re.match(r"[0-9][0-9].[0-9][0-9].[0-9][0-9][0-9][0-9]",i):
                    argscolor.append("darkcyan")
                else:
                    argscolor.append("black")
            ret += """<span style="color:{1}">{0}</span> <span style="color:{3}">{2}</span> {4}</br>""" \
                .format(user,usercolor,func,funccolor,
                        " ".join('<span style="color:{1}">{0}</span>'.format(*a) for a in zip(args,argscolor)))


        return ret

    @classmethod
    def from_raw(cls,data):
        ret = []
        for line in data.split("\n"):
            if line.count(" ") < 2:
                continue
            ret.append(tuple(i if i != "*" else "" for i in line.split(" ")))
        return cls(ret)


class CommandLoader:
    def __init__(self,tree,accepted=[]):
        self.tree = tree
        self.accepted = accepted
    def __call__(self,command):
        #print(command)
        user,func,*args = command
        args = list(args) + [""]*4 #missing last arguments
        if user in self.accepted or user[0] == "$":
            getattr(self,func)(*args)
    def person(self,name,birth,dead,*_):
        #print("making",name)
        p = self.tree.get_person(name)
        p.birth = birth
        p.dead = dead
    def family(self,p1,p2,*children):
        #print("making family")
        parentlist = [p for p in (p1,p2) if p != ""]
        f = self.tree.get_family(*parentlist)
        f.children.extend(self.tree.get_person(p) for p in children if p != "")
    def delete(self,person):
        for f in self.tree.families:
            if person in f.parents:
                f.parents.remove(person)
            if person in f.children:
                f.children.remove(person)
    def merge(self,person1,person2):
        for f in self.tree.families:
            if person2 in f.parents:
                f.parents.remove(person2)
                f.parents.append(person1)
            if person2 in f.children:
                f.children.remove(person2)
                f.children.append(person1)
    def parents(self,child,p1,p2):
        self.family(p1,p2,child)
    def divorce(self,p1,p2):
        parentlist = [p for p in (p1,p2) if p != ""]
        f = self.tree.get_family(*parentlist)
        f.divorced = True
    def head(self,p,*_):
        self.tree.head = self.tree.get_person(p)


def xmlTest():
    f = FamilyTree()
    f.from_xml("dox.xml")
    return Commands(f.build_commands()).to_html()

def bashTest():
    f = FamilyTree()
    f.from_code("data.log")
    return Commands(f.build_commands()).to_html()

def rawCode():
    with open("data.log") as fff:
        return Commands.from_raw(fff.read()).to_html()

def main():
    f = FamilyTree()
    f.from_xml("dox.xml")
    with open("autodata.log","w") as fff:
        fff.write(Commands(f.build_commands()).to_raw())


if __name__ == "__main__":
    main()
